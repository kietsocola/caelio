# Caelio Personality API Documentation

REST API cho hệ thống phân loại tính cách đọc sách Caelio.

## 🚀 Khởi chạy API

### Cài đặt dependencies
```bash
pip install -r requirements_api.txt
```

### Chạy API
```bash
python run_api.py
```

API sẽ chạy tại: `http://localhost:8000`

- **Swagger Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 📋 API Endpoints

### 1. Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "message": "API is running"
}
```

### 2. Lấy câu hỏi

#### Tất cả câu hỏi
```http
GET /questions?question_type=discovery
GET /questions?question_type=professional
```

**Parameters:**
- `question_type`: `discovery` (hành trình khám phá) hoặc `professional` (hành trình chuyên ngành)

#### Câu hỏi cụ thể
```http
GET /questions/{question_id}?question_type=discovery
GET /questions/{question_id}?question_type=professional
```

**Response Example (Discovery):**
```json
{
  "Q1": {
    "question": "Nếu một cuốn sách có linh hồn, linh hồn ấy nên làm gì cùng bạn?",
    "choices": {
      "A": {
        "text": "Cùng bạn đi qua những vùng cảm xúc sâu thẳm, để hiểu và được hiểu.",
        "group": "Kết nối",
        "synthesizer": false
      }
    }
  }
}
```

**Response Example (Professional):**
```json
{
  "Q1": {
    "question": "Lĩnh vực bạn muốn đào sâu là gì?",
    "choices": {
      "A": {
        "text": "Kinh tế - Quản Trị - Tài chính",
        "field": "business"
      }
    }
  }
}
```

### 3. Phân tích tính cách

#### Hành trình khám phá
```http
POST /analyze
```

**Request Body:**
```json
{
  "Q1": "C",
  "Q2": "D",
  "Q3": "E",
  "Q4": "C",
  "Q5": "B",
  "Q6": "E",
  "Q7": "C",
  "Q8": "C"
}
```

#### Hành trình chuyên ngành
```http
POST /analyze-professional
```

**Request Body:**
```json
{
  "discovery_answers": {
    "Q1": "C",
    "Q2": "D",
    "Q3": "E",
    "Q4": "C",
    "Q5": "B",
    "Q6": "E",
    "Q7": "C",
    "Q8": "C"
  },
  "professional_answers": {
    "Q1": "A",
    "Q2": "B",
    "Q3": "B",
    "Q4": "C"
  }
}
```

**Request Body:**
```json
{
  "Q1": "A",
  "Q2": "B", 
  "Q3": "C",
  "Q4": "D",
  "Q5": "E",
  "Q6": "A",
  "Q7": "B",
  "Q8": "C"
}
```

**Response:**
```json
{
  "primary_group": "Tri thức",
  "secondary_group": "Kiến tạo",
  "primary_score": 4,
  "secondary_score": 2,
  "synthesizer_score": 6,
  "is_synthesizer": true,
  "profile_name": "Thinker–Synthesizer",
  "english_name": "The Analytical Synthesizer",
  "all_scores": {
    "Kết nối": 1,
    "Tự do": 0,
    "Tri thức": 4,
    "Chinh phục": 1,
    "Kiến tạo": 2
  },
  "is_multi_motivated": false,
  "description": {
    "title": "🧠 The Thinkers - Người Tư duy",
    "description": "Bạn tìm kiếm tri thức, sự thật và lý giải thế giới...",
    "books": "Khoa học phổ thông, triết học, lịch sử...",
    "traits": "Hiếu học, logic, thích phân tích và tìm hiểu",
    "synthesizer_note": "🔗 Đặc điểm Synthesizer: Bạn có khả năng tư duy tổng hợp cao..."
  }
}
```

### 4. Gợi ý sách

#### Hành trình khám phá
```http
POST /recommend?top_n=20
```

**Request Body:** (giống /analyze)

#### Hành trình chuyên ngành  
```http
POST /recommend-professional?top_n=20
```

**Request Body:** (Giống /analyze-professional)
```json
{
  "discovery_answers": {
    "Q1": "C",
    "Q2": "D",
    "Q3": "E",
    "Q4": "C",
    "Q5": "B",
    "Q6": "E",
    "Q7": "C",
    "Q8": "C"
  },
  "professional_answers": {
    "Q1": "A",
    "Q2": "B",
    "Q3": "B",
    "Q4": "C"
  }
}
```

**Response:**
```json
{
  "profile": { /* PersonalityProfile object */ },
  "recommendations": [
    {
      "product_id": "12345",
      "title": "Sapiens: Lược sử loài người", 
      "authors": "Yuval Noah Harari",
      "category": "Lịch sử",
      "summary": "Cuốn sách về lịch sử nhân loại...",
      "personality_match_score": 0.95,
      "cover_link": "https://example.com/cover.jpg"
    }
  ],
  "total_matches": 150,
  "match_distribution": {
    "Lịch sử": 25,
    "Khoa học": 30,
    "Triết học": 20
  }
}
```

### 5. Danh sách nhóm tính cách
```http
GET /groups
```

### 6. Thống kê hệ thống
```http
GET /stats
```

### 7. API tổng hợp (Phân tích + Gợi ý)

#### Hành trình khám phá (tổng hợp)
```http
POST /discover?top_n=20
```

Trả về cả analysis + recommendations trong 1 API call.

**Request Body:**
```json
{
  "Q1": "C",
  "Q2": "D",
  "Q3": "E",
  "Q4": "C",
  "Q5": "B",
  "Q6": "E",
  "Q7": "C",
  "Q8": "C"
}
```

#### Hành trình chuyên ngành (tổng hợp)
```http
POST /professional?top_n=20
```

Trả về cả analysis + recommendations trong 1 API call.

**Request Body:** (Giống /analyze-professional)
```json
{
  "discovery_answers": {
    "Q1": "C",
    "Q2": "D",
    "Q3": "E",
    "Q4": "C",
    "Q5": "B",
    "Q6": "E",
    "Q7": "C",
    "Q8": "C"
  },
  "professional_answers": {
    "Q1": "A",
    "Q2": "B",
    "Q3": "B",
    "Q4": "C"
  }
}
```

### 8. Test endpoint
```http
POST /test/example
```

## 🔧 Cách sử dụng trong Frontend

### JavaScript/React Example
```javascript
class CaelioAPI {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }
  
  async analyzePersonality(answers) {
    const response = await fetch(`${this.baseUrl}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(answers)
    });
    return response.json();
  }
  
  async getRecommendations(answers, topN = 20) {
    const response = await fetch(`${this.baseUrl}/recommend?top_n=${topN}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(answers)
    });
    return response.json();
  }
}

