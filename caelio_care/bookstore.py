"""
Bookstore management system
Handles bookstore registration and book purchase links
"""

from typing import Optional, List, Dict
from pydantic import BaseModel, EmailStr
from datetime import datetime
import math


class BookstoreCreate(BaseModel):
    """Schema for creating a new bookstore"""
    name: str
    email: EmailStr
    phone: str
    address: str
    latitude: float  # GPS coordinates
    longitude: float
    commission_rate: float  # Percentage (0-100)
    description: Optional[str] = None
    website: Optional[str] = None


class Bookstore(BaseModel):
    """Schema for bookstore"""
    id: int
    name: str
    email: str
    phone: str
    address: str
    latitude: float
    longitude: float
    commission_rate: float
    description: Optional[str] = None
    website: Optional[str] = None
    is_active: bool
    created_at: datetime


class BookLinkCreate(BaseModel):
    """Schema for adding book purchase link"""
    book_id: int  # product_id từ CSV (74021317, 184466860, etc.)
    bookstore_id: int
    purchase_url: str
    price: Optional[float] = None
    stock_status: Optional[str] = "available"  # available, out_of_stock, pre_order


class BookLink(BaseModel):
    """Schema for book purchase link"""
    id: int
    book_id: int
    bookstore_id: int
    purchase_url: str
    price: Optional[float] = None
    stock_status: str
    created_at: datetime


