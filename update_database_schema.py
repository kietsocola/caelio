"""
Script to update database schema for bookstore features
Adds new columns to book_links table and creates orders tables
"""

import asyncio
import asyncpg

async def update_database():
    """Update database schema"""
    try:
        # Connect to database
        conn = await asyncpg.connect(
            user='postgres',
            password='123',
            database='caelio_care',
            host='localhost',
            port=5432
        )
        
        print("📊 Connected to database")
        
        # Check if columns already exist
        print("\n🔍 Checking existing schema...")
        
        # Add columns to book_links if they don't exist
        print("\n📝 Updating book_links table...")
        
        # Add stock_quantity
        try:
            await conn.execute('''
                ALTER TABLE book_links 
                ADD COLUMN IF NOT EXISTS stock_quantity INTEGER DEFAULT 0
            ''')
            print("✅ Added stock_quantity column")
        except Exception as e:
            print(f"⚠️ stock_quantity: {e}")
        
        # Add sold_count
        try:
            await conn.execute('''
                ALTER TABLE book_links 
                ADD COLUMN IF NOT EXISTS sold_count INTEGER DEFAULT 0
            ''')
            print("✅ Added sold_count column")
        except Exception as e:
            print(f"⚠️ sold_count: {e}")
        
        # Add view_count
        try:
            await conn.execute('''
                ALTER TABLE book_links 
                ADD COLUMN IF NOT EXISTS view_count INTEGER DEFAULT 0
            ''')
            print("✅ Added view_count column")
        except Exception as e:
            print(f"⚠️ view_count: {e}")
        
        # Create orders table
        print("\n📝 Creating orders table...")
        try:
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
            print("✅ Created orders table")
        except Exception as e:
            print(f"⚠️ orders table: {e}")
        
        # Create order_items table
        print("\n📝 Creating order_items table...")
        try:
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
            print("✅ Created order_items table")
        except Exception as e:
            print(f"⚠️ order_items table: {e}")
        
        # Create indexes
        print("\n📝 Creating indexes...")
        try:
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id)
            ''')
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_orders_bookstore_id ON orders(bookstore_id)
            ''')
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id)
            ''')
            print("✅ Created indexes")
        except Exception as e:
            print(f"⚠️ indexes: {e}")
        
        # Verify schema
        print("\n🔍 Verifying schema...")
        columns = await conn.fetch('''
            SELECT column_name, data_type, column_default
            FROM information_schema.columns
            WHERE table_name = 'book_links'
            ORDER BY ordinal_position
        ''')
        
        print("\n📋 book_links columns:")
        for col in columns:
            print(f"   - {col['column_name']}: {col['data_type']} (default: {col['column_default']})")
        
        # Check orders table
        orders_exists = await conn.fetchval('''
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'orders'
            )
        ''')
        print(f"\n📋 orders table exists: {orders_exists}")
        
        order_items_exists = await conn.fetchval('''
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'order_items'
            )
        ''')
        print(f"📋 order_items table exists: {order_items_exists}")
        
        await conn.close()
        print("\n✅ Database schema updated successfully!")
        
    except Exception as e:
        print(f"\n❌ Error updating database: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(update_database())
