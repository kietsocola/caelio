# ✅ HOÀN THÀNH: Hệ thống phân quyền đơn giản

## Tóm tắt

Đã implement thành công hệ thống phân quyền đơn giản với 3 vai trò:
- **user**: Người dùng bình thường (mặc định)
- **admin**: Quản trị viên
- **bookstore**: Nhà sách

## Files đã tạo/sửa

### 1. Migration Scripts
- ✅ `add_user_roles.py` - Thêm cột `role` vào bảng `users`
- ✅ `create_admin.py` - Script tạo admin user đầu tiên

### 2. Core Files
- ✅ `caelio_care/auth.py` - Cập nhật models (User, UserCreate) với field `role`
- ✅ `caelio_care/main.py` - Thêm dependencies phân quyền và endpoints admin

### 3. Documentation & Testing
- ✅ `RBAC_GUIDE.md` - Hướng dẫn chi tiết về phân quyền
- ✅ `test_rbac.py` - Script test tự động phân quyền

## Thay đổi chính

### Database Schema
```sql
ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT 'user';
ALTER TABLE users ADD CONSTRAINT users_role_check 
  CHECK (role IN ('user', 'admin', 'bookstore'));
CREATE INDEX idx_users_role ON users(role);
```

### Models (auth.py)
```python
class User(BaseModel):
    user_id: int
    email: str
    username: str
    full_name: Optional[str]
    role: str = "user"  # NEW
    created_at: Optional[datetime]
    is_active: bool = True

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    role: Optional[str] = "user"  # NEW
```

### Dependencies (main.py)
```python
async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin role"""
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

async def require_bookstore(current_user: User = Depends(get_current_user)) -> User:
    """Require bookstore role"""
    if current_user.role != 'bookstore':
        raise HTTPException(status_code=403, detail="Bookstore access required")
    return current_user

async def require_admin_or_bookstore(current_user: User = Depends(get_current_user)) -> User:
    """Require admin or bookstore role"""
    if current_user.role not in ['admin', 'bookstore']:
        raise HTTPException(status_code=403, detail="Admin or Bookstore access required")
    return current_user
```

### New Admin Endpoints
```python
GET  /care/admin/users                      # Danh sách users (admin only)
GET  /care/admin/users?role=bookstore       # Lọc theo role (admin only)
PUT  /care/admin/users/{user_id}/role       # Thay đổi role (admin only)
PUT  /care/admin/users/{user_id}/activate   # Activate/deactivate (admin only)
```

### Protected Endpoints
```python
# Admin hoặc Bookstore
PUT  /care/orders/{order_id}/status                # Cập nhật trạng thái đơn hàng
GET  /care/bookstores/{bookstore_id}/orders        # Xem đơn hàng nhà sách
GET  /care/bookstores/{bookstore_id}/statistics    # Xem thống kê nhà sách
```

## Cách sử dụng

### 1. Tạo admin đầu tiên
```bash
python create_admin.py

# Hoặc với custom info
python create_admin.py --email=myemail@test.com --username=myadmin --password=secret123
```

### 2. Test phân quyền
```bash
python test_rbac.py
```

### 3. API Examples

**Đăng ký user bình thường:**
```bash
POST /care/auth/register
{
  "email": "user@example.com",
  "username": "normaluser",
  "password": "password123"
}
```

**Đăng ký bookstore:**
```bash
POST /care/auth/register
{
  "email": "bookstore@example.com",
  "username": "mybookstore",
  "password": "password123",
  "role": "bookstore"
}
```

**Admin quản lý users:**
```bash
# Lấy danh sách users
GET /care/admin/users?page=1&page_size=50
Authorization: Bearer <admin_token>

# Thay đổi role
PUT /care/admin/users/123/role?new_role=bookstore
Authorization: Bearer <admin_token>

# Deactivate user
PUT /care/admin/users/123/activate?is_active=false
Authorization: Bearer <admin_token>
```

## Quyền hạn chi tiết

### User (Người dùng bình thường)
✅ Làm bài test  
✅ Tạo/sửa/xóa White Books của mình  
✅ Tạo đơn hàng  
✅ Xem đơn hàng của mình  
❌ Quản lý users  
❌ Xem thống kê nhà sách  

### Admin (Quản trị viên)
✅ Tất cả quyền của User  
✅ Quản lý tất cả users (xem, đổi role, activate/deactivate)  
✅ Xem/cập nhật đơn hàng của tất cả nhà sách  
✅ Xem thống kê của tất cả nhà sách  

### Bookstore (Nhà sách)
✅ Tất cả quyền của User  
✅ Thêm link mua sách  
✅ Xem đơn hàng của nhà sách mình  
✅ Cập nhật trạng thái đơn hàng  
✅ Xem thống kê nhà sách mình  
❌ Quản lý users  
❌ Xem thống kê nhà sách khác  

## Response Codes

### 401 Unauthorized
Chưa đăng nhập hoặc token không hợp lệ
```json
{
  "detail": "Invalid authentication credentials"
}
```

### 403 Forbidden
Đã đăng nhập nhưng không đủ quyền
```json
{
  "detail": "Admin access required"
}
```

## Admin mặc định đã tạo

```
Email: admin@caelio.com
Username: admin
Password: admin123
Role: admin
```

⚠️ **LƯU Ý**: Nên đổi mật khẩu admin này sau khi deploy production!

## Testing Results

Chạy `python test_rbac.py` để kiểm tra:

✅ Admin có thể xem tất cả users  
✅ Normal user bị chặn khi truy cập admin endpoints  
✅ Bookstore có thể xem thống kê của mình  
✅ Admin có thể thay đổi role của users  
✅ Public endpoints hoạt động không cần authentication  

## Lưu ý bảo mật

1. ✅ Mật khẩu được hash bằng bcrypt
2. ✅ JWT token expires sau 24 giờ
3. ⚠️ Cần đổi SECRET_KEY trong production (file `auth.py`)
4. ⚠️ Nên dùng HTTPS trong production
5. ⚠️ Nên thêm rate limiting cho các API quan trọng

## Next Steps (Optional)

- [ ] Thêm audit log cho các thao tác admin
- [ ] Implement refresh token
- [ ] Thêm permission chi tiết hơn (CRUD permissions)
- [ ] Rate limiting
- [ ] Password reset flow
- [ ] Email verification
