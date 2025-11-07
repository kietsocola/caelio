# Caelio Care API - Complete Documentation

**Version**: 2.0  
**Base URL**: `http://localhost:8000`

This is the complete API documentation for the Caelio Care bibliotherapy platform, which combines personality assessment, emotional wellbeing analysis, user-generated content (White Books), and bookstore marketplace functionality.

---

## Table of Contents

1. [Authentication](#authentication)
2. [User Management](#user-management)
3. [Emotional Assessment (PERMA-DASS)](#emotional-assessment)
4. [White Books (User Content)](#white-books)
5. [Bookstore Management](#bookstore-management)
6. [Order Management](#order-management)
7. [Statistics](#statistics)
8. [Error Handling](#error-handling)

---

## Authentication

### Overview
The API uses JWT (JSON Web Token) for authentication. Some endpoints are public, while others require authentication.

**Public Endpoints**:
- User registration/login
- Emotional test (anonymous or authenticated)
- View published white books
- Search books
- View bookstores

**Protected Endpoints**:
- Creating/editing white books
- Managing bookstore (if owner)
- Placing orders
- Viewing personal data

### Get JWT Token

Include the token in subsequent requests:
```
Authorization: Bearer <your_jwt_token>
```

---

## User Management

### 1. Register User

**Endpoint**: `POST /auth/register`  
**Auth**: Not required

**Request**:
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password123",
  "full_name": "John Doe"
}
```

**Response**: `200 OK`
```json
{
  "user_id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "created_at": "2024-01-15T10:00:00"
}
```

### 2. Login

**Endpoint**: `POST /auth/login`  
**Auth**: Not required

**Request**:
```json
{
  "username": "john_doe",
  "password": "secure_password123"
}
```

**Response**: `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "user_id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "full_name": "John Doe"
  }
}
```

### 3. Get Current User

**Endpoint**: `GET /auth/me`  
**Auth**: Required

**Response**: `200 OK` - User object

---

## Emotional Assessment

### PERMA-DASS System
9-question emotional assessment based on PERMA-V and DASS frameworks. Categorizes users into 4 emotional layers and provides personalized book recommendations and writing prompts.

### 1. Get Emotional Test Questions

**Endpoint**: `GET /emotional-test/questions`  
**Auth**: Not required

**Response**: `200 OK`
```json
{
  "questions": [
    {
      "id": "1",
      "question": "Trong tuần qua, bạn có cảm thấy khó thở không?",
      "category": "anxiety",
      "options": [
        "0 - Không bao giờ",
        "1 - Thỉnh thoảng",
        "2 - Khá thường xuyên",
        "3 - Rất thường xuyên"
      ]
    },
    // ... 8 more questions
  ]
}
```

### 2. Submit Test (Anonymous)

**Endpoint**: `POST /emotional-test/submit`  
**Auth**: Not required

**Request**:
```json
{
  "answers": {
    "1": 1,
    "2": 2,
    "3": 0,
    "4": 1,
    "5": 2,
    "6": 1,
    "7": 0,
    "8": 2,
    "9": 1
  }
}
```

**Response**: `200 OK`
```json
{
  "test_id": "anon_abc123",
  "emotional_layer": "Layer 2",
  "created_at": "2024-01-15T10:30:00"
}
```

### 3. Submit Test (Authenticated)

**Endpoint**: `POST /emotional-test/submit`  
**Auth**: Required

**Request**: Same as anonymous

**Response**: `200 OK`
```json
{
  "test_id": 123,
  "user_id": 1,
  "emotional_layer": "Layer 2",
  "created_at": "2024-01-15T10:30:00"
}
```

### 4. Analyze Test Results

**Endpoint**: `GET /emotional-test/results/{test_id}`  
**Auth**: Not required (for anonymous tests), Required (for user tests)

**Response**: `200 OK`
```json
{
  "test_id": 123,
  "emotional_layer": "Layer 2",
  "layer_description": {
    "description": "Căng thẳng vừa phải, hạnh phúc trung bình",
    "characteristics": [
      "Có những lúc cảm thấy stress nhưng vẫn kiểm soát được",
      "Có mối quan hệ xã hội nhưng chưa thực sự sâu sắc"
    ]
  },
  "book_recommendations": {
    "primary_books": [...],
    "secondary_books": [...]
  },
  "writing_prompts": [
    "Hãy viết về một khoảnh khắc bạn cảm thấy bình yên...",
    "Mô tả một mối quan hệ quan trọng trong cuộc đời bạn..."
  ]
}
```

### 5. Get User Test History

**Endpoint**: `GET /emotional-test/history`  
**Auth**: Required

**Response**: `200 OK` - Array of test results

---

## White Books

User-generated content system where users write multi-chapter books.

### Data Models

**WhiteBook**:
```json
{
  "id": 1,
  "author_id": 123,
  "author_username": "john_doe",
  "title": "My Journey",
  "cover_image": "https://example.com/cover.jpg",
  "description": "A personal story",
  "emotional_layer": "Layer 1",
  "tags": ["healing", "hope"],
  "is_published": true,
  "view_count": 245,
  "like_count": 18,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-20T14:22:00",
  "chapters": [...]
}
```

**Chapter**:
```json
{
  "id": 1,
  "book_id": 1,
  "chapter_number": 1,
  "chapter_title": "The Beginning",
  "content": "It all started...",
  "created_at": "2024-01-15T10:35:00",
  "updated_at": "2024-01-15T10:35:00"
}
```

### 1. Create White Book

**Endpoint**: `POST /white-books/create`  
**Auth**: Required

**Request**:
```json
{
  "title": "My Healing Journey",
  "cover_image": "https://example.com/cover.jpg",
  "description": "A story about recovery",
  "emotional_layer": "Layer 1",
  "tags": ["healing", "hope"]
}
```

**Response**: `200 OK` - WhiteBook object (without chapters)

### 2. Add Chapter

**Endpoint**: `POST /white-books/{book_id}/chapters`  
**Auth**: Required (must be author)

**Request**:
```json
{
  "chapter_number": 1,
  "chapter_title": "The Beginning",
  "content": "It all started on a rainy day..."
}
```

**Response**: `200 OK` - Chapter object

### 3. Get Book Chapters

**Endpoint**: `GET /white-books/{book_id}/chapters`  
**Auth**: Not required

**Response**: `200 OK` - Array of Chapter objects (sorted by chapter_number)

### 4. Update Book Metadata

**Endpoint**: `PUT /white-books/{book_id}`  
**Auth**: Required (must be author)

**Request**:
```json
{
  "title": "Updated Title",
  "description": "New description",
  "tags": ["new", "tags"]
}
```

**Response**: `200 OK` - Updated WhiteBook object

### 5. Delete Chapter

**Endpoint**: `DELETE /white-books/{book_id}/chapters/{chapter_id}`  
**Auth**: Required (must be author)

**Response**: `200 OK`
```json
{
  "message": "Chapter deleted successfully"
}
```

### 6. Get My Books

**Endpoint**: `GET /white-books/my-books`  
**Auth**: Required

**Response**: `200 OK` - Array of WhiteBook objects

### 7. Get Book Detail

**Endpoint**: `GET /white-books/{book_id}?include_chapters=true`  
**Auth**: Not required

**Response**: `200 OK` - WhiteBook object with chapters

### 8. Publish Book

**Endpoint**: `PUT /white-books/{book_id}/publish`  
**Auth**: Required (must be author)

**Response**: `200 OK`
```json
{
  "message": "Book published successfully"
}
```

### 9. Unpublish Book

**Endpoint**: `PUT /white-books/{book_id}/unpublish`  
**Auth**: Required (must be author)

**Response**: `200 OK`

### 10. Delete Book

**Endpoint**: `DELETE /white-books/{book_id}`  
**Auth**: Required (must be author)

**Response**: `200 OK` (deletes all chapters too)

### 11. Get Published Books

**Endpoint**: `GET /white-books/published?emotional_layer=Layer1&page=1&page_size=20`  
**Auth**: Not required

**Response**: `200 OK` - Array of published WhiteBook objects

### 12. Search Books

**Endpoint**: `GET /white-books/search/{query}?limit=20`  
**Auth**: Not required

**Response**: `200 OK` - Array of matching WhiteBook objects

### 13. Toggle Like

**Endpoint**: `POST /white-books/{book_id}/like`  
**Auth**: Required

**Response**: `200 OK`
```json
{
  "liked": true,
  "like_count": 19
}
```

---

## Bookstore Management

### Data Models

**Bookstore**:
```json
{
  "id": 1,
  "name": "Nhà sách Fahasa Nguyễn Huệ",
  "address": "40 Nguyễn Huệ, Q.1, TP.HCM",
  "gps_latitude": 10.7769,
  "gps_longitude": 106.7009,
  "phone": "0901234567",
  "email": "contact@fahasa.com",
  "commission_rate": 15.5,
  "is_active": true,
  "created_at": "2024-01-10T09:00:00"
}
```

**BookLink**:
```json
{
  "id": 1,
  "bookstore_id": 1,
  "book_name": "Đắc Nhân Tâm",
  "book_code": "DNT001",
  "price": 86000.0,
  "stock_quantity": 50,
  "sold_count": 120,
  "view_count": 450,
  "purchase_link": "https://fahasa.com/dac-nhan-tam",
  "created_at": "2024-01-10T10:00:00",
  "updated_at": "2024-01-15T14:30:00"
}
```

### 1. Register Bookstore

**Endpoint**: `POST /bookstores/register`  
**Auth**: Not required

**Request**:
```json
{
  "name": "Nhà sách Fahasa Nguyễn Huệ",
  "address": "40 Nguyễn Huệ, Q.1, TP.HCM",
  "gps_latitude": 10.7769,
  "gps_longitude": 106.7009,
  "phone": "0901234567",
  "email": "contact@fahasa.com",
  "commission_rate": 15.5
}
```

**Response**: `200 OK` - Bookstore object

### 2. Get All Bookstores

**Endpoint**: `GET /bookstores?active_only=true`  
**Auth**: Not required

**Response**: `200 OK` - Array of Bookstore objects

### 3. Get Bookstore Details

**Endpoint**: `GET /bookstores/{bookstore_id}`  
**Auth**: Not required

**Response**: `200 OK` - Bookstore object

### 4. Update Bookstore

**Endpoint**: `PUT /bookstores/{bookstore_id}`  
**Auth**: Not required

**Request**:
```json
{
  "name": "Updated Name",
  "commission_rate": 12.0,
  "is_active": true
}
```

**Response**: `200 OK` - Updated Bookstore object

### 5. Add Book Link

**Endpoint**: `POST /bookstores/{bookstore_id}/books`  
**Auth**: Not required

**Request**:
```json
{
  "book_name": "Đắc Nhân Tâm",
  "book_code": "DNT001",
  "price": 86000.0,
  "stock_quantity": 50,
  "purchase_link": "https://fahasa.com/dac-nhan-tam"
}
```

**Response**: `200 OK` - BookLink object

### 6. Update Book Link

**Endpoint**: `PUT /bookstores/{bookstore_id}/books/{book_id}`  
**Auth**: Not required

**Request**:
```json
{
  "price": 79000.0,
  "stock_quantity": 30
}
```

**Response**: `200 OK` - Updated BookLink object

### 7. Get Bookstore Books

**Endpoint**: `GET /bookstores/{bookstore_id}/books?in_stock_only=true`  
**Auth**: Not required

**Response**: `200 OK` - Array of BookLink objects

### 8. Get Purchase Links (Prioritized)

**Endpoint**: `GET /books/{book_code}/purchase-links?user_latitude=10.7769&user_longitude=106.7009&limit=5`  
**Auth**: Not required

**Response**: `200 OK`
```json
[
  {
    "bookstore_id": 1,
    "bookstore_name": "Nhà sách Fahasa Nguyễn Huệ",
    "bookstore_address": "40 Nguyễn Huệ, Q.1, TP.HCM",
    "book_id": 1,
    "book_name": "Đắc Nhân Tâm",
    "price": 86000.0,
    "stock_quantity": 50,
    "purchase_link": "https://fahasa.com/dac-nhan-tam",
    "distance_km": 0.5,
    "commission_rate": 15.5,
    "priority_score": 84.5
  }
]
```

**Priority Formula**: `priority_score = commission_rate * 10 - distance_km`

### 9. Bookstore Statistics

**Endpoint**: `GET /bookstores/{bookstore_id}/stats`  
**Auth**: Not required

**Response**: `200 OK`
```json
{
  "bookstore_id": 1,
  "total_books": 156,
  "in_stock_books": 142,
  "total_stock_quantity": 2450,
  "total_sold": 1823,
  "total_views": 8932,
  "total_revenue": 125600000.0,
  "top_selling_books": [...]
}
```

---

## Order Management

### Data Models

**Order**:
```json
{
  "id": 1,
  "user_id": 123,
  "book_link_id": 456,
  "quantity": 2,
  "total_price": 172000.0,
  "order_status": "pending",
  "payment_status": "pending",
  "shipping_address": "123 Lê Lợi, Q.1, TP.HCM",
  "phone": "0987654321",
  "notes": "Giao giờ hành chính",
  "created_at": "2024-01-15T14:30:00",
  "updated_at": "2024-01-15T14:30:00"
}
```

**Order Status**: `pending`, `confirmed`, `shipping`, `delivered`, `cancelled`  
**Payment Status**: `pending`, `paid`, `refunded`

### 1. Create Order

**Endpoint**: `POST /orders/create`  
**Auth**: Required

**Request**:
```json
{
  "book_link_id": 456,
  "quantity": 2,
  "shipping_address": "123 Lê Lợi, Q.1, TP.HCM",
  "phone": "0987654321",
  "notes": "Giao giờ hành chính"
}
```

**Response**: `200 OK` - Order object

**Note**: Stock is automatically decremented

### 2. Get My Orders

**Endpoint**: `GET /orders/my-orders?status=pending`  
**Auth**: Required

**Response**: `200 OK` - Array of Order objects with book/bookstore details

### 3. Get Order Detail

**Endpoint**: `GET /orders/{order_id}`  
**Auth**: Required

**Response**: `200 OK` - Order object with full details

### 4. Update Order Status

**Endpoint**: `PUT /orders/{order_id}/status`  
**Auth**: Required

**Request**:
```json
{
  "order_status": "confirmed",
  "payment_status": "paid"
}
```

**Response**: `200 OK` - Updated Order object

### 5. Cancel Order

**Endpoint**: `PUT /orders/{order_id}/cancel`  
**Auth**: Required

**Response**: `200 OK` - Updated Order object

**Note**: Stock is automatically restored

### 6. Get Bookstore Orders

**Endpoint**: `GET /bookstores/{bookstore_id}/orders?status=pending`  
**Auth**: Not required

**Response**: `200 OK` - Array of Order objects for that bookstore

---

## Statistics

### Get System Statistics

**Endpoint**: `GET /stats`  
**Auth**: Not required

**Response**: `200 OK`
```json
{
  "users": 1234,
  "emotional_tests": 5678,
  "white_books": {
    "total": 234,
    "published": 189
  },
  "emotional_layers": [
    {"emotional_layer": "Layer 2", "count": 2341},
    {"emotional_layer": "Layer 1", "count": 1876}
  ],
  "available_layers": ["Layer 1", "Layer 2", "Layer 3", "Layer 4"]
}
```

---

## Error Handling

### Error Response Format
```json
{
  "detail": "Error message description"
}
```

### HTTP Status Codes
- **200 OK**: Success
- **400 Bad Request**: Invalid input
- **401 Unauthorized**: Missing/invalid token
- **403 Forbidden**: Not authorized for this action
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

---

## Complete Usage Examples

### 1. User Takes Emotional Test & Gets Recommendations

```bash
# 1. Take the test (anonymous)
POST /emotional-test/submit
{
  "answers": { "1": 1, "2": 2, "3": 0, ... }
}
# Response: { "test_id": "anon_abc123", "emotional_layer": "Layer 2" }

# 2. Get detailed results
GET /emotional-test/results/anon_abc123
# Response includes book recommendations and writing prompts

# 3. View recommended books (from bookstore)
GET /books/DNT001/purchase-links?user_latitude=10.7769&user_longitude=106.7009

# 4. Register to save test results
POST /auth/register
{ "username": "john", "email": "john@ex.com", "password": "pass123" }

# 5. Login
POST /auth/login
{ "username": "john", "password": "pass123" }
# Response: { "access_token": "...", ... }

# 6. Take test again (now saved to profile)
POST /emotional-test/submit
Authorization: Bearer <token>
{ "answers": { ... } }

# 7. View test history
GET /emotional-test/history
Authorization: Bearer <token>
```

### 2. User Creates & Publishes a Multi-Chapter Book

```bash
# 1. Create book
POST /white-books/create
Authorization: Bearer <token>
{
  "title": "My Healing Journey",
  "cover_image": "https://example.com/cover.jpg",
  "description": "A 5-chapter story",
  "emotional_layer": "Layer 1",
  "tags": ["healing", "hope"]
}
# Response: { "id": 123, ... }

# 2. Add chapters
POST /white-books/123/chapters
Authorization: Bearer <token>
{ "chapter_number": 1, "chapter_title": "Dark Days", "content": "..." }

POST /white-books/123/chapters
Authorization: Bearer <token>
{ "chapter_number": 2, "chapter_title": "Finding Help", "content": "..." }

# ... add more chapters

# 3. Preview the book
GET /white-books/123?include_chapters=true

# 4. Publish
PUT /white-books/123/publish
Authorization: Bearer <token>

# 5. Book appears in public listings
GET /white-books/published?emotional_layer=Layer 1

# 6. Other users can read
GET /white-books/123
GET /white-books/123/chapters
```

### 3. Bookstore Registration & Book Sales

```bash
# 1. Register bookstore
POST /bookstores/register
{
  "name": "Fahasa Nguyễn Huệ",
  "address": "40 Nguyễn Huệ, Q.1, TP.HCM",
  "gps_latitude": 10.7769,
  "gps_longitude": 106.7009,
  "phone": "0901234567",
  "email": "contact@fahasa.com",
  "commission_rate": 15.5
}
# Response: { "id": 1, ... }

# 2. Add books to inventory
POST /bookstores/1/books
{
  "book_name": "Đắc Nhân Tâm",
  "book_code": "DNT001",
  "price": 86000.0,
  "stock_quantity": 50,
  "purchase_link": "https://fahasa.com/dac-nhan-tam"
}

# 3. User searches for book
GET /books/DNT001/purchase-links?user_latitude=10.7769&user_longitude=106.7009

# 4. User places order
POST /orders/create
Authorization: Bearer <token>
{
  "book_link_id": 456,
  "quantity": 2,
  "shipping_address": "123 Lê Lợi, Q.1",
  "phone": "0987654321"
}

# 5. Bookstore views orders
GET /bookstores/1/orders?status=pending

# 6. Update order status
PUT /orders/789/status
{ "order_status": "confirmed", "payment_status": "paid" }

# 7. View bookstore statistics
GET /bookstores/1/stats
```

---

## Running the Server

```bash
# Install dependencies
pip install -r requirements_api.txt

# Set environment variables
export DATABASE_URL="postgresql://user:password@localhost/caelio_db"
export JWT_SECRET_KEY="your-secret-key-here"

# Run the combined server
python run_api.py

# Server runs on http://localhost:8000
# API docs available at http://localhost:8000/docs
```

---

## Database Setup

Requires PostgreSQL database. Run migrations:

```bash
# Create database
createdb caelio_db

# Run schema setup (automatically done on first run)
# Or manually run migration scripts:
python update_database_schema.py  # For bookstore features
python update_white_books_schema.py  # For white books chapters
```

---

## Additional Resources

- **Bookstore & Orders API**: See `BOOKSTORE_ORDER_API_DOCS.md`
- **White Books API**: See `WHITE_BOOKS_API_DOCS.md`
- **Caelio Care Guide**: See `caelio_care/guide.md`
- **API Guide**: See `GUIDE_FINAL.md`

---

**Support**: For questions or issues, contact the development team.
