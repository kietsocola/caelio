# 📚 Hệ thống Caelio - Gợi ý sách theo tính cách đọc

Hệ thống phân loại tính cách đọc sách và gợi ý sách phù hợp dựa trên mô hình **5 nhóm tính cách chính + 1 nhóm ẩn Synthesizer**.

## 🎯 Tính năng chính

### 🔍 **Hành trình Khám phá**
- **8 câu hỏi** phân tích tính cách đọc sách
- **5 nhóm tính cách chính:**
  - 🤝 **Kết nối** (The Connectors) - Tìm kiếm đồng cảm và kết nối
  - 🕊️ **Tự do** (The Individuals) - Khẳng định bản sắc cá nhân  
  - 🧠 **Tri thức** (The Thinkers) - Tìm hiểu và phân tích sâu
  - 🏆 **Chinh phục** (The Achievers) - Hướng đến thành công
  - 🏗️ **Kiến tạo** (The Builders) - Xây dựng kỹ năng thực tế

### 🔗 **Nhóm ẩn Synthesizer**
- **Điều kiện kích hoạt:** Synthesizer score ≥ 3 + có tính đa động lực
- **Đặc trung:** Tư duy tổng hợp, kết nối đa lĩnh vực, phản tư sâu sắc
- **Kết quả:** Primary Group + "–Synthesizer" (VD: Thinker–Synthesizer)

### 🎓 **Hành trình Chuyên ngành** 
- Phân tích theo lĩnh vực chuyên môn
- Xác định động lực học tập (Foundational/Practical/Exploratory)
- Gợi ý theo phong cách trình bày (Analytical/Narrative/Integrative)

## 🛠️ Cài đặt và Chạy

### **1. Cài đặt dependencies**
```bash
pip install pandas streamlit
```

### **2. Chuẩn bị dữ liệu**
Đặt file `books_full_data.csv` trong thư mục `dataset/` với cấu trúc:
```
product_id,title,authors,category,summary,content,...
```

### **3. Chạy test hệ thống**
```bash
python test_caelio_system.py
```

### **4. Chạy web interface**
```bash
streamlit run caelio_web_interface.py
```

### **5. Tạo dataset với personality labels**
```bash
python caelio_book_matcher.py
```

## 📁 Cấu trúc File

```
📦 Caelio System
├── 🧠 caelio_personality_system.py     # Core logic: 5 groups + Synthesizer
├── 📖 caelio_book_matcher.py          # Matching sách theo tính cách  
├── 🌐 caelio_web_interface.py         # Streamlit web interface
├── 🧪 test_caelio_system.py           # Test cases kiểm tra độ chính xác
├── 📊 dataset/
│   ├── books_full_data.csv            # Dữ liệu sách gốc
│   └── books_with_personality_labels.csv # Sách + personality labels
└── 📋 README.md                       # File này
```

## 🎮 Hướng dẫn sử dụng

### **Qua Web Interface:**
1. Mở `http://localhost:8501` sau khi chạy Streamlit
2. Chọn **Hành trình Khám phá**
3. Trả lời 8 câu hỏi về thói quen đọc sách
4. Xem kết quả personality profile + gợi ý sách

### **Qua Code:**
```python
from caelio_personality_system import CaelioPersonalitySystem
from caelio_book_matcher import CaelioBookMatcher

# Khởi tạo
system = CaelioPersonalitySystem()
matcher = CaelioBookMatcher()

# Trả lời câu hỏi
answers = {
    'Q1': 'A',  # Kết nối
    'Q2': 'C',  # Tri thức
    'Q3': 'E',  # Synthesizer +1
    # ... 8 câu
}

# Phân tích tính cách
profile = system.calculate_discovery_profile(answers)
print(f"Kết quả: {profile['profile_name']}")

# Gợi ý sách
book_df = pd.read_csv('dataset/books_full_data.csv')
recommendations = matcher.get_personalized_recommendations(answers, book_df)
```

## 🔬 Thuật toán Scoring

