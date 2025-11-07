"""
White Books system - User-generated content with chapters
Users can create books with multiple chapters
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import asyncpg


class ChapterCreate(BaseModel):
    """Schema for creating a chapter"""
    chapter_number: int
    chapter_title: str
    content: str


class Chapter(BaseModel):
    """Schema for a book chapter"""
    id: int
    book_id: int
    chapter_number: int
    chapter_title: str
    content: str
    created_at: datetime
    updated_at: datetime


class WhiteBookCreate(BaseModel):
    """Schema for creating a white book"""
    title: str
    cover_image: Optional[str] = None
    description: Optional[str] = None
    emotional_layer: Optional[str] = None
    tags: List[str] = []
    chapters: List[ChapterCreate] = []  # Can create with chapters


class WhiteBookUpdate(BaseModel):
    """Schema for updating a white book"""
    title: Optional[str] = None
    cover_image: Optional[str] = None
    description: Optional[str] = None
    emotional_layer: Optional[str] = None
    tags: Optional[List[str]] = None


class WhiteBook(BaseModel):
    """Schema for a white book"""
    id: int
    author_id: int
    author_username: Optional[str] = None
    title: str
    cover_image: Optional[str]
    description: Optional[str]
    emotional_layer: Optional[str]
    tags: List[str]
    is_published: bool
    view_count: int
    like_count: int
    created_at: datetime
    updated_at: datetime
    chapters: Optional[List[Chapter]] = None
    chapter_count: Optional[int] = None

class WhiteBooksManager:
    """Manager for white books operations"""
    
    def __init__(self, db_pool):
        self.db_pool = db_pool
    
    async def create_book(self, author_id: int, book_data: WhiteBookCreate) -> WhiteBook:
        """Create a new white book with optional chapters"""
        async with self.db_pool.acquire() as conn:
            async with conn.transaction():
                # Create book
                book_id = await conn.fetchval('''
                    INSERT INTO white_books (
                        author_id, title, cover_image, description, 
                        emotional_layer, tags
                    )
                    VALUES ($1, $2, $3, $4, $5, $6)
                    RETURNING id
                ''', 
                    author_id, book_data.title, book_data.cover_image,
                    book_data.description, book_data.emotional_layer, book_data.tags
                )
                
                print(f"DEBUG: Created book with ID: {book_id}")
                
                # Create chapters if provided
                if book_data.chapters:
                    for chapter in book_data.chapters:
                        await conn.execute('''
                            INSERT INTO white_book_chapters (
                                book_id, chapter_number, chapter_title, content
                            )
                            VALUES ($1, $2, $3, $4)
                        ''',
                            book_id, chapter.chapter_number, 
                            chapter.chapter_title, chapter.content
                        )
        
        # Get the created book with chapters (after transaction commits)
        result = await self.get_book_by_id(book_id, include_author=True, include_chapters=True)
        print(f"DEBUG: get_book_by_id returned: {result}")
        return result
    
    async def update_book(self, book_id: int, author_id: int, update_data: WhiteBookUpdate) -> Optional[WhiteBook]:
        """Update white book information"""
        async with self.db_pool.acquire() as conn:
            # Check ownership
            owner = await conn.fetchval(
                'SELECT author_id FROM white_books WHERE id = $1',
                book_id
            )
            if owner != author_id:
                return None
            
            # Build update query
            updates = []
            values = []
            param_idx = 1
            
            if update_data.title is not None:
                updates.append(f"title = ${param_idx}")
                values.append(update_data.title)
                param_idx += 1
            
            if update_data.cover_image is not None:
                updates.append(f"cover_image = ${param_idx}")
                values.append(update_data.cover_image)
                param_idx += 1
            
            if update_data.description is not None:
                updates.append(f"description = ${param_idx}")
                values.append(update_data.description)
                param_idx += 1
            
            if update_data.emotional_layer is not None:
                updates.append(f"emotional_layer = ${param_idx}")
                values.append(update_data.emotional_layer)
                param_idx += 1
            
            if update_data.tags is not None:
                updates.append(f"tags = ${param_idx}")
                values.append(update_data.tags)
                param_idx += 1
            
            if not updates:
                return await self.get_book_by_id(book_id, include_chapters=True)
            
            updates.append("updated_at = CURRENT_TIMESTAMP")
            values.append(book_id)
            
            query = f'''
                UPDATE white_books
                SET {', '.join(updates)}
                WHERE id = ${param_idx}
            '''
            
            await conn.execute(query, *values)
            return await self.get_book_by_id(book_id, include_chapters=True)
    
    async def add_chapter(self, book_id: int, author_id: int, chapter_data: ChapterCreate) -> Optional[Chapter]:
        """Add a new chapter to a book"""
        async with self.db_pool.acquire() as conn:
            # Check ownership
            owner = await conn.fetchval(
                'SELECT author_id FROM white_books WHERE id = $1',
                book_id
            )
            if owner != author_id:
                return None
            
            # Check if chapter number already exists
            existing = await conn.fetchval('''
                SELECT id FROM white_book_chapters
                WHERE book_id = $1 AND chapter_number = $2
            ''', book_id, chapter_data.chapter_number)
            
            if existing:
                # Update existing chapter
                row = await conn.fetchrow('''
                    UPDATE white_book_chapters
                    SET chapter_title = $1, content = $2, updated_at = CURRENT_TIMESTAMP
                    WHERE book_id = $3 AND chapter_number = $4
                    RETURNING *
                ''',
                    chapter_data.chapter_title, chapter_data.content,
                    book_id, chapter_data.chapter_number
                )
            else:
                # Insert new chapter
                row = await conn.fetchrow('''
                    INSERT INTO white_book_chapters (
                        book_id, chapter_number, chapter_title, content
                    )
                    VALUES ($1, $2, $3, $4)
                    RETURNING *
                ''',
                    book_id, chapter_data.chapter_number,
                    chapter_data.chapter_title, chapter_data.content
                )
            
            # Update book's updated_at
            await conn.execute('''
                UPDATE white_books SET updated_at = CURRENT_TIMESTAMP WHERE id = $1
            ''', book_id)
            
            return Chapter(**dict(row))
    
    async def delete_chapter(self, book_id: int, chapter_id: int, author_id: int) -> bool:
        """Delete a chapter"""
        async with self.db_pool.acquire() as conn:
            # Check ownership
            owner = await conn.fetchval(
                'SELECT author_id FROM white_books WHERE id = $1',
                book_id
            )
            if owner != author_id:
                return False
            
            result = await conn.execute('''
                DELETE FROM white_book_chapters
                WHERE id = $1 AND book_id = $2
            ''', chapter_id, book_id)
            
            # Update book's updated_at
            await conn.execute('''
                UPDATE white_books SET updated_at = CURRENT_TIMESTAMP WHERE id = $1
            ''', book_id)
            
            return result == 'DELETE 1'
    
    async def get_book_by_id(
        self, 
        book_id: int, 
        include_author: bool = False,
        include_chapters: bool = False
    ) -> Optional[WhiteBook]:
        """Get book by ID"""
        async with self.db_pool.acquire() as conn:
            if include_author:
                query = '''
                    SELECT wb.*, u.username as author_username
                    FROM white_books wb
                    LEFT JOIN users u ON wb.author_id = u.user_id
                    WHERE wb.id = $1
                '''
            else:
                query = '''
                    SELECT *, NULL as author_username
                    FROM white_books
                    WHERE id = $1
                '''
            
            row = await conn.fetchrow(query, book_id)
            if not row:
                return None
            
            book_dict = dict(row)
            
            # Get chapters if requested
            chapters = None
            chapter_count = 0
            if include_chapters:
                chapter_rows = await conn.fetch('''
                    SELECT * FROM white_book_chapters
                    WHERE book_id = $1
                    ORDER BY chapter_number ASC
                ''', book_id)
                chapters = [Chapter(**dict(r)) for r in chapter_rows]
                chapter_count = len(chapters)
            else:
                chapter_count = await conn.fetchval('''
                    SELECT COUNT(*) FROM white_book_chapters WHERE book_id = $1
                ''', book_id)
            
            return WhiteBook(
                id=book_dict['id'],
                author_id=book_dict['author_id'],
                author_username=book_dict.get('author_username'),
                title=book_dict['title'],
                cover_image=book_dict.get('cover_image'),
                description=book_dict.get('description'),
                emotional_layer=book_dict.get('emotional_layer'),
                tags=book_dict.get('tags') or [],
                is_published=book_dict['is_published'],
                view_count=book_dict['view_count'],
                like_count=book_dict['like_count'],
                created_at=book_dict['created_at'],
                updated_at=book_dict['updated_at'],
                chapters=chapters,
                chapter_count=chapter_count
            )
    
    async def get_user_books(self, author_id: int, include_chapters: bool = False) -> List[WhiteBook]:
        """Get all books by a user"""
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch('''
                SELECT wb.*, 
                       (SELECT COUNT(*) FROM white_book_chapters WHERE book_id = wb.id) as chapter_count
                FROM white_books wb
                WHERE wb.author_id = $1
                ORDER BY wb.created_at DESC
            ''', author_id)
            
            books = []
            for row in rows:
                book_dict = dict(row)
                
                chapters = None
                if include_chapters:
                    chapter_rows = await conn.fetch('''
                        SELECT * FROM white_book_chapters
                        WHERE book_id = $1
                        ORDER BY chapter_number ASC
                    ''', book_dict['id'])
                    chapters = [Chapter(**dict(r)) for r in chapter_rows]
                
                books.append(WhiteBook(
                    id=book_dict['id'],
                    author_id=book_dict['author_id'],
                    author_username=None,
                    title=book_dict['title'],
                    cover_image=book_dict.get('cover_image'),
                    description=book_dict.get('description'),
                    emotional_layer=book_dict.get('emotional_layer'),
                    tags=book_dict.get('tags') or [],
                    is_published=book_dict['is_published'],
                    view_count=book_dict['view_count'],
                    like_count=book_dict['like_count'],
                    created_at=book_dict['created_at'],
                    updated_at=book_dict['updated_at'],
                    chapters=chapters,
                    chapter_count=book_dict['chapter_count']
                ))
            
            return books
    
    async def publish_book(self, book_id: int, author_id: int) -> bool:
        """Publish a book (only author can publish their own book)"""
        async with self.db_pool.acquire() as conn:
            result = await conn.execute('''
                UPDATE white_books
                SET is_published = TRUE, updated_at = CURRENT_TIMESTAMP
                WHERE id = $1 AND author_id = $2
            ''', book_id, author_id)
            
            return result == "UPDATE 1"
    
    async def unpublish_book(self, book_id: int, author_id: int) -> bool:
        """Unpublish a book"""
        async with self.db_pool.acquire() as conn:
            result = await conn.execute('''
                UPDATE white_books
                SET is_published = FALSE, updated_at = CURRENT_TIMESTAMP
                WHERE id = $1 AND author_id = $2
            ''', book_id, author_id)
            
            return result == "UPDATE 1"
    
    async def delete_book(self, book_id: int, author_id: int) -> bool:
        """Delete a book (only unpublished books can be deleted)"""
        async with self.db_pool.acquire() as conn:
            result = await conn.execute('''
                DELETE FROM white_books
                WHERE id = $1 AND author_id = $2 AND is_published = FALSE
            ''', book_id, author_id)
            
            return result == "DELETE 1"
    
    async def get_published_books(
        self, 
        emotional_layer: Optional[str] = None,
        limit: int = 20, 
        offset: int = 0
    ) -> List[WhiteBook]:
        """Get published books, optionally filtered by emotional layer"""
        async with self.db_pool.acquire() as conn:
            if emotional_layer:
                query = '''
                    SELECT wb.*, u.username as author_username,
                           (SELECT COUNT(*) FROM white_book_chapters WHERE book_id = wb.id) as chapter_count
                    FROM white_books wb
                    LEFT JOIN users u ON wb.author_id = u.user_id
                    WHERE wb.is_published = TRUE AND wb.emotional_layer = $1
                    ORDER BY wb.created_at DESC
                    LIMIT $2 OFFSET $3
                '''
                rows = await conn.fetch(query, emotional_layer, limit, offset)
            else:
                query = '''
                    SELECT wb.*, u.username as author_username,
                           (SELECT COUNT(*) FROM white_book_chapters WHERE book_id = wb.id) as chapter_count
                    FROM white_books wb
                    LEFT JOIN users u ON wb.author_id = u.user_id
                    WHERE wb.is_published = TRUE
                    ORDER BY wb.created_at DESC
                    LIMIT $1 OFFSET $2
                '''
                rows = await conn.fetch(query, limit, offset)
            
            books = []
            for row in rows:
                book_dict = dict(row)
                books.append(WhiteBook(
                    id=book_dict['id'],
                    author_id=book_dict['author_id'],
                    author_username=book_dict.get('author_username'),
                    title=book_dict['title'],
                    cover_image=book_dict.get('cover_image'),
                    description=book_dict.get('description'),
                    emotional_layer=book_dict.get('emotional_layer'),
                    tags=book_dict.get('tags') or [],
                    is_published=book_dict['is_published'],
                    view_count=book_dict['view_count'],
                    like_count=book_dict['like_count'],
                    created_at=book_dict['created_at'],
                    updated_at=book_dict['updated_at'],
                    chapters=None,
                    chapter_count=book_dict['chapter_count']
                ))
            
            return books
    
    async def increment_view_count(self, book_id: int) -> bool:
        """Increment view count for a book"""
        async with self.db_pool.acquire() as conn:
            result = await conn.execute('''
                UPDATE white_books
                SET view_count = view_count + 1
                WHERE id = $1 AND is_published = TRUE
            ''', book_id)
            
            return result == "UPDATE 1"
    
    async def toggle_like(self, book_id: int, user_id: int) -> Dict[str, Any]:
        """Toggle like for a book (simplified version - just increment/decrement)"""
        async with self.db_pool.acquire() as conn:
            # For now, just increment like count
            # TODO: Create a likes table to track who liked what
            await conn.execute('''
                UPDATE white_books
                SET like_count = like_count + 1
                WHERE id = $1 AND is_published = TRUE
            ''', book_id)
            
            new_count = await conn.fetchval(
                'SELECT like_count FROM white_books WHERE id = $1',
                book_id
            )
            
            return {"liked": True, "like_count": new_count}
    
    async def increment_views(self, book_id: int) -> None:
        """Increment view count for a book"""
        async with self.db_pool.acquire() as conn:
            await conn.execute('''
                UPDATE white_books
                SET view_count = view_count + 1
                WHERE id = $1
            ''', book_id)
    
    async def search_books(self, query: str, limit: int = 20) -> List[WhiteBook]:
        """Search published books by title, description or tags"""
        async with self.db_pool.acquire() as conn:
            search_query = f"%{query}%"
            rows = await conn.fetch('''
                SELECT wb.*, u.username as author_username,
                       (SELECT COUNT(*) FROM white_book_chapters WHERE book_id = wb.id) as chapter_count
                FROM white_books wb
                LEFT JOIN users u ON wb.author_id = u.user_id
                WHERE wb.is_published = TRUE 
                AND (
                    wb.title ILIKE $1 
                    OR wb.description ILIKE $1
                    OR EXISTS (
                        SELECT 1 FROM unnest(wb.tags) as tag 
                        WHERE tag ILIKE $1
                    )
                )
                ORDER BY wb.view_count DESC, wb.created_at DESC
                LIMIT $2
            ''', search_query, limit)
            
            books = []
            for row in rows:
                book_dict = dict(row)
                books.append(WhiteBook(
                    id=book_dict['id'],
                    author_id=book_dict['author_id'],
                    author_username=book_dict.get('author_username'),
                    title=book_dict['title'],
                    cover_image=book_dict.get('cover_image'),
                    description=book_dict.get('description'),
                    emotional_layer=book_dict.get('emotional_layer'),
                    tags=book_dict.get('tags') or [],
                    is_published=book_dict['is_published'],
                    view_count=book_dict['view_count'],
                    like_count=book_dict['like_count'],
                    created_at=book_dict['created_at'],
                    updated_at=book_dict['updated_at'],
                    chapters=None,
                    chapter_count=book_dict['chapter_count']
                ))
            
            return books
    
    async def get_chapter(self, chapter_id: int) -> Optional[Chapter]:
        """Get a specific chapter"""
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow('''
                SELECT * FROM white_book_chapters WHERE id = $1
            ''', chapter_id)
            
            if row:
                return Chapter(**dict(row))
            return None
    
    async def get_book_chapters(self, book_id: int) -> List[Chapter]:
        """Get all chapters of a book"""
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch('''
                SELECT * FROM white_book_chapters
                WHERE book_id = $1
                ORDER BY chapter_number ASC
            ''', book_id)
            
            return [Chapter(**dict(row)) for row in rows]