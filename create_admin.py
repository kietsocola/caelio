"""
Create first admin user for Caelio Care system
"""

import asyncio
import asyncpg
import bcrypt
import sys

async def create_admin(email=None, username=None, password=None, full_name=None, force=False):
    """Create admin user"""
    try:
        conn = await asyncpg.connect(
            user='postgres',
            password='123',
            database='caelio_care',
            host='localhost',
            port=5432
        )
        
        # Check if admin already exists
        existing_admin = await conn.fetchval('''
            SELECT COUNT(*) FROM users WHERE role = 'admin'
        ''')
        
        if existing_admin > 0 and not force:
            print(f"⚠️ Already have {existing_admin} admin(s) in the system")
            print("Use --force to create anyway")
            await conn.close()
            return
        
        # Use defaults if not provided
        email = email or "admin@caelio.com"
        username = username or "admin"
        password = password or "admin123"
        full_name = full_name or "System Admin"
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create admin
        try:
            user_id = await conn.fetchval('''
                INSERT INTO users (email, username, password_hash, full_name, role)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING user_id
            ''', email, username, password_hash, full_name, 'admin')
            
            print(f"\n✅ Admin user created successfully!")
            print(f"   User ID: {user_id}")
            print(f"   Email: {email}")
            print(f"   Username: {username}")
            print(f"   Password: {password}")
            print(f"   Role: admin")
            print(f"\n⚠️ Please save these credentials securely!")
            
        except asyncpg.UniqueViolationError as e:
            if "email" in str(e):
                print(f"❌ Email '{email}' already exists")
            elif "username" in str(e):
                print(f"❌ Username '{username}' already exists")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error creating admin: {e}")
        raise e

if __name__ == "__main__":
    # Parse command line arguments
    force = "--force" in sys.argv
    
    # Default values
    email = "admin@caelio.com"
    username = "admin"
    password = "admin123"
    full_name = "System Admin"
    
    # Parse named arguments
    for arg in sys.argv[1:]:
        if arg.startswith("--email="):
            email = arg.split("=")[1]
        elif arg.startswith("--username="):
            username = arg.split("=")[1]
        elif arg.startswith("--password="):
            password = arg.split("=")[1]
        elif arg.startswith("--name="):
            full_name = arg.split("=")[1]
    
    asyncio.run(create_admin(email, username, password, full_name, force))
