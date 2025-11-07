"""
Database connection and models for Caelio Care
Using PostgreSQL
"""

import asyncpg
import asyncio
from typing import Optional, List, Dict, Any
import json
from datetime import datetime
import os

class Database:
    def __init__(self):
        self.pool = None
        
    async def connect(self):
        """Connect to PostgreSQL database"""
        try:
            self.pool = await asyncpg.create_pool(
                user='postgres',
                password='123', 
                database='caelio_care',
                host='localhost',
                port=5432,
                min_size=1,
                max_size=10
            )
            print("Connected to PostgreSQL successfully")
            await self.create_tables()
        except Exception as e:
            print(f"Database connection failed: {e}")
            raise e
    
    async def create_tables(self):
        """Create necessary tables"""
        async with self.pool.acquire() as conn:
            # Users table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    full_name VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')
            
            # Emotional test results
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS emotional_test_results (
                    result_id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(user_id),
                    answers JSONB NOT NULL,
                    perma_score FLOAT NOT NULL,
                    dass_score FLOAT NOT NULL,
                    mbi_score FLOAT NOT NULL,
                    emotional_layer VARCHAR(50) NOT NULL,
                    archetype VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # White books (user-created books)
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS white_books (
                    id SERIAL PRIMARY KEY,
                    author_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
                    title VARCHAR(500) NOT NULL,
                    cover_image TEXT,
                    description TEXT,
                    emotional_layer VARCHAR(50),
                    tags TEXT[],
                    is_published BOOLEAN DEFAULT FALSE,
                    view_count INTEGER DEFAULT 0,
                    like_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # White book chapters
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS white_book_chapters (
                    id SERIAL PRIMARY KEY,
                    book_id INTEGER REFERENCES white_books(id) ON DELETE CASCADE,
                    chapter_number INTEGER NOT NULL,
                    chapter_title VARCHAR(500) NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(book_id, chapter_number)
                )
            ''')
            
            # Create indexes for white books
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_white_books_author_id ON white_books(author_id)
            ''')
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_white_books_emotional_layer ON white_books(emotional_layer)
            ''')
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_white_books_is_published ON white_books(is_published)
            ''')
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_white_book_chapters_book_id ON white_book_chapters(book_id)
            ''')
            
            # Book recommendations/prescriptions
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS book_prescriptions (
                    prescription_id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(user_id),
                    emotional_layer VARCHAR(50) NOT NULL,
                    recommended_books JSONB,
                    recommended_movies JSONB,
                    writing_prompts JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Books table (from CSV)
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS books (
                    product_id BIGINT PRIMARY KEY,
                    title VARCHAR(500) NOT NULL,
                    authors VARCHAR(500),
                    original_price FLOAT,
                    current_price FLOAT,
                    quantity INTEGER,
                    category VARCHAR(200),
                    n_review INTEGER,
                    avg_rating FLOAT,
                    pages INTEGER,
                    manufacturer VARCHAR(300),
                    cover_link TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Bookstores table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS bookstores (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    phone VARCHAR(50) NOT NULL,
                    address TEXT NOT NULL,
                    latitude FLOAT NOT NULL,
                    longitude FLOAT NOT NULL,
                    commission_rate FLOAT NOT NULL CHECK (commission_rate >= 0 AND commission_rate <= 100),
                    description TEXT,
                    website VARCHAR(500),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Book purchase links table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS book_links (
                    id SERIAL PRIMARY KEY,
                    book_id BIGINT NOT NULL REFERENCES books(product_id) ON DELETE CASCADE,
                    bookstore_id INTEGER REFERENCES bookstores(id) ON DELETE CASCADE,
                    purchase_url TEXT NOT NULL,
                    price FLOAT,
                    stock_quantity INTEGER DEFAULT 0,
                    sold_count INTEGER DEFAULT 0,
                    view_count INTEGER DEFAULT 0,
                    stock_status VARCHAR(50) DEFAULT 'available',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(book_id, bookstore_id)
                )
            ''')
            
            # Create index for faster queries
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_book_links_book_id ON book_links(book_id)
            ''')
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_book_links_bookstore_id ON book_links(bookstore_id)
            ''')
            
            # Orders table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(user_id),
                    bookstore_id INTEGER REFERENCES bookstores(id),
                    order_number VARCHAR(50) UNIQUE NOT NULL,
                    total_amount FLOAT NOT NULL,
                    order_status VARCHAR(50) DEFAULT 'pending',
                    payment_status VARCHAR(50) DEFAULT 'unpaid',
                    payment_method VARCHAR(50),
                    shipping_address TEXT NOT NULL,
                    shipping_phone VARCHAR(50) NOT NULL,
                    shipping_name VARCHAR(255) NOT NULL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Order items table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS order_items (
                    id SERIAL PRIMARY KEY,
                    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
                    book_link_id INTEGER REFERENCES book_links(id),
                    book_id BIGINT NOT NULL,
                    book_title VARCHAR(500),
                    quantity INTEGER NOT NULL,
                    unit_price FLOAT NOT NULL,
                    subtotal FLOAT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for orders
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id)
            ''')
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_orders_bookstore_id ON orders(bookstore_id)
            ''')
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id)
            ''')
            
            print("Database tables created successfully")

# Global database instance
db = Database()

async def init_database():
    """Initialize database connection"""
    await db.connect()

async def get_db():
    """Get database connection"""
    return db.pool

async def import_books_from_csv(csv_path: str = "dataset/book_data.csv"):
    """Import books from CSV file into database"""
    import pandas as pd
    import os
    
    try:
        # Read CSV
        if not os.path.exists(csv_path):
            print(f"CSV file not found: {csv_path}")
            return False
        
        df = pd.read_csv(csv_path)
        print(f"Found {len(df)} books in CSV")
        
        # Drop duplicates based on product_id (keep first occurrence)
        df = df.drop_duplicates(subset=['product_id'], keep='first')
        print(f"After removing duplicates: {len(df)} unique books")
        
        # Get database connection
        pool = await get_db()
        async with pool.acquire() as conn:
            # Check existing books
            existing_count = await conn.fetchval('SELECT COUNT(*) FROM books')
            print(f"Existing books in database: {existing_count}")
            
            if existing_count > 0:
                print("Books already imported. Skipping import.")
                return True
            
            # Insert books
            inserted = 0
            for _, row in df.iterrows():
                try:
                    await conn.execute('''
                        INSERT INTO books (
                            product_id, title, authors, original_price, current_price,
                            quantity, category, n_review, avg_rating, pages,
                            manufacturer, cover_link
                        )
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                        ON CONFLICT (product_id) DO NOTHING
                    ''',
                        int(row['product_id']),
                        str(row['title']),
                        str(row['authors']) if pd.notna(row['authors']) else None,
                        float(row['original_price']) if pd.notna(row['original_price']) else None,
                        float(row['current_price']) if pd.notna(row['current_price']) else None,
                        int(row['quantity']) if pd.notna(row['quantity']) else 0,
                        str(row['category']) if pd.notna(row['category']) else None,
                        int(row['n_review']) if pd.notna(row['n_review']) else 0,
                        float(row['avg_rating']) if pd.notna(row['avg_rating']) else 0.0,
                        int(row['pages']) if pd.notna(row['pages']) else 0,
                        str(row['manufacturer']) if pd.notna(row['manufacturer']) else None,
                        str(row['cover_link']) if pd.notna(row['cover_link']) else None
                    )
                    inserted += 1
                except Exception as e:
                    print(f"Error inserting book {row.get('product_id', 'unknown')}: {e}")
            
            print(f"Successfully imported {inserted} books")
            return True
            
    except Exception as e:
        print(f"Error importing books from CSV: {e}")
        return False