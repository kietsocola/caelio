# Hướng dẫn Cấu hình Email cho Reset Password

## Cấu hình Gmail

### Bước 1: Tạo App Password cho Gmail

1. Đăng nhập vào tài khoản Google của bạn
2. Truy cập: https://myaccount.google.com/security
3. Bật **2-Step Verification** (xác minh 2 bước) nếu chưa bật
4. Sau khi bật 2-Step Verification, quay lại Security settings
5. Tìm và click vào **App passwords** (Mật khẩu ứng dụng)
6. Chọn app: **Mail**
7. Chọn device: **Other** và đặt tên "Caelio Care"
8. Click **Generate** - Google sẽ tạo ra mật khẩu 16 ký tự
9. **Lưu mật khẩu này lại** - bạn sẽ cần nó ở bước tiếp theo

### Bước 2: Cập nhật cấu hình trong auth.py

Mở file `caelio_care/auth.py` và cập nhật các biến sau (dòng 15-20):

```python
# Email configuration
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "your-email@gmail.com"  # ← Thay bằng email của bạn
SMTP_PASSWORD = "xxxx xxxx xxxx xxxx"   # ← Thay bằng App Password vừa tạo (16 ký tự)
SMTP_FROM_EMAIL = "your-email@gmail.com"  # ← Thay bằng email của bạn
SMTP_FROM_NAME = "Caelio Care"
```

**Ví dụ:**
```python
SMTP_USERNAME = "caeliocare@gmail.com"
SMTP_PASSWORD = "abcd efgh ijkl mnop"  # App Password từ Google
SMTP_FROM_EMAIL = "caeliocare@gmail.com"
```

### Bước 3: Cập nhật Reset Link Domain

Trong file `auth.py`, tìm function `send_reset_email()` và cập nhật domain:

```python
# Dòng ~170
reset_link = f"https://caelio-care.com/reset-password?token={token}"
# Thay "caelio-care.com" bằng domain thật của bạn
# Hoặc dùng localhost khi test: http://localhost:3000/reset-password?token={token}
```

### Bước 4: Cài đặt thư viện cần thiết

```bash
cd caelio_care
pip install -r requirements.txt
```

Hoặc cài đặt thủ công:
```bash
pip install aiosmtplib==3.0.1 email-validator==2.1.0
```

## Sử dụng Email Service khác

### Outlook/Hotmail

```python
SMTP_HOST = "smtp-mail.outlook.com"
SMTP_PORT = 587
SMTP_USERNAME = "your-email@outlook.com"
SMTP_PASSWORD = "your-password"
```

### Custom SMTP Server

```python
SMTP_HOST = "mail.yourdomain.com"
SMTP_PORT = 587  # hoặc 465 cho SSL
SMTP_USERNAME = "noreply@yourdomain.com"
SMTP_PASSWORD = "your-smtp-password"
```

## API Endpoints

### 1. Forgot Password (Quên mật khẩu)

```http
POST /auth/forgot-password
Content-Type: application/json

{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "message": "Nếu email tồn tại trong hệ thống, bạn sẽ nhận được email hướng dẫn đặt lại mật khẩu."
}
```

### 2. Reset Password (Đặt lại mật khẩu với token)

```http
POST /auth/reset-password
Content-Type: application/json

{
  "token": "token-from-email",
  "new_password": "newpassword123"
}
```

**Response:**
```json
{
  "message": "Mật khẩu đã được đặt lại thành công"
}
```

### 3. Change Password (Đổi mật khẩu khi đã đăng nhập)

```http
POST /auth/change-password
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "old_password": "oldpassword123",
  "new_password": "newpassword456"
}
```

**Response:**
```json
{
  "message": "Mật khẩu đã được thay đổi thành công"
}
```

## Flow hoàn chỉnh

### Flow Quên Mật Khẩu

1. **User**: Click "Quên mật khẩu" trên frontend
2. **Frontend**: Gọi `POST /auth/forgot-password` với email
3. **Backend**: 
   - Tạo token reset password
   - Lưu token vào database (expires sau 30 phút)
   - Gửi email chứa link reset password
