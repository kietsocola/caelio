"""
White Books system - User-generated content
Simple book creation and publishing
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import asyncpg

class WhiteBookCreate(BaseModel):
    title: str
    category: Optional[str] = None
    content: str
    emotional_layer: Optional[str] = None
    prompt_used: Optional[str] = None
    tags: List[str] = []

class WhiteBook(BaseModel):
    book_id: int
    author_id: int
    author_username: Optional[str] = None
    title: str
    category: Optional[str]
    content: str
    emotional_layer: Optional[str]
    prompt_used: Optional[str]
    tags: List[str]
    is_published: bool
    created_at: datetime
    updated_at: datetime
    views: int
    likes: int

class WhiteBooksManager:
    def __init__(self, db_pool):
        self.db_pool = db_pool
    
    async def create_book(self, author_id: int, book_data: WhiteBookCreate) -> WhiteBook:
        """Create a new white book"""
        async with self.db_pool.acquire() as conn:
            book_id = await conn.fetchval('''
                INSERT INTO white_books (
                    author_id, title, category, content, emotional_layer, 
                    prompt_used, tags, created_at, updated_at
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $8)
                RETURNING book_id
            ''', 
                author_id, book_data.title, book_data.category, book_data.content,
                book_data.emotional_layer, book_data.prompt_used, book_data.tags,
                datetime.now()
            )
            
            # Get the created book
            return await self.get_book_by_id(book_id, include_author=True)
    
    async def get_book_by_id(self, book_id: int, include_author: bool = False) -> Optional[WhiteBook]:
        """Get book by ID"""
        async with self.db_pool.acquire() as conn:
            if include_author:
                query = '''
                    SELECT wb.*, u.username as author_username
                    FROM white_books wb
                    JOIN users u ON wb.author_id = u.user_id
                    WHERE wb.book_id = $1
                '''
            else:
                query = '''
                    SELECT *, NULL as author_username
                    FROM white_books
                    WHERE book_id = $1
                '''
            
            row = await conn.fetchrow(query, book_id)
            
            if row:
                return WhiteBook(
                    book_id=row['book_id'],
                    author_id=row['author_id'],
                    author_username=row.get('author_username'),
                    title=row['title'],
                    category=row['category'],
                    content=row['content'],
                    emotional_layer=row['emotional_layer'],
                    prompt_used=row['prompt_used'],
                    tags=row['tags'] or [],
                    is_published=row['is_published'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    views=row['views'],
                    likes=row['likes']
                )
        return None
    
    async def get_user_books(self, author_id: int) -> List[WhiteBook]:
        """Get all books by a user"""
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch('''
                SELECT *, NULL as author_username
                FROM white_books
                WHERE author_id = $1
                ORDER BY created_at DESC
            ''', author_id)
            
            books = []
            for row in rows:
                books.append(WhiteBook(
                    book_id=row['book_id'],
                    author_id=row['author_id'],
                    author_username=row.get('author_username'),
                    title=row['title'],
                    category=row['category'],
                    content=row['content'],
                    emotional_layer=row['emotional_layer'],
                    prompt_used=row['prompt_used'],
                    tags=row['tags'] or [],
                    is_published=row['is_published'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    views=row['views'],
                    likes=row['likes']
                ))
            
            return books
    
    async def publish_book(self, book_id: int, author_id: int) -> bool:
        """Publish a book (only author can publish their own book)"""
        async with self.db_pool.acquire() as conn:
            result = await conn.execute('''
                UPDATE white_books
                SET is_published = TRUE, updated_at = $1
                WHERE book_id = $2 AND author_id = $3
            ''', datetime.now(), book_id, author_id)
            
            return result == "UPDATE 1"
    
    async def get_published_books(self, emotional_layer: Optional[str] = None, 
                                 limit: int = 20, offset: int = 0) -> List[WhiteBook]:
        """Get published books, optionally filtered by emotional layer"""
        async with self.db_pool.acquire() as conn:
            if emotional_layer:
                query = '''
                    SELECT wb.*, u.username as author_username
                    FROM white_books wb
                    JOIN users u ON wb.author_id = u.user_id
                    WHERE wb.is_published = TRUE AND wb.emotional_layer = $1
                    ORDER BY wb.created_at DESC
                    LIMIT $2 OFFSET $3
                '''
                rows = await conn.fetch(query, emotional_layer, limit, offset)
            else:
                query = '''
                    SELECT wb.*, u.username as author_username
                    FROM white_books wb
                    JOIN users u ON wb.author_id = u.user_id
                    WHERE wb.is_published = TRUE
                    ORDER BY wb.created_at DESC
                    LIMIT $1 OFFSET $2
                '''
                rows = await conn.fetch(query, limit, offset)
            
            books = []
            for row in rows:
                books.append(WhiteBook(
                    book_id=row['book_id'],
                    author_id=row['author_id'],
                    author_username=row['author_username'],
                    title=row['title'],
                    category=row['category'],
                    content=row['content'],
                    emotional_layer=row['emotional_layer'],
                    prompt_used=row['prompt_used'],
                    tags=row['tags'] or [],
                    is_published=row['is_published'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    views=row['views'],
                    likes=row['likes']
                ))
            
            return books
    
    async def increment_views(self, book_id: int) -> bool:
        """Increment view count for a book"""
        async with self.db_pool.acquire() as conn:
            result = await conn.execute('''
                UPDATE white_books
                SET views = views + 1
                WHERE book_id = $1 AND is_published = TRUE
            ''', book_id)
            
            return result == "UPDATE 1"
    
    async def search_books(self, query: str, limit: int = 20) -> List[WhiteBook]:
        """Search published books by title or content"""
        async with self.db_pool.acquire() as conn:
            search_query = f"%{query}%"
            rows = await conn.fetch('''
                SELECT wb.*, u.username as author_username
                FROM white_books wb
                JOIN users u ON wb.author_id = u.user_id
                WHERE wb.is_published = TRUE 
                AND (wb.title ILIKE $1 OR wb.content ILIKE $1)
                ORDER BY wb.created_at DESC
                LIMIT $2
            ''', search_query, limit)
            
            books = []
            for row in rows:
                books.append(WhiteBook(
                    book_id=row['book_id'],
                    author_id=row['author_id'],
                    author_username=row['author_username'],
                    title=row['title'],
                    category=row['category'],
                    content=row['content'][:500] + "..." if len(row['content']) > 500 else row['content'],
                    emotional_layer=row['emotional_layer'],
                    prompt_used=row['prompt_used'],
                    tags=row['tags'] or [],
                    is_published=row['is_published'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    views=row['views'],
                    likes=row['likes']
                ))
            
            return books