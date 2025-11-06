# 📚 Bookstore & Order Management API Documentation

## Base URL
```
http://localhost:8000/care
```

---

## 🏪 Bookstore APIs

### 1. Đăng ký nhà sách
**POST** `/bookstores/register`

Đăng ký nhà sách mới vào hệ thống.

**Request Body:**
```json
{
  "name": "Nhà Sách Fahasa",
  "email": "fahasa@example.com",
  "phone": "1900636467",
  "address": "60-62 Lê Lợi, Quận 1, TP.HCM",
  "latitude": 10.7720,
  "longitude": 106.6972,
  "commission_rate": 15.5,
  "description": "Chuỗi nhà sách lớn nhất Việt Nam",
  "website": "https://www.fahasa.com"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Nhà Sách Fahasa",
  "email": "fahasa@example.com",
  "phone": "1900636467",
  "address": "60-62 Lê Lợi, Quận 1, TP.HCM",
  "latitude": 10.7720,
  "longitude": 106.6972,
  "commission_rate": 15.5,
  "description": "Chuỗi nhà sách lớn nhất Việt Nam",
  "website": "https://www.fahasa.com",
  "is_active": true,
  "created_at": "2025-11-06T10:30:00"
}
```

---

### 2. Lấy danh sách nhà sách
**GET** `/bookstores?active_only=true`

Lấy danh sách tất cả nhà sách.

**Query Parameters:**
- `active_only` (boolean, optional): Chỉ lấy nhà sách đang hoạt động. Default: `true`

**Response:**
```json
[
  {
    "id": 1,
    "name": "Nhà Sách Fahasa",
    "email": "fahasa@example.com",
    "phone": "1900636467",
    "address": "60-62 Lê Lợi, Quận 1, TP.HCM",
    "latitude": 10.7720,
    "longitude": 106.6972,
    "commission_rate": 15.5,
    "description": "Chuỗi nhà sách lớn nhất Việt Nam",
    "website": "https://www.fahasa.com",
    "is_active": true,
    "created_at": "2025-11-06T10:30:00"
  }
]
```

---

### 3. Chi tiết nhà sách
**GET** `/bookstores/{bookstore_id}`

Lấy thông tin chi tiết một nhà sách.

**Response:**
```json
{
  "id": 1,
  "name": "Nhà Sách Fahasa",
  "email": "fahasa@example.com",
  "phone": "1900636467",
  "address": "60-62 Lê Lợi, Quận 1, TP.HCM",
  "latitude": 10.7720,
  "longitude": 106.6972,
  "commission_rate": 15.5,
  "description": "Chuỗi nhà sách lớn nhất Việt Nam",
  "website": "https://www.fahasa.com",
  "is_active": true,
  "created_at": "2025-11-06T10:30:00"
}
```

---

### 4. Thống kê nhà sách
**GET** `/bookstores/{bookstore_id}/statistics`

Lấy thống kê chi tiết của nhà sách (doanh thu, lượt xem, sách bán chạy).

**Response:**
```json
{
  "total_orders": 150,
  "total_revenue": 45500000,
  "total_books_sold": 320,
  "total_views": 5420,
  "order_status_breakdown": [
    {
      "order_status": "delivered",
      "count": 120
    },
    {
      "order_status": "processing",
      "count": 20
    },
    {
      "order_status": "pending",
      "count": 10
    }
  ],
  "top_selling_books": [
    {
      "book_id": 74021317,
      "title": "Cây Cam Ngọt Của Tôi",
      "authors": "José Mauro de Vasconcelos",
      "total_sold": 45,
      "total_revenue": 2916000
    }
  ]
}
```

---

### 5. Lấy đơn hàng của nhà sách
**GET** `/bookstores/{bookstore_id}/orders?page=1&page_size=50`

Lấy danh sách đơn hàng của nhà sách (dành cho quản lý nhà sách).

