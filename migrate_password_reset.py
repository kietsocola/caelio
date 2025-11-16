"""
Migration script to add password reset functionality
Creates password_reset_tokens table and adds role column to users table
"""

import asyncio
import asyncpg

async def migrate_database():
    """Run database migration for password reset"""
    
    # Connect to database
    conn = await asyncpg.connect(
        user='postgres',
        password='123',
        database='caelio_care',
        host='localhost',
        port=5432
    )
    
    try:
        print("Starting database migration for password reset...")
        print("=" * 60)
        
        # 1. Add role column to users table if not exists
        print("\n1. Adding 'role' column to users table...")
        try:
            await conn.execute('''
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='users' AND column_name='role'
                    ) THEN
                        ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT 'user';
                        RAISE NOTICE 'Column role added successfully';
                    ELSE
                        RAISE NOTICE 'Column role already exists';
                    END IF;
                END $$;
            ''')
            print("   ✓ Role column checked/added successfully")
        except Exception as e:
            print(f"   ✗ Error adding role column: {e}")
            raise
        
        # 2. Create password_reset_tokens table
        print("\n2. Creating password_reset_tokens table...")
        try:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS password_reset_tokens (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER UNIQUE REFERENCES users(user_id) ON DELETE CASCADE,
                    token VARCHAR(255) UNIQUE NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            print("   ✓ Table password_reset_tokens created successfully")
        except Exception as e:
            print(f"   ✗ Error creating table: {e}")
            raise
        
        # 3. Create indexes for password_reset_tokens
        print("\n3. Creating indexes...")
        try:
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_token 
                ON password_reset_tokens(token)
            ''')
            print("   ✓ Index on token created")
            
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_expires_at 
                ON password_reset_tokens(expires_at)
            ''')
            print("   ✓ Index on expires_at created")
            
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_user_id 
                ON password_reset_tokens(user_id)
            ''')
            print("   ✓ Index on user_id created")
        except Exception as e:
            print(f"   ✗ Error creating indexes: {e}")
            raise
        
        # 4. Verify tables exist
        print("\n4. Verifying migration...")
        
        # Check password_reset_tokens table
        table_exists = await conn.fetchval('''
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'password_reset_tokens'
            )
        ''')
        
        if table_exists:
            print("   ✓ password_reset_tokens table exists")
            
            # Get column info
            columns = await conn.fetch('''
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'password_reset_tokens'
                ORDER BY ordinal_position
            ''')
            
            print("\n   Table structure:")
            for col in columns:
                nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                print(f"     - {col['column_name']}: {col['data_type']} {nullable}")
        else:
            print("   ✗ password_reset_tokens table does NOT exist")
        
        # Check role column in users
        role_exists = await conn.fetchval('''
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'role'
            )
        ''')
        
        if role_exists:
            print("\n   ✓ role column exists in users table")
            
            # Get role column info
            role_info = await conn.fetchrow('''
                SELECT data_type, column_default, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'role'
            ''')
            print(f"     Type: {role_info['data_type']}")
            print(f"     Default: {role_info['column_default']}")
            print(f"     Nullable: {role_info['is_nullable']}")
        else:
            print("\n   ✗ role column does NOT exist in users table")
        
        # 5. Get indexes info
        print("\n5. Checking indexes...")
        indexes = await conn.fetch('''
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE tablename = 'password_reset_tokens'
        ''')
        
        for idx in indexes:
            print(f"   ✓ {idx['indexname']}")
        
        print("\n" + "=" * 60)
        print("✓ Migration completed successfully!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Install required packages: pip install aiosmtplib email-validator")
        print("2. Configure SMTP settings in caelio_care/auth.py")
        print("3. Run test: python test_password_reset.py")
        print("4. Start API: python run_api.py")
        
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await conn.close()
    
    return True

if __name__ == "__main__":
    success = asyncio.run(migrate_database())
    exit(0 if success else 1)
