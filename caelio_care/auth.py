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
import secrets
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SECRET_KEY = "caelio-care-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours
RESET_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes for password reset

# Email configuration - Update these with your SMTP settings
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "vankiet27012004@gmail.com"  # Change this
SMTP_PASSWORD = "pxoo wdhb dzdn aith"  # Change this - use App Password for Gmail
SMTP_FROM_EMAIL = "manager@caelio.com"  # Change this
SMTP_FROM_NAME = "Caelio System"

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

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

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
    
    def generate_reset_token(self) -> str:
        """Generate secure random token for password reset"""
        return secrets.token_urlsafe(32)
    
    async def create_reset_token(self, email: str) -> Optional[str]:
        """Create password reset token for user"""
        async with self.db_pool.acquire() as conn:
            # Check if user exists
            user = await conn.fetchrow('SELECT user_id, email, username FROM users WHERE email = $1', email)
            if not user:
                return None
            
            # Generate token
            token = self.generate_reset_token()
            expires_at = datetime.utcnow() + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
            
            # Store token in database
            await conn.execute('''
                INSERT INTO password_reset_tokens (user_id, token, expires_at)
                VALUES ($1, $2, $3)
                ON CONFLICT (user_id) 
                DO UPDATE SET token = $2, expires_at = $3, created_at = CURRENT_TIMESTAMP
            ''', user['user_id'], token, expires_at)
            
            return token
    
    async def verify_reset_token(self, token: str) -> Optional[int]:
        """Verify reset token and return user_id if valid"""
        async with self.db_pool.acquire() as conn:
            result = await conn.fetchrow('''
                SELECT user_id, expires_at 
                FROM password_reset_tokens 
                WHERE token = $1
            ''', token)
            
            if not result:
                return None
            
            # Check if token expired
            if datetime.utcnow() > result['expires_at']:
                # Delete expired token
                await conn.execute('DELETE FROM password_reset_tokens WHERE token = $1', token)
                return None
            
            return result['user_id']
    
    async def reset_password(self, token: str, new_password: str) -> bool:
        """Reset password using valid token"""
        user_id = await self.verify_reset_token(token)
        if not user_id:
            return False
        
        # Hash new password
        password_hash = self.hash_password(new_password)
        
        async with self.db_pool.acquire() as conn:
            # Update password
            await conn.execute(
                'UPDATE users SET password_hash = $1 WHERE user_id = $2',
                password_hash, user_id
            )
            
            # Delete used token
            await conn.execute('DELETE FROM password_reset_tokens WHERE user_id = $1', user_id)
        
        return True
    
    async def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """Change password for authenticated user"""
        async with self.db_pool.acquire() as conn:
            user_row = await conn.fetchrow(
                'SELECT password_hash FROM users WHERE user_id = $1',
                user_id
            )
            
            if not user_row:
                return False
            
            # Verify old password
            if not self.verify_password(old_password, user_row['password_hash']):
                return False
            
            # Hash and update new password
            password_hash = self.hash_password(new_password)
            await conn.execute(
                'UPDATE users SET password_hash = $1 WHERE user_id = $2',
                password_hash, user_id
            )
        
        return True
    
    async def send_reset_email(self, email: str, token: str, username: str) -> bool:
        """Send password reset email"""
        try:
            # Create reset link (update with your actual domain)
            reset_link = f"https://caelio.tech/reset-password?token={token}"
            
            # Create email message
            message = MIMEMultipart('alternative')
            message['Subject'] = 'Đặt lại mật khẩu Caelio Care'
            message['From'] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
            message['To'] = email
            
            # Email body
            text = f"""
            Xin chào {username},
            
            Bạn đã yêu cầu đặt lại mật khẩu cho tài khoản Caelio Care của mình.
            
            Vui lòng nhấp vào liên kết sau để đặt lại mật khẩu:
            {reset_link}
            
            Link này sẽ hết hạn sau {RESET_TOKEN_EXPIRE_MINUTES} phút.
            
            Nếu bạn không yêu cầu đặt lại mật khẩu, vui lòng bỏ qua email này.
            
            Trân trọng,
            Đội ngũ Caelio Care
            """
            
            html = f"""
            <html>
              <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                  <h2 style="color: #4A90E2;">Đặt lại mật khẩu Caelio Care</h2>
                  <p>Xin chào <strong>{username}</strong>,</p>
                  <p>Bạn đã yêu cầu đặt lại mật khẩu cho tài khoản Caelio Care của mình.</p>
                  <p>Vui lòng nhấp vào nút bên dưới để đặt lại mật khẩu:</p>
                  <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_link}" 
                       style="background-color: #4A90E2; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                      Đặt lại mật khẩu
                    </a>
                  </div>
                  <p style="color: #666; font-size: 14px;">
                    Link này sẽ hết hạn sau <strong>{RESET_TOKEN_EXPIRE_MINUTES} phút</strong>.
                  </p>
                  <p style="color: #666; font-size: 14px;">
                    Nếu bạn không yêu cầu đặt lại mật khẩu, vui lòng bỏ qua email này.
                  </p>
                  <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                  <p style="color: #999; font-size: 12px;">
                    Trân trọng,<br>
                    Đội ngũ Caelio Care
                  </p>
                </div>
              </body>
            </html>
            """
            
            part1 = MIMEText(text, 'plain')
            part2 = MIMEText(html, 'html')
            message.attach(part1)
            message.attach(part2)
            
            # Send email
            await aiosmtplib.send(
                message,
                hostname=SMTP_HOST,
                port=SMTP_PORT,
                username=SMTP_USERNAME,
                password=SMTP_PASSWORD,
                start_tls=True
            )
            
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False