**Query Parameters:**
- `page` (integer, optional): Trang hiện tại. Default: `1`
- `page_size` (integer, optional): Số đơn hàng mỗi trang. Default: `50`

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 5,
    "bookstore_id": 1,
    "order_number": "ORD20251106ABC12345",
    "total_amount": 194800,
    "order_status": "processing",
    "payment_status": "paid",
    "payment_method": "credit_card",
    "shipping_address": "123 Nguyễn Văn Linh, Quận 7, TP.HCM",
    "shipping_phone": "0901234567",
    "shipping_name": "Nguyễn Văn A",
    "notes": null,
    "created_at": "2025-11-06T14:30:00",
    "updated_at": "2025-11-06T14:35:00",
    "items": [
      {
        "id": 1,
        "order_id": 1,
        "book_link_id": 10,
        "book_id": 74021317,
        "book_title": "Cây Cam Ngọt Của Tôi",
        "quantity": 3,
        "unit_price": 64800,
        "subtotal": 194400,
        "created_at": "2025-11-06T14:30:00"
      }
    ]
  }
]
```

---

## 📖 Book & Book Link APIs

### 6. Tìm kiếm sách
**GET** `/books/search/{query}?limit=20`

Tìm kiếm sách theo tên, tác giả hoặc thể loại.

**Path Parameters:**
- `query` (string, required): Từ khóa tìm kiếm

**Query Parameters:**
- `limit` (integer, optional): Số kết quả tối đa. Default: `20`

**Response:**
```json
{
  "query": "Cây Cam",
  "total": 1,
  "books": [
    {
      "product_id": 74021317,
      "title": "Cây Cam Ngọt Của Tôi",
      "authors": "José Mauro de Vasconcelos",
      "original_price": 108000,
      "current_price": 64800,
      "quantity": 53075,
      "category": "Tiểu Thuyết",
      "n_review": 11481,
      "avg_rating": 5.0,
      "pages": 244,
      "manufacturer": "Nhà Xuất Bản Hội Nhà Văn",
      "cover_link": "https://salt.tikicdn.com/ts/product/5e/18/24/2a6154ba08df6ce6161c13f4303fa19e.jpg",
      "created_at": "2025-11-06T10:00:00"
    }
  ]
}
```

---

### 7. Chi tiết sách
**GET** `/books/{book_id}`

Lấy thông tin chi tiết một cuốn sách.

**Path Parameters:**
- `book_id` (integer, required): Product ID của sách (từ CSV)

**Response:**
```json
{
  "product_id": 74021317,
  "title": "Cây Cam Ngọt Của Tôi",
  "authors": "José Mauro de Vasconcelos",
  "original_price": 108000,
  "current_price": 64800,
  "quantity": 53075,
  "category": "Tiểu Thuyết",
  "n_review": 11481,
  "avg_rating": 5.0,
  "pages": 244,
  "manufacturer": "Nhà Xuất Bản Hội Nhà Văn",
  "cover_link": "https://salt.tikicdn.com/ts/product/5e/18/24/2a6154ba08df6ce6161c13f4303fa19e.jpg",
  "created_at": "2025-11-06T10:00:00"
}
```

---

### 8. Thêm/Cập nhật link mua sách
**POST** `/bookstores/book-links`

Nhà sách thêm link bán sách của mình.

**Request Body:**
```json
{
  "book_id": 74021317,
  "bookstore_id": 1,
  "purchase_url": "https://www.fahasa.com/products/74021317",
  "price": 64800,
  "stock_quantity": 100,
  "stock_status": "available"
}
```

**Response:**
```json
{
  "id": 10,
  "book_id": 74021317,
  "bookstore_id": 1,
  "purchase_url": "https://www.fahasa.com/products/74021317",
  "price": 64800,
  "stock_quantity": 100,
  "sold_count": 0,
  "view_count": 0,
  "stock_status": "available",
  "created_at": "2025-11-06T11:00:00"
}
```

---

### 9. Lấy link mua sách (có ưu tiên)
**GET** `/books/{book_id}/purchase-links?user_latitude=10.7723&user_longitude=106.6975`

Lấy danh sách link mua sách, được sắp xếp theo:
1. Khoảng cách gần user nhất (nếu có GPS)
2. % hoa hồng cao nhất

**Path Parameters:**
- `book_id` (integer, required): Product ID của sách

**Query Parameters:**
- `user_latitude` (float, optional): Vĩ độ GPS của user
- `user_longitude` (float, optional): Kinh độ GPS của user

**Response:**
```json
{
  "book_id": 74021317,
  "total_links": 2,
  "sorted_by": "distance and commission_rate",
  "purchase_links": [
    {
      "id": 10,
      "book_id": 74021317,
      "purchase_url": "https://www.fahasa.com/products/74021317",
      "price": 64800,
      "stock_quantity": 100,
      "sold_count": 15,
      "view_count": 250,
      "stock_status": "available",
      "bookstore_id": 1,
      "bookstore_name": "Nhà Sách Fahasa",
      "bookstore_address": "60-62 Lê Lợi, Quận 1, TP.HCM",
      "bookstore_latitude": 10.7720,
      "bookstore_longitude": 106.6972,
      "commission_rate": 15.5,
      "bookstore_phone": "1900636467",
      "bookstore_website": "https://www.fahasa.com",
      "book_title": "Cây Cam Ngọt Của Tôi",
      "book_authors": "José Mauro de Vasconcelos",
      "book_cover_link": "https://salt.tikicdn.com/ts/product/5e/18/24/2a6154ba08df6ce6161c13f4303fa19e.jpg",
      "book_category": "Tiểu Thuyết",
      "book_original_price": 64800,
      "distance_km": 0.35
    },
    {
      "id": 15,
      "book_id": 74021317,
      "purchase_url": "https://www.phuongnam.com/products/74021317",
      "price": 65000,
      "stock_quantity": 50,
      "sold_count": 8,
      "view_count": 120,
      "stock_status": "available",
      "bookstore_id": 2,
      "bookstore_name": "Nhà Sách Phương Nam",
      "bookstore_address": "379 Nguyễn Thị Minh Khai, Quận 3, TP.HCM",
      "bookstore_latitude": 10.7794,
      "bookstore_longitude": 106.6889,
      "commission_rate": 18.0,
      "bookstore_phone": "02838225797",
      "bookstore_website": "https://www.nhasachphuongnam.com",
      "book_title": "Cây Cam Ngọt Của Tôi",
      "book_authors": "José Mauro de Vasconcelos",
      "book_cover_link": "https://salt.tikicdn.com/ts/product/5e/18/24/2a6154ba08df6ce6161c13f4303fa19e.jpg",
      "book_category": "Tiểu Thuyết",
      "book_original_price": 64800,
      "distance_km": 1.2
    }
  ]
}
```

---

### 10. Chi tiết Book Link
**GET** `/book-links/{book_link_id}`

Lấy thông tin chi tiết của một book link.

**Response:**
```json
{
  "id": 10,
  "book_id": 74021317,
  "bookstore_id": 1,
  "purchase_url": "https://www.fahasa.com/products/74021317",
  "price": 64800,
  "stock_quantity": 100,
  "sold_count": 15,
  "view_count": 250,
  "stock_status": "available",
  "created_at": "2025-11-06T11:00:00",
  "updated_at": "2025-11-06T11:00:00",
  "title": "Cây Cam Ngọt Của Tôi",
  "authors": "José Mauro de Vasconcelos",
  "cover_link": "https://salt.tikicdn.com/ts/product/5e/18/24/2a6154ba08df6ce6161c13f4303fa19e.jpg",
  "category": "Tiểu Thuyết",
  "original_price": 64800,
  "bookstore_name": "Nhà Sách Fahasa",
  "bookstore_address": "60-62 Lê Lợi, Quận 1, TP.HCM"
}
```

---

### 11. Tăng lượt xem Book Link
**POST** `/book-links/{book_link_id}/view`

Tăng view count khi user xem chi tiết book link (gọi mỗi khi user click vào link).

**Response:**
```json
{
  "message": "View count incremented successfully"
}
```

---

### 12. Lấy sách của nhà sách
**GET** `/bookstores/{bookstore_id}/books`

Lấy danh sách sách mà nhà sách đang bán.

**Response:**
```json
{
  "bookstore_id": 1,
  "books": [
    {
      "id": 10,
      "book_id": 74021317,
      "bookstore_id": 1,
      "purchase_url": "https://www.fahasa.com/products/74021317",
      "price": 64800,
      "stock_quantity": 100,
      "sold_count": 15,
      "view_count": 250,
      "stock_status": "available",
      "created_at": "2025-11-06T11:00:00",
      "updated_at": "2025-11-06T11:00:00",
      "title": "Cây Cam Ngọt Của Tôi",
      "authors": "José Mauro de Vasconcelos",
      "cover_link": "https://salt.tikicdn.com/ts/product/5e/18/24/2a6154ba08df6ce6161c13f4303fa19e.jpg",
      "category": "Tiểu Thuyết",
      "original_price": 64800
    }
  ]
}
```

---

## 🛒 Order Management APIs

### 13. Tạo đơn hàng
**POST** `/orders/create`

Tạo đơn hàng mới (yêu cầu đăng nhập).

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "items": [
    {
      "book_link_id": 10,
      "quantity": 2
    },
    {
      "book_link_id": 15,
      "quantity": 1
    }
  ],
  "shipping_name": "Nguyễn Văn A",
  "shipping_phone": "0901234567",
  "shipping_address": "123 Nguyễn Văn Linh, Quận 7, TP.HCM",
  "payment_method": "credit_card",
  "notes": "Giao giờ hành chính"
}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 5,
  "bookstore_id": 1,
  "order_number": "ORD20251106ABC12345",
  "total_amount": 194800,
  "order_status": "pending",
  "payment_status": "unpaid",
  "payment_method": "credit_card",
  "shipping_address": "123 Nguyễn Văn Linh, Quận 7, TP.HCM",
  "shipping_phone": "0901234567",
  "shipping_name": "Nguyễn Văn A",
  "notes": "Giao giờ hành chính",
  "created_at": "2025-11-06T14:30:00",
  "updated_at": "2025-11-06T14:30:00",
  "items": [
    {
      "id": 1,
      "order_id": 1,
      "book_link_id": 10,
      "book_id": 74021317,
      "book_title": "Cây Cam Ngọt Của Tôi",
      "quantity": 2,
      "unit_price": 64800,
      "subtotal": 129600,
      "created_at": "2025-11-06T14:30:00"
    },
    {
      "id": 2,
      "order_id": 1,
      "book_link_id": 15,
      "book_id": 184466860,
      "book_title": "Hành Tinh Của Một Kẻ Nghĩ Nhiều",
      "quantity": 1,
      "unit_price": 59900,
      "subtotal": 59900,
      "created_at": "2025-11-06T14:30:00"
    }
  ]
}
```

