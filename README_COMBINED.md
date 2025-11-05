# Caelio Combined API - Comprehensive Bibliotherapy System

## 🌟 Overview
Hệ thống bibliotherapy tổng hợp kết hợp 2 API:
- **Personality API**: Đánh giá tính cách và gợi ý sách theo archetype
- **Caelio Care API**: Đánh giá cảm xúc PERMA-DASS và tính năng "sách trắng"

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements_api.txt
```

### 2. Setup PostgreSQL (for Caelio Care)
```bash
# Create database
createdb caelio_care
```

### 3. Run Combined Server
```bash
python run_api.py
```

### 4. Test Everything
```bash
python test_combined_api.py
```

## 📍 API Endpoints

### 🏠 Main Server (localhost:8000)
- `GET /` - Root endpoint with service info
- `GET /health` - Combined health check
- `GET /docs` - Main API documentation

### 🧠 Personality API (localhost:8000/personality)
- `GET /personality/questions` - Get personality questions
- `POST /personality/analyze` - Analyze personality (3 or 8 questions)
- `POST /personality/discover` - Complete analysis + book recommendations
- `POST /personality/professional` - Professional journey analysis
- `GET /personality/books` - List books with pagination
- `GET /personality/books/{id}` - Book detail with comments

### 💚 Caelio Care API (localhost:8000/care)
- `POST /care/auth/register` - Register user
- `POST /care/auth/login` - Login user
- `GET /care/emotional-test/questions` - Get PERMA-DASS questions
- `POST /care/emotional-test/analyze` - Analyze emotional state → layer
- `GET /care/emotional-test/prescription/{layer}` - Get book prescription
- `POST /care/white-books/create` - Create user book
- `GET /care/white-books/published` - Browse community books
- `GET /care/writing-prompts/{layer}` - Get writing prompts

## 🧮 System Logic

### Personality Assessment (Archetype)
```
3-8 Questions → Personality Groups:
├── Kết nối (Connectors)
├── Tự do (Individuals) 
├── Tri thức (Thinkers)
├── Chinh phục (Achievers)
└── Kiến tạo (Builders)
+ Synthesizer detection
```

### Emotional Assessment (PERMA-DASS)
```
9 Questions (1-5 scale) → Emotional Layers:
├── PERMA (Q1-Q5): Positive emotions
├── DASS (Q6-Q9): Negative emotions  
├── MBI = PERMA - DASS
└── Layer: Nhận diện → Chấp nhận → Hồi phục → Tái sinh
```

### Combined Recommendation
```
Archetype + Emotional Layer → Personalized Prescription:
├── Books (từ database + white books)
├── Movies 
├── Writing prompts
└── State-based personalization
```

## 🎯 Complete User Journey

### 1. Assessment Phase
```bash
# Step 1: Personality assessment
curl -X POST "http://localhost:8000/personality/discover" \
  -H "Content-Type: application/json" \
  -d '{"Q1": "A", "Q2": "C", "Q3": "E"}'

# Result: Archetype (e.g., "Tri thức")
```

### 2. Registration & Emotional Assessment  
```bash
# Step 2: Register for Caelio Care
curl -X POST "http://localhost:8000/care/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser", 
    "password": "password123"
  }'

# Step 3: Emotional assessment
curl -X POST "http://localhost:8000/care/emotional-test/analyze" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "Q1": 4, "Q2": 3, "Q3": 3, "Q4": 4, "Q5": 3,
    "Q6": 2, "Q7": 3, "Q8": 2, "Q9": 1
  }' \
  -G --data-urlencode "archetype=Tri thức"

# Result: Emotional Layer (e.g., "Hồi phục") + MBI Score
```

### 3. Personalized Recommendations
```bash
# Step 4: Get combined prescription
curl "http://localhost:8000/care/emotional-test/prescription/Hồi phục?archetype=Tri thức"

# Result: Books + Movies + Writing Prompts tailored for "Tri thức in Hồi phục phase"
```

### 4. Content Creation
```bash
# Step 5: Create white book based on prompts
curl -X POST "http://localhost:8000/care/white-books/create" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Hành trình tìm lại cân bằng",
    "content": "...",
    "emotional_layer": "Hồi phục",
    "prompt_used": "Hôm nay bạn biết ơn điều gì?"
  }'

# Step 6: Publish to community
curl -X PUT "http://localhost:8000/care/white-books/{book_id}/publish" \
  -H "Authorization: Bearer {token}"
```

## 🔄 Integration Benefits

### 1. **Dual Assessment System**
- **Personality**: Stable traits (archetype)
- **Emotional**: Current state (layer) 
- **Combined**: More accurate recommendations

### 2. **Progressive User Journey**
- Start with quick personality test (no auth required)
- Upgrade to full emotional assessment (with auth)
- Create and share content in community

### 3. **Community & Content**
- Users create books for their emotional layer
- Others in same state can read and relate
- Peer-to-peer bibliotherapy support

### 4. **Unified Data**
- Single server, unified logging
- Cross-system analytics possible
- Integrated user experience

## 📊 Example Complete Flow

```python
# 1. Quick personality check (no auth)
personality = assess_personality(["A", "C", "E"])
# → "Tri thức" (Knowledge Seeker)

# 2. Register & emotional assessment (with auth)  
register_user("user@email.com", "password")
emotional = assess_emotions([4,3,3,4,3,2,3,2,1], archetype="Tri thức")  
# → "Hồi phục" (Recovery phase)

# 3. Get combined prescription
prescription = get_prescription("Hồi phục", archetype="Tri thức")
# → Academic books + Recovery themes + Reflective prompts

# 4. Create content & contribute
write_book(prescription.prompts[0])  # "Hôm nay bạn biết ơn điều gì?"
publish_to_community()

# 5. Browse others' content  
read_community_books(emotional_layer="Hồi phục")
```

## 🛠️ Development

### File Structure
```
├── run_api.py                 # Combined server launcher
├── caelio_api.py             # Main personality API
├── caelio_care/              # Emotional assessment system
│   ├── main.py               # Care API endpoints
│   ├── auth.py               # JWT authentication
│   ├── emotional_system.py   # PERMA-DASS logic
│   ├── white_books.py        # User content system
│   └── database.py           # PostgreSQL connection
├── test_combined_api.py      # Comprehensive testing
└── requirements_api.txt      # All dependencies
```

### Port & URLs
- **Single Server**: localhost:8000
- **Personality API**: /personality/*
- **Caelio Care API**: /care/*  
- **Documentation**: /docs, /personality/docs, /care/docs

### Database Requirements
- **Personality API**: CSV files (existing data)
- **Caelio Care**: PostgreSQL (user data, white books)

## 🎉 Result

Bạn đã có một **hệ thống bibliotherapy hoàn chỉnh** trên 1 server duy nhất:

✅ **Assessment**: Personality + Emotional state  
✅ **Recommendations**: Books + Movies + Writing prompts  
✅ **Community**: User-generated white books  
✅ **Authentication**: Secure user accounts  
✅ **Scalability**: Modular architecture, easy to extend  

Chạy `python run_api.py` và trải nghiệm toàn bộ hệ thống! 🚀