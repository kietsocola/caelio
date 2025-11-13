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
    stock_quantity: Optional[int] = 0
    stock_status: Optional[str] = "available"  # available, out_of_stock, pre_order


class BookLink(BaseModel):
    """Schema for book purchase link"""
    id: int
    book_id: int
    bookstore_id: int
    purchase_url: str
    price: Optional[float] = None
    stock_quantity: int
    sold_count: int
    view_count: int
    stock_status: str
    created_at: datetime


class OrderItemCreate(BaseModel):
    """Schema for creating order item"""
    book_link_id: int
    quantity: int


class OrderCreate(BaseModel):
    """Schema for creating an order"""
    items: List[OrderItemCreate]
    shipping_name: str
    shipping_phone: str
    shipping_address: str
    payment_method: str  # cash, credit_card, bank_transfer, momo, zalopay
    notes: Optional[str] = None


class OrderItem(BaseModel):
    """Schema for order item"""
    id: int
    order_id: int
    book_link_id: int
    book_id: int
    book_title: str
    quantity: int
    unit_price: float
    subtotal: float
    created_at: datetime


class Order(BaseModel):
    """Schema for order"""
    id: int
    user_id: int
    bookstore_id: int
    order_number: str
    total_amount: float
    order_status: str  # pending, confirmed, processing, shipped, delivered, cancelled
    payment_status: str  # unpaid, paid, refunded
    payment_method: str
    shipping_address: str
    shipping_phone: str
    shipping_name: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    items: Optional[List[OrderItem]] = None


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
    
    async def delete_bookstore(self, bookstore_id: int) -> bool:
        """Delete a bookstore (admin only)"""
        async with self.db_pool.acquire() as conn:
            # Check if bookstore has any orders
            has_orders = await conn.fetchval(
                'SELECT EXISTS(SELECT 1 FROM orders WHERE bookstore_id = $1)',
                bookstore_id
            )
            
            if has_orders:
                # Soft delete - deactivate instead of deleting
                result = await conn.execute(
                    'UPDATE bookstores SET is_active = false WHERE id = $1',
                    bookstore_id
                )
                return result == 'UPDATE 1'
            else:
                # Hard delete if no orders
                result = await conn.execute(
                    'DELETE FROM bookstores WHERE id = $1',
                    bookstore_id
                )
                return result == 'DELETE 1'
    
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
                    SET purchase_url = $1, price = $2, stock_quantity = $3, stock_status = $4, updated_at = CURRENT_TIMESTAMP
                    WHERE book_id = $5 AND bookstore_id = $6
                    RETURNING *
                ''',
                    link_data.purchase_url,
                    link_data.price,
                    link_data.stock_quantity,
                    link_data.stock_status,
                    link_data.book_id,
                    link_data.bookstore_id
                )
            else:
                # Insert new link
                row = await conn.fetchrow('''
                    INSERT INTO book_links (
                        book_id, bookstore_id, purchase_url, price, stock_quantity, stock_status
                    )
                    VALUES ($1, $2, $3, $4, $5, $6)
                    RETURNING *
                ''',
                    link_data.book_id,
                    link_data.bookstore_id,
                    link_data.purchase_url,
                    link_data.price,
                    link_data.stock_quantity,
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
    
    async def update_book_link(self, link_id: int, update_data: Dict) -> Optional[BookLink]:
        """Update a book purchase link"""
        async with self.db_pool.acquire() as conn:
            # Build update query dynamically
            set_clauses = []
            values = []
            param_index = 1
            
            for key, value in update_data.items():
                if key not in ['id', 'book_id', 'bookstore_id', 'created_at']:
                    set_clauses.append(f"{key} = ${param_index}")
                    values.append(value)
                    param_index += 1
            
            if not set_clauses:
                return await self.get_book_link_by_id(link_id)
            
            set_clauses.append(f"updated_at = CURRENT_TIMESTAMP")
            values.append(link_id)
            query = f'''
                UPDATE book_links
                SET {', '.join(set_clauses)}
                WHERE id = ${param_index}
                RETURNING *
            '''
            
            row = await conn.fetchrow(query, *values)
            if row:
                return BookLink(**dict(row))
            return None
    
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
    
    async def get_books_with_links(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get all books that have purchase links"""
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch('''
                SELECT DISTINCT
                    b.*,
                    COUNT(bl.id) as link_count,
                    MIN(bl.price) as min_price,
                    MAX(bl.price) as max_price
                FROM books b
                INNER JOIN book_links bl ON b.product_id = bl.book_id
                INNER JOIN bookstores bs ON bl.bookstore_id = bs.id
                WHERE bs.is_active = true
                GROUP BY b.product_id
                ORDER BY link_count DESC, b.avg_rating DESC
                LIMIT $1 OFFSET $2
            ''', limit, offset)
            
            return [dict(row) for row in rows]
    
    async def increment_view_count(self, book_link_id: int) -> bool:
        """Increment view count for a book link"""
        async with self.db_pool.acquire() as conn:
            result = await conn.execute('''
                UPDATE book_links
                SET view_count = view_count + 1
                WHERE id = $1
            ''', book_link_id)
            return result == 'UPDATE 1'
    
    async def get_book_link_by_id(self, book_link_id: int) -> Optional[Dict]:
        """Get book link by ID with full info"""
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow('''
                SELECT 
                    bl.*,
                    b.title,
                    b.authors,
                    b.cover_link,
                    b.category,
                    b.current_price as original_price,
                    bs.name as bookstore_name,
                    bs.address as bookstore_address
                FROM book_links bl
                LEFT JOIN books b ON bl.book_id = b.product_id
                LEFT JOIN bookstores bs ON bl.bookstore_id = bs.id
                WHERE bl.id = $1
            ''', book_link_id)
            
            if row:
                return dict(row)
            return None
    
    async def create_order(self, user_id: int, order_data: OrderCreate) -> Order:
        """Create a new order"""
        import uuid
        from datetime import datetime
        
        async with self.db_pool.acquire() as conn:
            # Start transaction
            async with conn.transaction():
                # Get items info and calculate total
                total_amount = 0
                bookstore_id = None
                items_data = []
                
                for item in order_data.items:
                    # Get book link info
                    link = await conn.fetchrow('''
                        SELECT bl.*, b.title, bs.id as bookstore_id
                        FROM book_links bl
                        LEFT JOIN books b ON bl.book_id = b.product_id
                        LEFT JOIN bookstores bs ON bl.bookstore_id = bs.id
                        WHERE bl.id = $1
                    ''', item.book_link_id)
                    
                    if not link:
                        raise ValueError(f"Book link {item.book_link_id} not found")
                    
                    # Check stock
                    if link['stock_quantity'] < item.quantity:
                        raise ValueError(f"Insufficient stock for {link['title']}")
                    
                    # Set bookstore_id (all items must be from same bookstore)
                    if bookstore_id is None:
                        bookstore_id = link['bookstore_id']
                    elif bookstore_id != link['bookstore_id']:
                        raise ValueError("All items must be from the same bookstore")
                    
                    subtotal = link['price'] * item.quantity
                    total_amount += subtotal
                    
                    items_data.append({
                        'book_link_id': item.book_link_id,
                        'book_id': link['book_id'],
                        'book_title': link['title'],
                        'quantity': item.quantity,
                        'unit_price': link['price'],
                        'subtotal': subtotal
                    })
                
                # Generate order number
                order_number = f"ORD{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:8].upper()}"
                
                # Create order
                order_row = await conn.fetchrow('''
                    INSERT INTO orders (
                        user_id, bookstore_id, order_number, total_amount,
                        shipping_name, shipping_phone, shipping_address,
                        payment_method, notes
                    )
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    RETURNING *
                ''',
                    user_id, bookstore_id, order_number, total_amount,
                    order_data.shipping_name, order_data.shipping_phone,
                    order_data.shipping_address, order_data.payment_method,
                    order_data.notes
                )
                
                order_id = order_row['id']
                
                # Create order items and update stock
                order_items = []
                for item_data in items_data:
                    # Insert order item
                    item_row = await conn.fetchrow('''
                        INSERT INTO order_items (
                            order_id, book_link_id, book_id, book_title,
                            quantity, unit_price, subtotal
                        )
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                        RETURNING *
                    ''',
                        order_id, item_data['book_link_id'], item_data['book_id'],
                        item_data['book_title'], item_data['quantity'],
                        item_data['unit_price'], item_data['subtotal']
                    )
                    order_items.append(OrderItem(**dict(item_row)))
                    
                    # Update stock and sold count
                    await conn.execute('''
                        UPDATE book_links
                        SET stock_quantity = stock_quantity - $1,
                            sold_count = sold_count + $1,
                            stock_status = CASE 
                                WHEN stock_quantity - $1 <= 0 THEN 'out_of_stock'
                                ELSE stock_status
                            END
                        WHERE id = $2
                    ''', item_data['quantity'], item_data['book_link_id'])
                
                order = Order(**dict(order_row), items=order_items)
                return order
    
    async def get_order_by_id(self, order_id: int, user_id: Optional[int] = None) -> Optional[Order]:
        """Get order by ID with items"""
        async with self.db_pool.acquire() as conn:
            # Get order
            query = 'SELECT * FROM orders WHERE id = $1'
            params = [order_id]
            
            if user_id is not None:
                query += ' AND user_id = $2'
                params.append(user_id)
            
            order_row = await conn.fetchrow(query, *params)
            if not order_row:
                return None
            
            # Get order items
            items_rows = await conn.fetch('''
                SELECT * FROM order_items WHERE order_id = $1
            ''', order_id)
            
            items = [OrderItem(**dict(row)) for row in items_rows]
            order = Order(**dict(order_row), items=items)
            return order
    
    async def get_user_orders(self, user_id: int, limit: int = 20, offset: int = 0) -> List[Order]:
        """Get user's orders"""
        async with self.db_pool.acquire() as conn:
            orders_rows = await conn.fetch('''
                SELECT * FROM orders
                WHERE user_id = $1
                ORDER BY created_at DESC
                LIMIT $2 OFFSET $3
            ''', user_id, limit, offset)
            
            orders = []
            for order_row in orders_rows:
                # Get items for each order
                items_rows = await conn.fetch('''
                    SELECT * FROM order_items WHERE order_id = $1
                ''', order_row['id'])
                
                items = [OrderItem(**dict(row)) for row in items_rows]
                order = Order(**dict(order_row), items=items)
                orders.append(order)
            
            return orders
    
    async def get_bookstore_orders(self, bookstore_id: int, limit: int = 50, offset: int = 0) -> List[Order]:
        """Get bookstore's orders"""
        async with self.db_pool.acquire() as conn:
            orders_rows = await conn.fetch('''
                SELECT * FROM orders
                WHERE bookstore_id = $1
                ORDER BY created_at DESC
                LIMIT $2 OFFSET $3
            ''', bookstore_id, limit, offset)
            
            orders = []
            for order_row in orders_rows:
                items_rows = await conn.fetch('''
                    SELECT * FROM order_items WHERE order_id = $1
                ''', order_row['id'])
                
                items = [OrderItem(**dict(row)) for row in items_rows]
                order = Order(**dict(order_row), items=items)
                orders.append(order)
            
            return orders
    
    async def update_order_status(
        self,
        order_id: int,
        order_status: Optional[str] = None,
        payment_status: Optional[str] = None
    ) -> Optional[Order]:
        """Update order status"""
        async with self.db_pool.acquire() as conn:
            updates = []
            params = []
            param_idx = 1
            
            if order_status:
                updates.append(f"order_status = ${param_idx}")
                params.append(order_status)
                param_idx += 1
            
            if payment_status:
                updates.append(f"payment_status = ${param_idx}")
                params.append(payment_status)
                param_idx += 1
            
            if not updates:
                return await self.get_order_by_id(order_id)
            
            updates.append(f"updated_at = CURRENT_TIMESTAMP")
            params.append(order_id)
            
            query = f'''
                UPDATE orders
                SET {', '.join(updates)}
                WHERE id = ${param_idx}
                RETURNING *
            '''
            
            order_row = await conn.fetchrow(query, *params)
            if not order_row:
                return None
            
            return await self.get_order_by_id(order_id)
    
    async def cancel_order(self, order_id: int, user_id: int) -> bool:
        """Cancel order and restore stock"""
        async with self.db_pool.acquire() as conn:
            async with conn.transaction():
                # Check order belongs to user and is cancellable
                order = await conn.fetchrow('''
                    SELECT * FROM orders
                    WHERE id = $1 AND user_id = $2
                    AND order_status IN ('pending', 'confirmed')
                ''', order_id, user_id)
                
                if not order:
                    return False
                
                # Restore stock
                items = await conn.fetch('''
                    SELECT * FROM order_items WHERE order_id = $1
                ''', order_id)
                
                for item in items:
                    await conn.execute('''
                        UPDATE book_links
                        SET stock_quantity = stock_quantity + $1,
                            sold_count = sold_count - $1,
                            stock_status = CASE 
                                WHEN stock_quantity + $1 > 0 THEN 'available'
                                ELSE stock_status
                            END
                        WHERE id = $2
                    ''', item['quantity'], item['book_link_id'])
                
                # Update order status
                await conn.execute('''
                    UPDATE orders
                    SET order_status = 'cancelled', updated_at = CURRENT_TIMESTAMP
                    WHERE id = $1
                ''', order_id)
                
                return True
    
    async def get_bookstore_statistics(self, bookstore_id: int) -> Dict:
        """Get bookstore statistics"""
        async with self.db_pool.acquire() as conn:
            # Total orders
            total_orders = await conn.fetchval('''
                SELECT COUNT(*) FROM orders WHERE bookstore_id = $1
            ''', bookstore_id)
            
            # Total revenue
            total_revenue = await conn.fetchval('''
                SELECT COALESCE(SUM(total_amount), 0) FROM orders
                WHERE bookstore_id = $1 AND payment_status = 'paid'
            ''', bookstore_id)
            
            # Total books sold
            total_books_sold = await conn.fetchval('''
                SELECT COALESCE(SUM(oi.quantity), 0)
                FROM order_items oi
                JOIN orders o ON oi.order_id = o.id
                WHERE o.bookstore_id = $1
            ''', bookstore_id)
            
            # Total views
            total_views = await conn.fetchval('''
                SELECT COALESCE(SUM(view_count), 0)
                FROM book_links
                WHERE bookstore_id = $1
            ''', bookstore_id)
            
            # Order status breakdown
            order_status = await conn.fetch('''
                SELECT order_status, COUNT(*) as count
                FROM orders
                WHERE bookstore_id = $1
                GROUP BY order_status
            ''', bookstore_id)
            
            # Top selling books
            top_books = await conn.fetch('''
                SELECT 
                    bl.book_id,
                    b.title,
                    b.authors,
                    SUM(oi.quantity) as total_sold,
                    SUM(oi.subtotal) as total_revenue
                FROM order_items oi
                JOIN orders o ON oi.order_id = o.id
                JOIN book_links bl ON oi.book_link_id = bl.id
                LEFT JOIN books b ON bl.book_id = b.product_id
                WHERE o.bookstore_id = $1
                GROUP BY bl.book_id, b.title, b.authors
                ORDER BY total_sold DESC
                LIMIT 10
            ''', bookstore_id)
            
            return {
                'total_orders': total_orders,
                'total_revenue': float(total_revenue) if total_revenue else 0,
                'total_books_sold': total_books_sold,
                'total_views': total_views,
                'order_status_breakdown': [dict(row) for row in order_status],
                'top_selling_books': [dict(row) for row in top_books]
            }
