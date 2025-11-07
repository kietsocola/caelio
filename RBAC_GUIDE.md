# Role-Based Access Control (RBAC) - Caelio Care API

## Tổng quan

Hệ thống phân quyền đơn giản với 3 vai trò (roles):

- **user**: Người dùng bình thường (mặc định)
- **admin**: Quản trị viên hệ thống
- **bookstore**: Nhà sách

## Chi tiết vai trò

### 1. User (Người dùng bình thường)
**Quyền hạn:**
- ✅ Đăng ký, đăng nhập
- ✅ Làm bài test tính cách và cảm xúc
- ✅ Xem lịch sử bài test của mình
- ✅ Tạo, chỉnh sửa, xóa White Books của mình
- ✅ Thêm/xóa chương cho White Books của mình
- ✅ Publish/unpublish White Books
- ✅ Like, view White Books
- ✅ Tìm kiếm sách
- ✅ Tạo đơn hàng
- ✅ Xem đơn hàng của mình
- ✅ Hủy đơn hàng (nếu còn pending/confirmed)

**Không có quyền:**
- ❌ Quản lý người dùng khác
- ❌ Cập nhật trạng thái đơn hàng
- ❌ Xem thống kê nhà sách
- ❌ Xem đơn hàng của nhà sách

### 2. Admin (Quản trị viên)
**Quyền hạn:**
- ✅ Tất cả quyền của User
- ✅ Xem danh sách tất cả users
- ✅ Thay đổi role của users
- ✅ Activate/deactivate users
- ✅ Cập nhật trạng thái đơn hàng
- ✅ Xem đơn hàng của tất cả nhà sách
- ✅ Xem thống kê của tất cả nhà sách

### 3. Bookstore (Nhà sách)
**Quyền hạn:**
- ✅ Tất cả quyền của User
- ✅ Đăng ký thông tin nhà sách
- ✅ Thêm link mua sách
- ✅ Xem đơn hàng của nhà sách mình
- ✅ Cập nhật trạng thái đơn hàng
- ✅ Xem thống kê nhà sách mình

**Không có quyền:**
- ❌ Quản lý users
- ❌ Xem đơn hàng/thống kê của nhà sách khác

## API Endpoints với phân quyền

### Authentication (Không cần đăng nhập)
```
POST /care/auth/register       # Đăng ký (role mặc định: user)
POST /care/auth/login          # Đăng nhập
```

### User endpoints (Cần đăng nhập - bất kỳ role nào)
```
GET  /care/auth/me                          # Thông tin user hiện tại
POST /care/emotional-test/analyze           # Làm bài test cảm xúc
GET  /care/emotional-test/my-results        # Lịch sử bài test
POST /care/white-books/create               # Tạo White Book
GET  /care/white-books/my-books             # White Books của mình
PUT  /care/white-books/{book_id}            # Sửa White Book
DELETE /care/white-books/{book_id}          # Xóa White Book
POST /care/white-books/{book_id}/chapters   # Thêm chương
POST /care/orders/create                    # Tạo đơn hàng
GET  /care/orders/my-orders                 # Đơn hàng của mình
PUT  /care/orders/{order_id}/cancel         # Hủy đơn hàng
```

### Admin-only endpoints (Chỉ admin)
```
GET  /care/admin/users                      # Danh sách users
PUT  /care/admin/users/{user_id}/role       # Thay đổi role
PUT  /care/admin/users/{user_id}/activate   # Activate/deactivate user
```

### Admin hoặc Bookstore endpoints
```
PUT  /care/orders/{order_id}/status                # Cập nhật trạng thái đơn hàng
GET  /care/bookstores/{bookstore_id}/orders        # Đơn hàng của nhà sách
GET  /care/bookstores/{bookstore_id}/statistics    # Thống kê nhà sách
```

### Public endpoints (Không cần đăng nhập)
```
GET  /care/                                 # API info
GET  /care/health                          # Health check
GET  /care/emotional-test/questions        # Câu hỏi test
GET  /care/white-books/published           # White Books đã publish
GET  /care/white-books/{book_id}           # Chi tiết White Book
GET  /care/books/{book_id}                 # Thông tin sách
GET  /care/books/search/{query}            # Tìm kiếm sách
GET  /care/bookstores                      # Danh sách nhà sách
```

## Đăng ký với role cụ thể

### Đăng ký user bình thường (mặc định)
```json
POST /care/auth/register
{
  "email": "user@example.com",
  "username": "normaluser",
  "password": "password123",
  "full_name": "Nguyễn Văn A"
}
```

### Đăng ký với role admin (chỉ admin có thể tạo admin khác)
```json
POST /care/auth/register
{
  "email": "admin@example.com",
  "username": "adminuser",
  "password": "password123",
  "full_name": "Admin User",
  "role": "admin"
}
```

### Đăng ký với role bookstore
```json
POST /care/auth/register
{
  "email": "bookstore@example.com",
  "username": "mybookstore",
  "password": "password123",
  "full_name": "Nhà sách ABC",
  "role": "bookstore"
}
```

## Response khi thiếu quyền

### 401 Unauthorized (Chưa đăng nhập)
```json
{
  "detail": "Invalid authentication credentials"
}
```

### 403 Forbidden (Không đủ quyền)
```json
{
  "detail": "Admin access required"
}
```
hoặc
```json
{
  "detail": "Admin or Bookstore access required"
}
```

## Ví dụ sử dụng

### 1. Admin quản lý users

```bash
# Lấy danh sách tất cả users
GET /care/admin/users?page=1&page_size=50
Authorization: Bearer <admin_token>

# Lọc theo role
GET /care/admin/users?role=bookstore
Authorization: Bearer <admin_token>

# Thay đổi role của user
PUT /care/admin/users/123/role
Authorization: Bearer <admin_token>
{
  "new_role": "bookstore"
}

# Deactivate user
PUT /care/admin/users/123/activate
Authorization: Bearer <admin_token>
{
  "is_active": false
}
```

### 2. Bookstore quản lý đơn hàng

```bash
# Xem đơn hàng của nhà sách
GET /care/bookstores/1/orders?page=1&page_size=50
Authorization: Bearer <bookstore_token>

# Cập nhật trạng thái đơn hàng
PUT /care/orders/456/status
Authorization: Bearer <bookstore_token>
{
  "order_status": "shipping",
  "payment_status": "paid"
}

# Xem thống kê
GET /care/bookstores/1/statistics
Authorization: Bearer <bookstore_token>
```