// Usage
const api = new CaelioAPI();
const answers = {Q1: "A", Q2: "B", /* ... */};
const profile = await api.analyzePersonality(answers);
const books = await api.getRecommendations(answers, 10);
```

### Python Example
```python
import requests

# Phân tích tính cách
response = requests.post('http://localhost:8000/analyze', json={
    "Q1": "A", "Q2": "B", "Q3": "C", "Q4": "D",
    "Q5": "E", "Q6": "A", "Q7": "B", "Q8": "C"
})
profile = response.json()

# Lấy gợi ý sách
response = requests.post('http://localhost:8000/recommend', 
    json=answers, 
    params={"top_n": 10}
)
recommendations = response.json()
```

## 🔒 CORS Configuration

API được cấu hình với CORS cho phép tất cả origins (`allow_origins=["*"]`).

**Trong production, nên chỉ định cụ thể domain:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## 📊 Data Models

### PersonalityAnswers
- Q1-Q8: string (A, B, C, D, hoặc E)

### PersonalityProfile  
- primary_group: string
- secondary_group: string | null
- primary_score: int
- secondary_score: int
- synthesizer_score: int
- is_synthesizer: bool
- profile_name: string
- english_name: string
- all_scores: dict
- is_multi_motivated: bool
- description: dict

### BookRecommendation
- product_id: string/number
- title: string
- authors: string
- category: string
- summary: string
- personality_match_score: float (0-1)
- cover_link: string

## 🚨 Error Handling

API trả về HTTP status codes chuẩn:
- 200: Success
- 400: Bad Request (invalid answers)
- 404: Not Found (question/resource not found)
- 500: Internal Server Error

**Error Response Format:**
```json
{
  "detail": "Error message here"
}
```

## 🧪 Testing

Chạy test example:
```bash
python api_client_example.py
```

Hoặc sử dụng test endpoint:
```bash
curl -X POST http://localhost:8000/test/example
```

## 📁 File Requirements

API cần file dữ liệu sách:
- `dataset/books_full_data.csv` (preferred)
- `books_full_data.csv` (fallback)
- `v2/labeled_books_v2.csv` (fallback)

Nếu không tìm thấy, API sẽ trả về gợi ý thể loại chung.

## 🔄 Development Mode

Chạy với auto-reload:
```bash
uvicorn caelio_api:app --host 0.0.0.0 --port 8000 --reload
```