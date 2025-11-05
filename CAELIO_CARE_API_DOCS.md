# Caelio Care API Documentation for Frontend Team

## Base URL
```
http://localhost:8000/care
```

## Authentication
Sử dụng JWT Bearer token trong header:
```
Authorization: Bearer {access_token}
```

---

## 📋 Table of Contents
1. [Authentication APIs](#authentication-apis)
2. [Emotional Assessment APIs](#emotional-assessment-apis)
3. [White Books APIs](#white-books-apis)
4. [Writing Prompts APIs](#writing-prompts-apis)
5. [Bookstore APIs](#bookstore-apis)
6. [Book Purchase Links APIs](#book-purchase-links-apis)
7. [Statistics APIs](#statistics-apis)
8. [Error Handling](#error-handling)

---

## 🔐 Authentication APIs

### 1. Register User
**Endpoint:** `POST /care/auth/register`

**Request:**
```json
{
  "email": "user@example.com",
  "username": "testuser",
  "password": "password123",
  "full_name": "Test User" // optional
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "user_id": 1,
    "email": "user@example.com",
    "username": "testuser",
    "full_name": "Test User",
    "created_at": "2025-11-04T10:30:00",
    "is_active": true
  }
}
```

**Errors:**
- `400`: Email already registered / Username already taken
- `500`: Registration failed

### 2. Login User
**Endpoint:** `POST /care/auth/login`

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "user_id": 1,
    "email": "user@example.com",
    "username": "testuser",
    "full_name": "Test User",
    "created_at": "2025-11-04T10:30:00",
    "is_active": true
  }
}
```

**Errors:**
- `401`: Incorrect email or password

### 3. Get Current User
**Endpoint:** `GET /care/auth/me`

**Headers:** `Authorization: Bearer {token}`

**Response (200):**
```json
{
  "user_id": 1,
  "email": "user@example.com",
  "username": "testuser",
  "full_name": "Test User",
  "created_at": "2025-11-04T10:30:00",
  "is_active": true
}
```

**Errors:**
- `401`: Invalid authentication credentials
- `404`: User not found

---

## 🧠 Emotional Assessment APIs

### 1. Get Emotional Questions
**Endpoint:** `GET /care/emotional-test/questions`

**Response (200):**
```json
{
  "questions": {
    "Q1": {
      "question": "Gần đây tôi thường cảm thấy biết ơn, nhẹ nhõm hoặc tìm thấy niềm vui trong những điều nhỏ bé.",
      "group": "PERMA",
      "component": "Positive Emotion",
      "layer": "Hồi phục / Tái sinh",
      "why": "Đọc để nuôi dưỡng cảm xúc tích cực, tìm lại niềm vui giản đơn trong cuộc sống.",
      "how": "Đọc chậm, văn chương hoặc thơ mang năng lượng bình an."
    },
    // ... Q2 to Q9
  },
  "scale": "1-5 (1 = Hoàn toàn không đồng ý, 5 = Hoàn toàn đồng ý)",
  "description": "Bộ câu hỏi đánh giá cảm xúc dựa trên mô hình PERMA-DASS"
}
```

### 2. Analyze Emotional Test
**Endpoint:** `POST /care/emotional-test/analyze`

**Headers:** `Authorization: Bearer {token}` (optional, nếu không login vẫn làm test được nhưng không lưu, còn login thì lưu kết quả)

**Query Parameters:**
- `archetype` (optional): string - Personality archetype from main API (e.g., "Tri thức", "Kết nối")

**Request:**
```json
{
  "Q1": 4,
  "Q2": 3,
  "Q3": 3,
  "Q4": 4,
  "Q5": 3,
  "Q6": 2,
  "Q7": 3,
  "Q8": 2,
  "Q9": 1
}
```

**Response (200):**
```json
{
  "perma_score": 3.4,
  "dass_score": 2.0,
  "mbi_score": 1.4,
  "emotional_layer": "Hồi phục",
  "layer_description": "Tái kết nối năng lượng và tìm lại nhịp sống.",
  "reading_goal": "Tái kết nối năng lượng và tìm lại nhịp sống.",
  "archetype_influence": "Tri thức"
}
```

**Errors:**
- `400`: Answer for {Q_id} must be between 1 and 5
- `401`: Authentication required
- `500`: Error analyzing emotional test

### 3. Get Book Prescription
**Endpoint:** `GET /care/emotional-test/prescription/{emotional_layer}`

**Path Parameters:**
- `emotional_layer`: string - One of: "Nhận diện", "Chấp nhận", "Hồi phục", "Tái sinh"

**Query Parameters:**
- `archetype` (optional): string - Personality archetype for customization

**Response (200):**
```json
{
  "emotional_layer": "Hồi phục",
  "goal": "Tái kết nối năng lượng và tìm lại nhịp sống.",
  "recommended_books": [
    "Ikigai (Héctor García)",
    "Sức mạnh của sự tĩnh lặng (Eckhart Tolle)",
    "Stillness is the Key (Ryan Holiday)",
    // Additional books based on archetype
  ],
  "recommended_movies": [
    "Eat Pray Love",
    "Soul (Pixar)"
  ],
  "writing_prompts": [
    "Hôm nay bạn biết ơn điều gì?",
    "Bạn đã làm điều nhỏ nào khiến bản thân thấy dễ chịu hơn?"
  ]
}
```

### 4. Get My Emotional Results
**Endpoint:** `GET /care/emotional-test/my-results`

**Headers:** `Authorization: Bearer {token}`

**Response (200):**
```json
[
  {
    "result_id": 1,
    "user_id": 1,
    "answers": {
      "Q1": 4,
      "Q2": 3,
      // ... Q3 to Q9
    },
    "perma_score": 3.4,
    "dass_score": 2.0,
    "mbi_score": 1.4,
    "emotional_layer": "Hồi phục",
    "archetype": "Tri thức",
    "created_at": "2025-11-04T10:30:00"
  }
  // ... up to 10 most recent results
]
```

---

## 📚 White Books APIs

### 1. Create White Book
**Endpoint:** `POST /care/white-books/create`

**Headers:** `Authorization: Bearer {token}`

**Request:**
```json
{
  "title": "Hành trình tìm lại chính mình",
  "category": "Tự truyện", // optional
  "content": "Đây là câu chuyện về hành trình khám phá bản thân...",
  "emotional_layer": "Hồi phục", // optional
  "prompt_used": "Hôm nay bạn biết ơn điều gì?", // optional
  "tags": ["tự truyện", "hồi phục", "biết ơn"] // optional
}
```

**Response (200):**
```json
{
  "book_id": 1,
  "author_id": 1,
  "author_username": null,
  "title": "Hành trình tìm lại chính mình",
  "category": "Tự truyện",
  "content": "Đây là câu chuyện về hành trình khám phá bản thân...",
  "emotional_layer": "Hồi phục",
  "prompt_used": "Hôm nay bạn biết ơn điều gì?",
  "tags": ["tự truyện", "hồi phục", "biết ơn"],
  "is_published": false,
  "created_at": "2025-11-04T10:30:00",
  "updated_at": "2025-11-04T10:30:00",
  "views": 0,
  "likes": 0
}
```

### 2. Get My White Books
**Endpoint:** `GET /care/white-books/my-books`

**Headers:** `Authorization: Bearer {token}`

**Response (200):**
```json
[
  {
    "book_id": 1,
    "author_id": 1,
    "title": "Hành trình tìm lại chính mình",
    "category": "Tự truyện",
    "content": "Full content...",
    "emotional_layer": "Hồi phục",
    "prompt_used": "Hôm nay bạn biết ơn điều gì?",
    "tags": ["tự truyện", "hồi phục"],
    "is_published": false,
    "created_at": "2025-11-04T10:30:00",
    "updated_at": "2025-11-04T10:30:00",
    "views": 0,
    "likes": 0
  }
  // ... all user's books
]
```

### 3. Publish White Book
**Endpoint:** `PUT /care/white-books/{book_id}/publish`

**Headers:** `Authorization: Bearer {token}`

**Path Parameters:**
- `book_id`: integer - ID of the book to publish

**Response (200):**
```json
{
  "message": "Book published successfully"
}
```

**Errors:**
- `404`: Book not found or not authorized
- `401`: Authentication required

### 4. Get Published White Books
**Endpoint:** `GET /care/white-books/published`

**Query Parameters:**
- `emotional_layer` (optional): string - Filter by emotional layer
- `page` (optional): integer - Page number (default: 1)
- `page_size` (optional): integer - Items per page (default: 20)

**Response (200):**
```json
[
  {
    "book_id": 1,
    "author_id": 1,
    "author_username": "testuser",
    "title": "Hành trình tìm lại chính mình",
    "category": "Tự truyện",
    "content": "Đây là câu chuyện về hành trình...",
    "emotional_layer": "Hồi phục",
    "prompt_used": "Hôm nay bạn biết ơn điều gì?",
    "tags": ["tự truyện", "hồi phục"],
    "is_published": true,
    "created_at": "2025-11-04T10:30:00",
    "updated_at": "2025-11-04T10:30:00",
    "views": 15,
    "likes": 3
  }
  // ... more published books
]
```

### 5. Get White Book Detail
**Endpoint:** `GET /care/white-books/{book_id}`

**Path Parameters:**
- `book_id`: integer - ID of the book

**Response (200):**
```json
{
  "book_id": 1,
  "author_id": 1,
  "author_username": "testuser",
  "title": "Hành trình tìm lại chính mình",
  "category": "Tự truyện",
  "content": "Full content of the book...",
  "emotional_layer": "Hồi phục",
  "prompt_used": "Hôm nay bạn biết ơn điều gì?",
  "tags": ["tự truyện", "hồi phục"],
  "is_published": true,
  "created_at": "2025-11-04T10:30:00",
  "updated_at": "2025-11-04T10:30:00",
  "views": 16, // Incremented after view
  "likes": 3
}
```

**Errors:**
- `404`: Book not found

### 6. Search White Books
**Endpoint:** `GET /care/white-books/search/{query}`

**Path Parameters:**
- `query`: string - Search query

**Query Parameters:**
- `limit` (optional): integer - Max results (default: 20)

**Response (200):**
```json
[
  {
    "book_id": 1,
    "author_id": 1,
    "author_username": "testuser",
    "title": "Hành trình tìm lại chính mình",
    "category": "Tự truyện",
    "content": "Truncated content preview...", // Max 500 chars
    "emotional_layer": "Hồi phục",
    "prompt_used": "Hôm nay bạn biết ơn điều gì?",
    "tags": ["tự truyện", "hồi phục"],
    "is_published": true,
    "created_at": "2025-11-04T10:30:00",
    "updated_at": "2025-11-04T10:30:00",
    "views": 15,
    "likes": 3
  }
  // ... search results
]
```

---

## ✍️ Writing Prompts APIs

### 1. Get Writing Prompts
**Endpoint:** `GET /care/writing-prompts/{emotional_layer}`

**Path Parameters:**
- `emotional_layer`: string - One of: "Nhận diện", "Chấp nhận", "Hồi phục", "Tái sinh"

**Response (200):**
```json
{
  "emotional_layer": "Hồi phục",
  "prompts": [
    "Hôm nay bạn biết ơn điều gì?",
    "Bạn đã làm điều nhỏ nào khiến bản thân thấy dễ chịu hơn?"
  ]
}
```

---

## 📊 Statistics APIs

### 1. Get System Stats
**Endpoint:** `GET /care/stats`

**Response (200):**
```json
{
  "users": 150,
  "emotional_tests": 423,
  "white_books": {
    "total": 89,
    "published": 67
  },
  "emotional_layers": [
    {
      "emotional_layer": "Hồi phục",
      "count": 156
    },
    {
      "emotional_layer": "Tái sinh", 
      "count": 98
    },
    {
      "emotional_layer": "Chấp nhận",
      "count": 87
    },
    {
      "emotional_layer": "Nhận diện",
      "count": 82
    }
  ],
  "available_layers": [
    "Nhận diện",
    "Chấp nhận", 
    "Hồi phục",
    "Tái sinh"
  ]
}
```

---

## 🚨 Error Handling

### Common Error Response Format:
```json
{
  "detail": "Error message description"
}
```

### HTTP Status Codes:
- `200`: Success
- `400`: Bad Request (validation error)
- `401`: Unauthorized (authentication required/invalid)
- `403`: Forbidden (not authorized for this action)
- `404`: Not Found (resource doesn't exist)
- `500`: Internal Server Error

### Authentication Errors:
```json
{
  "detail": "Invalid authentication credentials",
  "headers": {
    "WWW-Authenticate": "Bearer"
  }
}
```

---

## 🔄 Typical User Flow

### 1. User Registration & Assessment:
```javascript
// 1. Register
const registerResponse = await fetch('/care/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    username: 'user123',
    password: 'password123'
  })
});
const { access_token } = await registerResponse.json();

// 2. Get questions
const questionsResponse = await fetch('/care/emotional-test/questions');
const { questions } = await questionsResponse.json();

// 3. Submit assessment
const assessmentResponse = await fetch('/care/emotional-test/analyze?archetype=Tri thức', {
  method: 'POST',
  headers: { 
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${access_token}`
  },
  body: JSON.stringify({
    Q1: 4, Q2: 3, Q3: 3, Q4: 4, Q5: 3,
    Q6: 2, Q7: 3, Q8: 2, Q9: 1
  })
});
const profile = await assessmentResponse.json();

// 4. Get prescription
const prescriptionResponse = await fetch(`/care/emotional-test/prescription/${profile.emotional_layer}?archetype=Tri thức`);
const prescription = await prescriptionResponse.json();
```

### 2. Content Creation:
```javascript
// 1. Create book
const bookResponse = await fetch('/care/white-books/create', {
  method: 'POST',
  headers: { 
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${access_token}`
  },
  body: JSON.stringify({
    title: 'My Journey',
    content: 'Book content...',
    emotional_layer: profile.emotional_layer,
    prompt_used: prescription.writing_prompts[0]
  })
});
const book = await bookResponse.json();

// 2. Publish book
await fetch(`/care/white-books/${book.book_id}/publish`, {
  method: 'PUT',
  headers: { 'Authorization': `Bearer ${access_token}` }
});
```

---

## 📱 Frontend Implementation Notes

### 1. Authentication State Management:
- Store JWT token securely (localStorage/sessionStorage)
- Auto-add Authorization header to requests
- Handle token expiration (401 errors)
- Redirect to login on authentication failures

### 2. Emotional Assessment UI:
- 9 questions with 1-5 scale (radio buttons/slider)
- Progress indicator (question X of 9)
- Validation: ensure all questions answered
- Pass archetype from personality assessment if available

### 3. Results Display:
- Show emotional layer with description
- Display MBI score with visual indicator
- Show book/movie recommendations in cards
- Highlight writing prompts for content creation

### 4. White Books Interface:
- Rich text editor for content creation
- Tag input system
- Draft/Published status indicators
- Community browsing with filters
- Search functionality

### 5. Error Handling:
- Display user-friendly error messages
- Handle network failures gracefully
- Show loading states during API calls
- Validation feedback for forms

---

## 🏪 Bookstore APIs

### 1. Register Bookstore
**Endpoint:** `POST /care/bookstores/register`

**Description:** Đăng ký nhà sách mới vào hệ thống

**Request:**
```json
{
  "name": "Nhà sách Fahasa",
  "email": "fahasa@example.com",
  "phone": "0901234567",
  "address": "123 Nguyễn Huệ, Quận 1, TP.HCM",
  "latitude": 10.7769,
  "longitude": 106.7009,
  "commission_rate": 15.5,
  "description": "Nhà sách lớn nhất Việt Nam",
  "website": "https://fahasa.com"
}
```

**Response (200):**
```json
{
  "id": 1,
  "name": "Nhà sách Fahasa",
  "email": "fahasa@example.com",
  "phone": "0901234567",
  "address": "123 Nguyễn Huệ, Quận 1, TP.HCM",
  "latitude": 10.7769,
  "longitude": 106.7009,
  "commission_rate": 15.5,
  "description": "Nhà sách lớn nhất Việt Nam",
  "website": "https://fahasa.com",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00"
}
```

**Error (400):**
```json
{
  "detail": "Email already registered"
}
```

---

### 2. Get All Bookstores
**Endpoint:** `GET /care/bookstores?active_only=true`

**Description:** Lấy danh sách tất cả nhà sách

**Query Parameters:**
- `active_only` (boolean, optional): Chỉ lấy nhà sách đang hoạt động. Default: `true`

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "Nhà sách Fahasa",
    "email": "fahasa@example.com",
    "phone": "0901234567",
    "address": "123 Nguyễn Huệ, Quận 1, TP.HCM",
    "latitude": 10.7769,
    "longitude": 106.7009,
    "commission_rate": 15.5,
    "description": "Nhà sách lớn nhất Việt Nam",
    "website": "https://fahasa.com",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00"
  }
]
```

---

### 3. Get Bookstore Details
**Endpoint:** `GET /care/bookstores/{bookstore_id}`

**Description:** Lấy thông tin chi tiết của một nhà sách

**Response (200):**
```json
{
  "id": 1,
  "name": "Nhà sách Fahasa",
  "email": "fahasa@example.com",
  "phone": "0901234567",
  "address": "123 Nguyễn Huệ, Quận 1, TP.HCM",
  "latitude": 10.7769,
  "longitude": 106.7009,
  "commission_rate": 15.5,
  "description": "Nhà sách lớn nhất Việt Nam",
  "website": "https://fahasa.com",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00"
}
```

**Error (404):**
```json
{
  "detail": "Bookstore not found"
}
```

---

### 4. Get Bookstore Books
**Endpoint:** `GET /care/bookstores/{bookstore_id}/books`

**Description:** Lấy danh sách sách có sẵn tại nhà sách

**Response (200):**
```json
{
  "bookstore_id": 1,
  "books": [
    {
      "id": 1,
      "book_id": 123,
      "bookstore_id": 1,
      "purchase_url": "https://fahasa.com/book/123",
      "price": 150000,
      "stock_status": "available",
      "created_at": "2024-01-15T10:30:00"
    }
  ]
}
```

---

## 📚 Book Purchase Links APIs

### 1. Add Book Purchase Link
**Endpoint:** `POST /care/bookstores/book-links`

**Description:** Nhà sách thêm link bán sách của mình

**Request:**
```json
{
  "book_id": 123,
  "bookstore_id": 1,
  "purchase_url": "https://fahasa.com/book/123",
  "price": 150000,
  "stock_status": "available"
}
```

**Notes:**
- `stock_status` có thể là: `"available"`, `"out_of_stock"`, `"pre_order"`
- Nếu link đã tồn tại, sẽ cập nhật thông tin

**Response (200):**
```json
{
  "id": 1,
  "book_id": 123,
  "bookstore_id": 1,
  "purchase_url": "https://fahasa.com/book/123",
  "price": 150000,
  "stock_status": "available",
  "created_at": "2024-01-15T10:30:00"
}
```

---

### 2. Get Book Purchase Links (PRIORITY SORTING)
**Endpoint:** `GET /care/books/{book_id}/purchase-links?user_latitude=10.7769&user_longitude=106.7009`

**Description:** Lấy danh sách link mua sách, được ưu tiên theo:
1. Khoảng cách từ user đến nhà sách (nếu có GPS)
2. Tỷ lệ hoa hồng (cao hơn = ưu tiên hơn)

**Query Parameters:**
- `user_latitude` (float, optional): Vĩ độ GPS của user
- `user_longitude` (float, optional): Kinh độ GPS của user

**Response (200):**
```json
{
  "book_id": 123,
  "total_links": 3,
  "sorted_by": "distance and commission_rate",
  "purchase_links": [
    {
      "id": 1,
      "book_id": 123,
      "purchase_url": "https://fahasa.com/book/123",
      "price": 150000,
      "stock_status": "available",
      "bookstore_id": 1,
      "bookstore_name": "Nhà sách Fahasa",
      "bookstore_address": "123 Nguyễn Huệ, Quận 1, TP.HCM",
      "bookstore_latitude": 10.7769,
      "bookstore_longitude": 106.7009,
      "bookstore_phone": "0901234567",
      "bookstore_website": "https://fahasa.com",
      "commission_rate": 15.5,
      "distance_km": 0.5
    },
    {
      "id": 2,
      "book_id": 123,
      "purchase_url": "https://tiki.vn/book/123",
      "price": 145000,
      "stock_status": "available",
      "bookstore_id": 2,
      "bookstore_name": "Tiki",
      "bookstore_address": "52 Út Tịch, Tân Bình, TP.HCM",
      "bookstore_latitude": 10.8023,
      "bookstore_longitude": 106.6504,
      "bookstore_phone": "0909876543",
      "bookstore_website": "https://tiki.vn",
      "commission_rate": 12.0,
      "distance_km": 5.2
    }
  ]
}
```

**Response khi không có GPS (200):**
```json
{
  "book_id": 123,
  "total_links": 2,
  "sorted_by": "commission_rate only",
  "purchase_links": [
    {
      "id": 1,
      "book_id": 123,
      "purchase_url": "https://fahasa.com/book/123",
      "price": 150000,
      "stock_status": "available",
      "bookstore_id": 1,
      "bookstore_name": "Nhà sách Fahasa",
      "bookstore_address": "123 Nguyễn Huệ, Quận 1, TP.HCM",
      "bookstore_latitude": 10.7769,
      "bookstore_longitude": 106.7009,
      "bookstore_phone": "0901234567",
      "bookstore_website": "https://fahasa.com",
      "commission_rate": 15.5,
      "distance_km": null
    }
  ]
}
```

**Use Cases:**
1. **Khi user làm bài test cảm xúc**: Sau khi nhận được gợi ý sách, frontend gọi API này với `book_id` của từng sách được gợi ý
2. **Với GPS**: Pass `user_latitude` và `user_longitude` từ HTML5 Geolocation API
3. **Không có GPS**: Không pass GPS parameters, sẽ sort theo commission rate

**Frontend Integration:**
```javascript
// Lấy GPS từ browser
navigator.geolocation.getCurrentPosition(async (position) => {
  const { latitude, longitude } = position.coords;
  
  // Gọi API với GPS
  const response = await fetch(
    `/care/books/${bookId}/purchase-links?user_latitude=${latitude}&user_longitude=${longitude}`
  );
  const data = await response.json();
  
  // Hiển thị danh sách link, đã được sort theo khoảng cách
  displayPurchaseLinks(data.purchase_links);
});
```

---

## 📊 Integration Flow

### Complete User Journey:

1. **User đăng nhập** → Nhận JWT token
2. **Làm bài test cảm xúc** → Nhận emotional profile + gợi ý sách
3. **Xem chi tiết sách** → Gọi `/books/{book_id}/purchase-links` với GPS
4. **Chọn nhà sách gần nhất** → Click vào link mua hàng
5. **Mua sách** → Nhà sách nhận hoa hồng

### Bookstore Journey:

1. **Nhà sách đăng ký** → `POST /bookstores/register`
2. **Thêm link bán sách** → `POST /bookstores/book-links` cho mỗi sách
3. **User xem sách** → Nhà sách được ưu tiên theo GPS + commission
4. **User click link** → Nhà sách nhận traffic + conversion

---

This documentation provides complete API specification for the frontend team to implement Caelio Care features!