4. **User**: Nhận email, click vào link reset password
5. **Frontend**: Hiển thị form nhập mật khẩu mới với token từ URL
6. **User**: Nhập mật khẩu mới
7. **Frontend**: Gọi `POST /auth/reset-password` với token và mật khẩu mới
8. **Backend**: 
   - Verify token (check expires)
   - Update mật khẩu mới
   - Delete token đã sử dụng
9. **User**: Đăng nhập với mật khẩu mới

### Flow Đổi Mật Khẩu (đã đăng nhập)

1. **User**: Vào "Cài đặt" → "Đổi mật khẩu"
2. **Frontend**: Hiển thị form nhập mật khẩu cũ và mới
3. **User**: Nhập mật khẩu cũ và mật khẩu mới
4. **Frontend**: Gọi `POST /auth/change-password` kèm access token
5. **Backend**: 
   - Verify mật khẩu cũ
   - Update mật khẩu mới
6. **User**: Tiếp tục sử dụng (không cần đăng nhập lại)

## Security Notes

1. **Token Expiration**: Token reset password hết hạn sau 30 phút
2. **One-time Use**: Token chỉ dùng được 1 lần, sau đó bị xóa
3. **Email Privacy**: API không tiết lộ email có tồn tại hay không
4. **Password Requirements**: Mật khẩu tối thiểu 6 ký tự (có thể tăng lên)
5. **Rate Limiting**: Nên implement rate limiting cho endpoint forgot-password

## Testing

### Test với cURL

```bash
# 1. Forgot Password
curl -X POST http://localhost:8001/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# 2. Reset Password (lấy token từ email)
curl -X POST http://localhost:8001/auth/reset-password \
  -H "Content-Type: application/json" \
  -d '{"token": "token-from-email", "new_password": "newpass123"}'

# 3. Change Password (cần access token)
curl -X POST http://localhost:8001/auth/change-password \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"old_password": "oldpass123", "new_password": "newpass456"}'
```

## Troubleshooting

### Email không gửi được

1. **Check credentials**: Đảm bảo email và app password đúng
2. **Check 2-Step Verification**: Phải bật 2-Step Verification trên Gmail
3. **Check firewall**: Port 587 có bị chặn không
4. **Check logs**: Xem error trong console khi gửi email
5. **Test SMTP**: Dùng tool như telnet để test kết nối SMTP

### Token không hợp lệ

1. **Check expiration**: Token có hết hạn chưa (30 phút)
2. **Check database**: Token có tồn tại trong bảng `password_reset_tokens`
3. **Already used**: Token đã được sử dụng và bị xóa

### Frontend Integration

File frontend mẫu (React):

```jsx
// ForgotPassword.jsx
const handleForgotPassword = async (email) => {
  const response = await fetch('http://localhost:8001/auth/forgot-password', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email })
  });
  const data = await response.json();
  alert(data.message);
};

// ResetPassword.jsx
const handleResetPassword = async (token, newPassword) => {
  const response = await fetch('http://localhost:8001/auth/reset-password', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token, new_password: newPassword })
  });
  const data = await response.json();
  if (response.ok) {
    alert('Đặt lại mật khẩu thành công!');
    // Redirect to login
  }
};

// ChangePassword.jsx
const handleChangePassword = async (oldPassword, newPassword) => {
  const response = await fetch('http://localhost:8001/auth/change-password', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accessToken}`
    },
    body: JSON.stringify({ 
      old_password: oldPassword, 
      new_password: newPassword 
    })
  });
  const data = await response.json();
  alert(data.message);
};
```

## Environment Variables (Khuyến nghị)

Thay vì hard-code trong code, nên dùng environment variables:

```python
# auth.py
import os

SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
SMTP_FROM_EMAIL = os.getenv('SMTP_FROM_EMAIL')
SMTP_FROM_NAME = os.getenv('SMTP_FROM_NAME', 'Caelio Care')
```

Tạo file `.env`:
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=Caelio Care
```
