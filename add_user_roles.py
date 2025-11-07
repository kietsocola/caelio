"""
Add role field to users table for simple role-based access control
"""

import asyncpg
import asyncio

async def add_user_roles():
    """Add role column to users table"""
    try:
        conn = await asyncpg.connect(
            user='postgres',
            password='123',
            database='caelio_care',
            host='localhost',
            port=5432
        )
        
        # Add role column if not exists
        await conn.execute('''
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS role VARCHAR(50) DEFAULT 'user'
        ''')
        
        # Add check constraint for valid roles
        await conn.execute('''
            DO $$ 
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint 
                    WHERE conname = 'users_role_check'
                ) THEN
                    ALTER TABLE users 
                    ADD CONSTRAINT users_role_check 
                    CHECK (role IN ('user', 'admin', 'bookstore'));
                END IF;
            END $$;
        ''')
        
        # Create index on role for faster queries
        await conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)
        ''')
        
        print("✅ User roles added successfully")
        print("   - user: Người dùng bình thường (mặc định)")
        print("   - admin: Quản trị viên")
        print("   - bookstore: Nhà sách")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error adding user roles: {e}")
        raise e

if __name__ == "__main__":
    asyncio.run(add_user_roles())