**Note:** 
- Tất cả items trong một order phải thuộc cùng một nhà sách
- Hệ thống tự động kiểm tra stock và cập nhật số lượng kho

---

### 14. Chi tiết đơn hàng
**GET** `/orders/{order_id}`

Xem chi tiết đơn hàng (chỉ user tạo đơn mới xem được).

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 5,
  "bookstore_id": 1,
  "order_number": "ORD20251106ABC12345",
  "total_amount": 194800,
  "order_status": "processing",
  "payment_status": "paid",
  "payment_method": "credit_card",
  "shipping_address": "123 Nguyễn Văn Linh, Quận 7, TP.HCM",
  "shipping_phone": "0901234567",
  "shipping_name": "Nguyễn Văn A",
  "notes": "Giao giờ hành chính",
  "created_at": "2025-11-06T14:30:00",
  "updated_at": "2025-11-06T14:35:00",
  "items": [...]
}
```

---

### 15. Danh sách đơn hàng của tôi
**GET** `/orders/my-orders?page=1&page_size=20`

Xem danh sách đơn hàng của user (yêu cầu đăng nhập).

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `page` (integer, optional): Trang hiện tại. Default: `1`
- `page_size` (integer, optional): Số đơn hàng mỗi trang. Default: `20`

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 5,
    "bookstore_id": 1,
    "order_number": "ORD20251106ABC12345",
    "total_amount": 194800,
    "order_status": "delivered",
    "payment_status": "paid",
    "payment_method": "credit_card",
    "shipping_address": "123 Nguyễn Văn Linh, Quận 7, TP.HCM",
    "shipping_phone": "0901234567",
    "shipping_name": "Nguyễn Văn A",
    "notes": null,
    "created_at": "2025-11-06T14:30:00",
    "updated_at": "2025-11-06T16:00:00",
    "items": [...]
  }
]
```

