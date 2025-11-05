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
                    book_id SERIAL PRIMARY KEY,
                    author_id INTEGER REFERENCES users(user_id),
                    title VARCHAR(500) NOT NULL,
                    category VARCHAR(100),
                    content TEXT NOT NULL,
                    emotional_layer VARCHAR(50),
                    prompt_used TEXT,
                    tags TEXT[],
                    is_published BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    views INTEGER DEFAULT 0,
                    likes INTEGER DEFAULT 0
                )
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
            
            print("Database tables created successfully")

# Global database instance
db = Database()

async def init_database():
    """Initialize database connection"""
    await db.connect()

async def get_db():
    """Get database connection"""
    return db.pool