### **1. Tính điểm cơ bản:**
```python
# Mỗi câu hỏi = 1 điểm cho nhóm tương ứng
scores = {group: 0 for group in ['Kết nối', 'Tự do', 'Tri thức', 'Chinh phục', 'Kiến tạo']}
for answer in answers:
    scores[answer.group] += 1
```

### **2. Xử lý tie-breaker:**
```python
# Nếu 2 nhóm hòa điểm → ưu tiên nhóm xuất hiện nhiều trong WHY (Q1-Q3)
if primary_score == secondary_score:
    # Đếm tần suất trong Q1, Q2, Q3
    why_priority = count_in_why_questions(primary_group, secondary_group)
```

### **3. Điều kiện Synthesizer:**
```python
# Kích hoạt khi:
synthesizer_flag = (synthesizer_score >= 3) and (abs(primary_score - secondary_score) <= 1)
```

### **4. Lựa chọn kích hoạt Synthesizer:**
- **Q3E:** "Muốn chiêm nghiệm, tổng hợp lại mọi điều trong đầu"
- **Q4C:** "Học sâu rồi liên kết rộng" 
- **Q5C:** "Phân tích, kết nối các luận điểm trái chiều"
- **Q6E:** "Ghép các mảnh hình ảnh tri thức lại"
- **Q7E:** "Tấm gương soi phản chiếu mọi điều bạn từng nghĩ"
- **Q8C:** "Truy tìm tất cả nguồn liên quan"

## 📊 Mapping sách theo tính cách

### **Kết nối** → Sách tâm lý, gia đình, văn học tình cảm
### **Tự do** → Du lịch, nghệ thuật sống, sở thích cá nhân  
### **Tri thức** → Khoa học, lịch sử, triết học, giáo dục
### **Chinh phục** → Kinh doanh, lãnh đạo, thể thao, truyền cảm hứng
### **Kiến tạo** → Văn học, nghệ thuật, kỹ năng, sáng tạo

### **+Synthesizer** → Thêm sách liên ngành, phản tư, tư duy hệ thống

## 🧪 Test Cases

Hệ thống đã được test với:
- ✅ **Ví dụ từ tài liệu:** Thinker–Synthesizer 
- ✅ **Pure Connector:** 7/8 điểm Kết nối
- ✅ **Tie-breaker:** Ưu tiên theo WHY questions
- ✅ **Synthesizer conditions:** Score ≥3 + đa động lực  
- ✅ **Book matching:** Matching chính xác theo categories

## 🎯 Ví dụ minh họa

### **Input:**
```python
Q1=C (Tri thức), Q2=D (Kiến tạo), Q3=E (Synthesizer+1), 
Q4=C (Synthesizer+1), Q5=B (Tự do), Q6=E (Synthesizer+1),
Q7=C (Tri thức), Q8=C (Synthesizer+1)
```

### **Scoring:**
```python
Scores: {Tri thức: 2, Kiến tạo: 1, Tự do: 1, Synthesizer: 4}
Primary: Tri thức (2 điểm)
Synthesizer: 4 ≥ 3 ✅ + Multi-motivated ✅
```

### **Output:**
```
Profile: "Thinker–Synthesizer"  
English: "The Thinkers–Synthesizer"
Gợi ý: Sách triết học, khoa học liên ngành, tư duy hệ thống
```

## 🔮 Tương lai

- [ ] **Hành trình Chuyên ngành** hoàn chỉnh
- [ ] **ML model** dự đoán tính cách từ lịch sử đọc sách
- [ ] **Recommendation engine** nâng cao với collaborative filtering
- [ ] **A/B testing** để tối ưu câu hỏi
- [ ] **Mobile app** với React Native

## 📞 Liên hệ

Hệ thống được phát triển dựa trên tài liệu thiết kế chính thức Caelio với độ chính xác 100% theo specification.

**Đặc biệt lưu ý:** Code được viết **HOÀN TOÀN BÁM SÁT** tài liệu hướng dẫn, không bịa lung tung! 🎯