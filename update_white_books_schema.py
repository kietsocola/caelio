"""
Script to update white_books schema to support chapters
"""

import asyncio
import asyncpg

async def update_schema():
    """Update white books schema"""
    try:
        # Connect to database
        conn = await asyncpg.connect(
            user='postgres',
            password='123',
            database='caelio_care',
            host='localhost',
            port=5432
        )
        
        print("Connected to database")
        
        # Start transaction
        async with conn.transaction():
            # Drop old white_books table if exists (backup data first if needed)
            print("\n⚠️  Checking existing white_books table...")
            existing_books = await conn.fetch('SELECT COUNT(*) FROM white_books')
            book_count = existing_books[0]['count']
            print(f"Found {book_count} existing white books")
            
            if book_count > 0:
                print("⚠️  WARNING: Existing data will be lost!")
                print("Creating backup...")
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS white_books_backup AS 
                    SELECT * FROM white_books
                ''')
                print("✅ Backup created in white_books_backup table")
            
            # Drop old table
            print("\n🔄 Dropping old white_books table...")
            await conn.execute('DROP TABLE IF EXISTS white_books CASCADE')
            
            # Create new white_books table
            print("📝 Creating new white_books table...")
            await conn.execute('''
                CREATE TABLE white_books (
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
            print("✅ Created white_books table")
            
            # Create white_book_chapters table
            print("📝 Creating white_book_chapters table...")
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
            print("✅ Created white_book_chapters table")
            
            # Create white_book_likes table
            print("📝 Creating white_book_likes table...")
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS white_book_likes (
                    book_id INTEGER REFERENCES white_books(id) ON DELETE CASCADE,
                    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (book_id, user_id)
                )
            ''')
            print("✅ Created white_book_likes table")
            
            # Create indexes
            print("📝 Creating indexes...")
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
            print("✅ Created indexes")
        
        print("\n✅ Schema update completed successfully!")
        print("\n📊 Summary:")
        print(f"   - Old white_books backed up: {book_count} books")
        print("   - New tables created: white_books, white_book_chapters")
        print("   - Indexes created for better performance")
        
        await conn.close()
        
    except Exception as e:
        print(f"\n❌ Error updating schema: {e}")
        raise e

if __name__ == "__main__":
    print("🚀 Starting White Books Schema Update...")
    print("=" * 60)
    asyncio.run(update_schema())
    print("=" * 60)
    print("✅ Done!")