---

### 16. Hủy đơn hàng
**PUT** `/orders/{order_id}/cancel`

Hủy đơn hàng (chỉ hủy được khi status là `pending` hoặc `confirmed`).

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "message": "Order cancelled successfully"
}
```

**Note:** Khi hủy đơn, hệ thống tự động hoàn lại stock và sold_count.

---

### 17. Cập nhật trạng thái đơn hàng
**PUT** `/orders/{order_id}/status?order_status=processing&payment_status=paid`

Cập nhật trạng thái đơn hàng (dành cho bookstore/admin).

**Query Parameters:**
- `order_status` (string, optional): Trạng thái đơn hàng
  - `pending`: Chờ xác nhận
  - `confirmed`: Đã xác nhận
  - `processing`: Đang xử lý
  - `shipped`: Đang giao hàng
  - `delivered`: Đã giao hàng
  - `cancelled`: Đã hủy
- `payment_status` (string, optional): Trạng thái thanh toán
  - `unpaid`: Chưa thanh toán
  - `paid`: Đã thanh toán
  - `refunded`: Đã hoàn tiền

**Response:**
```json
{
  "id": 1,
  "user_id": 5,
  "bookstore_id": 1,
  "order_number": "ORD20251106ABC12345",
  "total_amount": 194800,
  "order_status": "processing",
  "payment_status": "paid",
  "payment_method": "credit_card",
  "shipping_address": "123 Nguyễn Văn Linh, Quận 7, TP.HCM",
  "shipping_phone": "0901234567",
  "shipping_name": "Nguyễn Văn A",
  "notes": null,
  "created_at": "2025-11-06T14:30:00",
  "updated_at": "2025-11-06T14:35:00",
  "items": [...]
}
```

---

## 📊 Data Models

### Bookstore
```typescript
{
  id: number;
  name: string;
  email: string;
  phone: string;
  address: string;
  latitude: number;
  longitude: number;
  commission_rate: number;  // 0-100
  description?: string;
  website?: string;
  is_active: boolean;
  created_at: datetime;
}
```

### BookLink
```typescript
{
  id: number;
  book_id: number;  // product_id from books table
  bookstore_id: number;
  purchase_url: string;
  price: number;
  stock_quantity: number;
  sold_count: number;
  view_count: number;
  stock_status: "available" | "out_of_stock" | "pre_order";
  created_at: datetime;
  updated_at: datetime;
}
```

### Order
```typescript
{
  id: number;
  user_id: number;
  bookstore_id: number;
  order_number: string;  // Format: ORD{YYYYMMDD}{UUID}
  total_amount: number;
  order_status: "pending" | "confirmed" | "processing" | "shipped" | "delivered" | "cancelled";
  payment_status: "unpaid" | "paid" | "refunded";
  payment_method: "cash" | "credit_card" | "bank_transfer" | "momo" | "zalopay";
  shipping_address: string;
  shipping_phone: string;
  shipping_name: string;
  notes?: string;
  created_at: datetime;
  updated_at: datetime;
  items: OrderItem[];
}
```

### OrderItem
```typescript
{
  id: number;
  order_id: number;
  book_link_id: number;
  book_id: number;
  book_title: string;
  quantity: number;
  unit_price: number;
  subtotal: number;
  created_at: datetime;
}
```

---

## 🔐 Authentication

Các API yêu cầu authentication cần có header:
```
Authorization: Bearer {access_token}
```

Access token lấy được từ API `/care/auth/login` hoặc `/care/auth/register`.

---

## ⚠️ Error Responses

### 400 Bad Request
```json
{
  "detail": "Insufficient stock for Cây Cam Ngọt Của Tôi"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid authentication credentials"
}
```

### 404 Not Found
```json
{
  "detail": "Order not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Error creating order: {error_message}"
}
```

---

## 💡 Use Cases

### Use Case 1: User mua sách
1. User tìm sách: `GET /books/search/Cây Cam`
2. User xem purchase links: `GET /books/74021317/purchase-links?user_latitude=10.7723&user_longitude=106.6975`
3. User click vào link → Tăng view: `POST /book-links/10/view`
4. User tạo đơn hàng: `POST /orders/create`
5. User xem đơn hàng: `GET /orders/1`

### Use Case 2: Nhà sách quản lý
1. Đăng ký nhà sách: `POST /bookstores/register`
2. Thêm sách bán: `POST /bookstores/book-links`
3. Xem đơn hàng: `GET /bookstores/1/orders`
4. Cập nhật trạng thái: `PUT /orders/1/status?order_status=shipped`
5. Xem thống kê: `GET /bookstores/1/statistics`

### Use Case 3: User quản lý đơn hàng
1. Xem danh sách đơn: `GET /orders/my-orders`
2. Xem chi tiết đơn: `GET /orders/1`
3. Hủy đơn (nếu còn pending): `PUT /orders/1/cancel`

---

## 📝 Notes

1. **Stock Management**: Hệ thống tự động quản lý kho:
   - Khi tạo đơn hàng: `stock_quantity -= quantity`, `sold_count += quantity`
   - Khi hủy đơn: `stock_quantity += quantity`, `sold_count -= quantity`
   - Tự động cập nhật `stock_status` thành `out_of_stock` khi hết hàng

2. **Order Constraints**:
   - Một đơn hàng chỉ có thể chứa sách từ một nhà sách
   - Chỉ hủy được đơn hàng khi status là `pending` hoặc `confirmed`

3. **Purchase Links Sorting**:
   - Nếu có GPS: Sắp xếp theo khoảng cách → % hoa hồng
   - Nếu không có GPS: Sắp xếp theo % hoa hồng

4. **View Count**: Gọi API increment view mỗi khi user click vào purchase link để tracking

---

**Last Updated**: November 6, 2025
**Version**: 1.0
