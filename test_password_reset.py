"""
Test script for password reset functionality
"""

import asyncio
import asyncpg
from datetime import datetime, timedelta

async def test_password_reset():
    """Test password reset token creation and verification"""
    
    # Connect to database
    conn = await asyncpg.connect(
        user='postgres',
        password='123',
        database='caelio_care',
        host='localhost',
        port=5432
    )
    
    try:
        print("Testing Password Reset Functionality...")
        print("-" * 50)
        
        # 1. Create test user if not exists
        print("\n1. Creating test user...")
        try:
            user_id = await conn.fetchval('''
                INSERT INTO users (email, username, password_hash, full_name, role)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING user_id
            ''', 'test@example.com', 'testuser', 'dummy_hash', 'Test User', 'user')
            print(f"   ✓ User created with ID: {user_id}")
        except asyncpg.UniqueViolationError:
            user_id = await conn.fetchval(
                "SELECT user_id FROM users WHERE email = $1",
                'test@example.com'
            )
            print(f"   ✓ User already exists with ID: {user_id}")
        
        # 2. Create reset token
        print("\n2. Creating reset token...")
        token = "test_token_123456789"
        expires_at = datetime.utcnow() + timedelta(minutes=30)
        
        await conn.execute('''
            INSERT INTO password_reset_tokens (user_id, token, expires_at)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id) 
            DO UPDATE SET token = $2, expires_at = $3, created_at = CURRENT_TIMESTAMP
        ''', user_id, token, expires_at)
        print(f"   ✓ Token created: {token}")
        print(f"   ✓ Expires at: {expires_at}")
        
        # 3. Verify token
        print("\n3. Verifying token...")
        result = await conn.fetchrow('''
            SELECT user_id, expires_at 
            FROM password_reset_tokens 
            WHERE token = $1
        ''', token)
        
        if result:
            print(f"   ✓ Token found for user_id: {result['user_id']}")
            print(f"   ✓ Token expires at: {result['expires_at']}")
            
            if datetime.utcnow() < result['expires_at']:
                print("   ✓ Token is still valid")
            else:
                print("   ✗ Token has expired")
        else:
            print("   ✗ Token not found")
        
        # 4. Check table structure
        print("\n4. Checking password_reset_tokens table structure...")
        columns = await conn.fetch('''
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'password_reset_tokens'
        ''')
        for col in columns:
            print(f"   - {col['column_name']}: {col['data_type']}")
        
        # 5. Check users table has role column
        print("\n5. Checking users table structure...")
        user_columns = await conn.fetch('''
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'users'
        ''')
        has_role = any(col['column_name'] == 'role' for col in user_columns)
        if has_role:
            print("   ✓ 'role' column exists in users table")
        else:
            print("   ✗ 'role' column NOT found in users table")
        
        # 6. Test expired token cleanup
        print("\n6. Testing expired token cleanup...")
        expired_token = "expired_token_987654321"
        expired_at = datetime.utcnow() - timedelta(minutes=1)  # Already expired
        
        await conn.execute('''
            INSERT INTO password_reset_tokens (user_id, token, expires_at)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id) 
            DO UPDATE SET token = $2, expires_at = $3
        ''', user_id, expired_token, expired_at)
        
        result = await conn.fetchrow('''
            SELECT user_id, expires_at 
            FROM password_reset_tokens 
            WHERE token = $1
        ''', expired_token)
        
        if result and datetime.utcnow() > result['expires_at']:
            print("   ✓ Expired token detected")
            await conn.execute('DELETE FROM password_reset_tokens WHERE token = $1', expired_token)
            print("   ✓ Expired token deleted")
        
        print("\n" + "=" * 50)
        print("✓ All tests completed successfully!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(test_password_reset())