class BookstoreManager:
    """Manager for bookstore operations"""
    
    def __init__(self, db_pool):
        self.db_pool = db_pool
    
    async def create_bookstore(self, bookstore_data: BookstoreCreate) -> Bookstore:
        """Create a new bookstore"""
        async with self.db_pool.acquire() as conn:
            # Check if email already exists
            existing = await conn.fetchrow(
                'SELECT id FROM bookstores WHERE email = $1',
                bookstore_data.email
            )
            if existing:
                raise ValueError("Email already registered")
            
            # Insert new bookstore
            row = await conn.fetchrow('''
                INSERT INTO bookstores (
                    name, email, phone, address, latitude, longitude,
                    commission_rate, description, website
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                RETURNING id, name, email, phone, address, latitude, longitude,
                          commission_rate, description, website, is_active, created_at
            ''',
                bookstore_data.name,
                bookstore_data.email,
                bookstore_data.phone,
                bookstore_data.address,
                bookstore_data.latitude,
                bookstore_data.longitude,
                bookstore_data.commission_rate,
                bookstore_data.description,
                bookstore_data.website
            )
            
            return Bookstore(**dict(row))
    
    async def get_bookstore_by_id(self, bookstore_id: int) -> Optional[Bookstore]:
        """Get bookstore by ID"""
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                'SELECT * FROM bookstores WHERE id = $1',
                bookstore_id
            )
            if row:
                return Bookstore(**dict(row))
            return None
    
    async def get_all_bookstores(self, active_only: bool = True) -> List[Bookstore]:
        """Get all bookstores"""
        async with self.db_pool.acquire() as conn:
            if active_only:
                rows = await conn.fetch(
                    'SELECT * FROM bookstores WHERE is_active = true ORDER BY name'
                )
            else:
                rows = await conn.fetch('SELECT * FROM bookstores ORDER BY name')
            
            return [Bookstore(**dict(row)) for row in rows]
    
    async def update_bookstore(
        self,
        bookstore_id: int,
        update_data: Dict
    ) -> Optional[Bookstore]:
        """Update bookstore information"""
        async with self.db_pool.acquire() as conn:
            # Build update query dynamically
            set_clauses = []
            values = []
            param_index = 1
            
            for key, value in update_data.items():
                if key not in ['id', 'created_at', 'email']:  # Don't update these fields
                    set_clauses.append(f"{key} = ${param_index}")
                    values.append(value)
                    param_index += 1
            
            if not set_clauses:
                return await self.get_bookstore_by_id(bookstore_id)
            
            values.append(bookstore_id)
            query = f'''
                UPDATE bookstores
                SET {', '.join(set_clauses)}
                WHERE id = ${param_index}
                RETURNING *
            '''
            
            row = await conn.fetchrow(query, *values)
            if row:
                return Bookstore(**dict(row))
            return None
    
    async def add_book_link(self, link_data: BookLinkCreate) -> BookLink:
        """Add a purchase link for a book"""
        async with self.db_pool.acquire() as conn:
            # Verify book exists
            book_exists = await conn.fetchval(
                'SELECT EXISTS(SELECT 1 FROM books WHERE product_id = $1)',
                link_data.book_id
            )
            if not book_exists:
                raise ValueError(f"Book with product_id {link_data.book_id} not found in database")
            
            # Check if link already exists
            existing = await conn.fetchrow('''
                SELECT id FROM book_links
                WHERE book_id = $1 AND bookstore_id = $2
            ''', link_data.book_id, link_data.bookstore_id)
            
            if existing:
                # Update existing link
                row = await conn.fetchrow('''
                    UPDATE book_links
                    SET purchase_url = $1, price = $2, stock_status = $3, updated_at = CURRENT_TIMESTAMP
                    WHERE book_id = $4 AND bookstore_id = $5
                    RETURNING *
                ''',
                    link_data.purchase_url,
                    link_data.price,
                    link_data.stock_status,
                    link_data.book_id,
                    link_data.bookstore_id
                )
            else:
                # Insert new link
                row = await conn.fetchrow('''
                    INSERT INTO book_links (
                        book_id, bookstore_id, purchase_url, price, stock_status
                    )
                    VALUES ($1, $2, $3, $4, $5)
                    RETURNING *
                ''',
                    link_data.book_id,
                    link_data.bookstore_id,
                    link_data.purchase_url,
                    link_data.price,
                    link_data.stock_status
                )
            
            return BookLink(**dict(row))
    
    async def get_book_links(
        self,
        book_id: int,
        user_latitude: Optional[float] = None,
        user_longitude: Optional[float] = None
    ) -> List[Dict]:
        """
        Get purchase links for a book, sorted by priority:
        1. Distance from user (if GPS provided)
        2. Commission rate (higher is better)
        """
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch('''
                SELECT 
                    bl.id,
                    bl.book_id,
                    bl.purchase_url,
                    bl.price,
                    bl.stock_status,
                    bs.id as bookstore_id,
                    bs.name as bookstore_name,
                    bs.address as bookstore_address,
                    bs.latitude as bookstore_latitude,
                    bs.longitude as bookstore_longitude,
                    bs.commission_rate,
                    bs.phone as bookstore_phone,
                    bs.website as bookstore_website,
                    b.title as book_title,
                    b.authors as book_authors,
                    b.cover_link as book_cover_link,
                    b.category as book_category,
                    b.current_price as book_original_price
                FROM book_links bl
                JOIN bookstores bs ON bl.bookstore_id = bs.id
                LEFT JOIN books b ON bl.book_id = b.product_id
                WHERE bl.book_id = $1 AND bs.is_active = true
                ORDER BY bs.commission_rate DESC
            ''', book_id)
            
            links = []
            for row in rows:
                link_dict = dict(row)
                
                # Calculate distance if user GPS provided
                if user_latitude is not None and user_longitude is not None:
                    distance = self._calculate_distance(
                        user_latitude,
                        user_longitude,
                        link_dict['bookstore_latitude'],
                        link_dict['bookstore_longitude']
                    )
                    link_dict['distance_km'] = round(distance, 2)
                else:
                    link_dict['distance_km'] = None
                
                links.append(link_dict)
            
            # Sort by distance first (if available), then by commission rate
            if user_latitude is not None and user_longitude is not None:
                links.sort(key=lambda x: (x['distance_km'], -x['commission_rate']))
            
            return links
    
    @staticmethod
    def _calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two GPS coordinates using Haversine formula
        Returns distance in kilometers
        """
        # Radius of Earth in kilometers
        R = 6371.0
        
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        return distance
    
    async def delete_book_link(self, link_id: int) -> bool:
        """Delete a book purchase link"""
        async with self.db_pool.acquire() as conn:
            result = await conn.execute(
                'DELETE FROM book_links WHERE id = $1',
                link_id
            )
            return result == 'DELETE 1'
    
    async def get_bookstore_books(self, bookstore_id: int) -> List[Dict]:
        """Get all books available at a bookstore"""
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch('''
                SELECT 
                    bl.*,
                    b.title,
                    b.authors,
                    b.cover_link,
                    b.category,
                    b.current_price as original_price
                FROM book_links bl
                LEFT JOIN books b ON bl.book_id = b.product_id
                WHERE bl.bookstore_id = $1
                ORDER BY bl.created_at DESC
            ''', bookstore_id)
            
            return [dict(row) for row in rows]
    
    async def get_book_info(self, book_id: int) -> Optional[Dict]:
        """Get book information by product_id"""
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow('''
                SELECT * FROM books WHERE product_id = $1
            ''', book_id)
            
            if row:
                return dict(row)
            return None
    
    async def search_books(self, query: str, limit: int = 20) -> List[Dict]:
        """Search books by title or author"""
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch('''
                SELECT * FROM books
                WHERE 
                    LOWER(title) LIKE LOWER($1) OR
                    LOWER(authors) LIKE LOWER($1) OR
                    LOWER(category) LIKE LOWER($1)
                ORDER BY avg_rating DESC, n_review DESC
                LIMIT $2
            ''', f'%{query}%', limit)
            
            return [dict(row) for row in rows]
