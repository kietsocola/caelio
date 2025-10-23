## Câu hỏi mở đầu
Khi đến với Caelio, bạn đang tìm kiếm điều gì?
A. Một cuốn sách khiến tôi nhìn thấy chính mình theo một cách mới. ➡ Dành cho hành trình khám phá.
B. Một cuốn sách giúp tôi học, làm việc hoặc nghiên cứu hiệu quả hơn. ➡ Dành cho hành trình chuyên

### 1. Health Check
```http
GET /health
```

### 2. Tất cả câu hỏi theo mỗi loại sau khi use chọn
```http
GET /questions?question_type=discovery
GET /questions?question_type=professional
```

### 3. API tổng hợp (Phân tích + Gợi ý)

#### Hành trình khám phá (tổng hợp)
```http
POST /discover?top_n=5
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
POST /professional?top_n=5
```

Trả về cả analysis + recommendations trong 1 API call.

**Request Body:**
```json
{
  "Q1": "A",
  "Q2": "B",
  "Q3": "B",
  "Q4": "B"
}
```