# Caelio Care - Emotional Assessment and Bibliotherapy System

## Overview
Hệ thống đánh giá cảm xúc và liệu pháp sách dựa trên mô hình PERMA-DASS với 4 tầng cảm xúc.

## Features
- 🔐 **Authentication**: Đăng ký/đăng nhập với JWT
- 🧠 **Emotional Assessment**: Bộ câu hỏi 9 câu dựa trên PERMA-DASS
- 📚 **Book Prescription**: Gợi ý sách theo tầng cảm xúc
- ✍️ **White Books**: Tính năng viết sách của người dùng
- 🎯 **4 Emotional Layers**: Nhận diện → Chấp nhận → Hồi phục → Tái sinh

## Setup

### 1. Database Setup (PostgreSQL)
```bash
# Install PostgreSQL
# Create database
createdb caelio_care

# Or using psql
psql -U postgres
CREATE DATABASE caelio_care;
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
cd caelio_care
python -m uvicorn main:app --reload --port 8001
```

## API Endpoints

### Authentication
- `POST /auth/register` - Đăng ký
- `POST /auth/login` - Đăng nhập
- `GET /auth/me` - Thông tin user

### Emotional Assessment
- `GET /emotional-test/questions` - Lấy câu hỏi
- `POST /emotional-test/analyze` - Phân tích kết quả
- `GET /emotional-test/prescription/{layer}` - Gợi ý sách theo tầng
- `GET /emotional-test/my-results` - Lịch sử test

### White Books
- `POST /white-books/create` - Tạo sách mới
- `GET /white-books/my-books` - Sách của tôi
- `PUT /white-books/{id}/publish` - Xuất bản sách
- `GET /white-books/published` - Sách đã xuất bản
- `GET /white-books/{id}` - Chi tiết sách
- `GET /white-books/search/{query}` - Tìm kiếm sách

### Writing Prompts
- `GET /writing-prompts/{layer}` - Gợi ý chủ đề viết

## Emotional Layers System

### 1. Nhận diện (Recognize)
- **MBI Score**: ≤ -1.0
- **Mục tiêu**: Gọi tên cảm xúc, hợp thức hóa nỗi buồn
- **Sách gợi ý**: Haruki Murakami, Viktor Frankl
- **Writing Prompts**: "Điều khiến bạn mệt mỏi nhất gần đây là gì?"

### 2. Chấp nhận (Accept)  
- **MBI Score**: -1.0 to 0
- **Mục tiêu**: Đối thoại và sống cùng cảm xúc
- **Sách gợi ý**: Haemin Sunim, Brené Brown
- **Writing Prompts**: "Cảm xúc này đang dạy bạn điều gì?"

### 3. Hồi phục (Recover)
- **MBI Score**: 0 to 1.0  
- **Mục tiêu**: Tái kết nối năng lượng và tìm lại nhịp sống
- **Sách gợi ý**: Ikigai, Eckhart Tolle
- **Writing Prompts**: "Hôm nay bạn biết ơn điều gì?"

### 4. Tái sinh (Recreate)
- **MBI Score**: > 1.0
- **Mục tiêu**: Chuyển hóa tổn thương thành sáng tạo  
- **Sách gợi ý**: Brené Brown, James Clear
- **Writing Prompts**: "Nếu viết lại hành trình của mình, bạn muốn đặt tên cuốn sách là gì?"

## Database Schema

### Users
```sql
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

### Emotional Test Results
```sql
CREATE TABLE emotional_test_results (
    result_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    answers JSONB NOT NULL,
    perma_score FLOAT NOT NULL,
    dass_score FLOAT NOT NULL,
    mbi_score FLOAT NOT NULL,
    emotional_layer VARCHAR(50) NOT NULL,
    archetype VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### White Books
```sql
CREATE TABLE white_books (
    book_id SERIAL PRIMARY KEY,
    author_id INTEGER REFERENCES users(user_id),
    title VARCHAR(500) NOT NULL,
    category VARCHAR(100),
    content TEXT NOT NULL,
    emotional_layer VARCHAR(50),
    prompt_used TEXT,
    tags TEXT[],
    is_published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0
);
```

## Usage Examples

### 1. Register & Login
```python
import requests

# Register
response = requests.post("http://localhost:8001/auth/register", json={
    "email": "user@example.com",
    "username": "testuser",
    "password": "password123",
    "full_name": "Test User"
})
token = response.json()["access_token"]

# Use token for authenticated requests
headers = {"Authorization": f"Bearer {token}"}
```

### 2. Take Emotional Assessment
```python
# Get questions
questions = requests.get("http://localhost:8001/emotional-test/questions")

# Submit answers (1-5 scale)
answers = {
    "Q1": 3, "Q2": 4, "Q3": 2, "Q4": 3, "Q5": 4,
    "Q6": 3, "Q7": 2, "Q8": 1, "Q9": 2
}

result = requests.post(
    "http://localhost:8001/emotional-test/analyze",
    json=answers,
    headers=headers
)
profile = result.json()
print(f"Emotional Layer: {profile['emotional_layer']}")
print(f"MBI Score: {profile['mbi_score']}")
```

### 3. Create White Book
```python
book_data = {
    "title": "Hành trình tìm lại chính mình",
    "content": "Nội dung sách...",
    "emotional_layer": "Hồi phục",
    "prompt_used": "Hôm nay bạn biết ơn điều gì?",
    "tags": ["tự truyện", "hồi phục"]
}

book = requests.post(
    "http://localhost:8001/white-books/create",
    json=book_data,
    headers=headers
)
```

### 4. Get Book Prescription
```python
prescription = requests.get(
    "http://localhost:8001/emotional-test/prescription/Hồi phục"
)
recommended_books = prescription.json()["recommended_books"]
```

## Development Notes

- Port: 8001 (để tránh conflict với API chính)
- Database: PostgreSQL local
- Authentication: JWT tokens
- CORS: Enabled for all origins
- File structure: Modular design trong thư mục `caelio_care/`

## API Documentation
Khi chạy ứng dụng, truy cập: http://localhost:8001/docs