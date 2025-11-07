"""
Authentication system for Caelio Care
Simple JWT-based authentication
"""

import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional
import asyncpg
from pydantic import BaseModel, EmailStr

SECRET_KEY = "caelio-care-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    role: Optional[str] = "user"  # user, admin, bookstore

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    user_id: int
    email: str
    username: str
    full_name: Optional[str]
    role: str = "user"
    created_at: Optional[datetime]
    is_active: bool = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User

class AuthManager:
    def __init__(self, db_pool):
        self.db_pool = db_pool
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def create_access_token(self, user_id: int) -> str:
        """Create JWT access token"""
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {"user_id": user_id, "exp": expire}
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    def verify_token(self, token: str) -> Optional[int]:
        """Verify JWT token and return user_id"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("user_id")
            return user_id
        except jwt.PyJWTError:
            return None
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create new user"""
        password_hash = self.hash_password(user_data.password)
        
        # Validate role
        if user_data.role not in ['user', 'admin', 'bookstore']:
            raise ValueError("Invalid role. Must be 'user', 'admin', or 'bookstore'")
        
        async with self.db_pool.acquire() as conn:
            try:
                user_id = await conn.fetchval('''
                    INSERT INTO users (email, username, password_hash, full_name, role)
                    VALUES ($1, $2, $3, $4, $5)
                    RETURNING user_id
                ''', user_data.email, user_data.username, password_hash, user_data.full_name, user_data.role)
                
                return User(
                    user_id=user_id,
                    email=user_data.email,
                    username=user_data.username,
                    full_name=user_data.full_name,
                    role=user_data.role,
                    created_at=datetime.now()
                )
            except asyncpg.UniqueViolationError as e:
                if "email" in str(e):
                    raise ValueError("Email already registered")
                elif "username" in str(e):
                    raise ValueError("Username already taken")
                else:
                    raise ValueError("User creation failed")
    
    async def authenticate_user(self, login_data: UserLogin) -> Optional[User]:
        """Authenticate user and return user object"""
        async with self.db_pool.acquire() as conn:
            user_row = await conn.fetchrow('''
                SELECT user_id, email, username, password_hash, full_name, role, created_at, is_active
                FROM users WHERE email = $1
            ''', login_data.email)
            
            if user_row and self.verify_password(login_data.password, user_row['password_hash']):
                return User(
                    user_id=user_row['user_id'],
                    email=user_row['email'],
                    username=user_row['username'],
                    full_name=user_row['full_name'],
                    role=user_row['role'],
                    created_at=user_row['created_at'],
                    is_active=user_row['is_active']
                )
        return None
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        async with self.db_pool.acquire() as conn:
            user_row = await conn.fetchrow('''
                SELECT user_id, email, username, full_name, role, created_at, is_active
                FROM users WHERE user_id = $1
            ''', user_id)
            
            if user_row:
                return User(
                    user_id=user_row['user_id'],
                    email=user_row['email'],
                    username=user_row['username'],
                    full_name=user_row['full_name'],
                    role=user_row['role'],
                    created_at=user_row['created_at'],
                    is_active=user_row['is_active']
                )
        return None