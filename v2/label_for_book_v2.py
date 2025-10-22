import pandas as pd
import numpy as np
import re
from collections import Counter
import io  # Nếu dùng string; bỏ nếu load file

# === LOAD DỮ LIỆU ===
book_file_path = '../dataset/books_full_data.csv'
df_books = pd.read_csv(book_file_path, encoding='utf-8')
print(f"✅ Loaded {len(df_books)} books from: {book_file_path}")

# === ĐỊNH NGHĨA GROUPS KEYWORDS MỞ RỘNG (THÊM TỪ ĐƠN TIẾNG VIỆT, BIẾN THỂ) ===
groups_keywords = {
    'Chinh phục': ['khởi nghiệp', 'phát triển bản thân', 'tự lực', 'vươn lên', 'nghèo khó', 'truyền cảm hứng', 'kỷ luật', 'năng suất', 'lãnh đạo', 'kiên cường', 'thất bại', 'nghịch cảnh', 'bản lĩnh', 'động lực', 'tư duy', 'doanh nhân', 'vượt khó', 'nghị lực', 'hồi ký', 'thành công'],  # Thêm từ đơn
    'Kiến tạo': ['sáng tạo', 'nghệ thuật', 'thiết kế', 'hiện đại', 'hậu hiện đại', 'thử nghiệm', 'tiểu luận', 'triết học', 'bản ngã', 'tự do cá nhân', 'chữa lành', 'hòa giải', 'tự sự', 'phong cách sống', 'design thinking', 'thơ ca', 'văn học sáng tạo'],
    'Tri thức': ['khoa học', 'lịch sử', 'tư tưởng', 'tâm lý học', 'stoicism', 'mindfulness', 'xã hội học', 'triết học', 'công nghệ', 'tư duy phản biện', 'nhận thức', 'non fiction', 'biography', 'nhà khoa học', 'viễn tưởng khoa học', 'xã hội'],
    'Tự do': ['du hành', 'phiêu lưu', 'hiện sinh', 'dystopia', 'phản kháng', 'kafka', 'orwell', 'camus', 'tự do tinh thần', 'du lịch', 'nội tâm', 'siêu thực', 'eat pray love', 'wild', 'flow', 'truyện ngắn'],
    'Kết nối': ['tình cảm', 'gia đình', 'xã hội', 'tản văn', 'cảm xúc', 'đồng cảm', 'chữa lành', 'tâm lý', 'giao tiếp', 'mối quan hệ', 'nhân văn', 'mất mát', 'xung đột', 'feel good', 'tình yêu'],
    'Đa động lực': ['đa tuyến', 'murakami', 'márquez', 'tổng hợp', 'sapiens', 'ký sự', 'tạp văn', 'giao thoa', 'đa tầng', 'phản tư', 'suy tưởng', 'hybrid', 'nhiều lớp', 'mở kết']  # Giữ ít để fallback
}
groups = list(groups_keywords.keys())

# Split keywords thành từ đơn để match tốt hơn (trước khi dùng)
def split_keywords(kws):
    split_kws = []
    for kw in kws:
        # Split cụm thành từ (giả sử space-separated)
        split_kws.extend(kw.split())
    return list(set(split_kws))  # Unique

# Pre-split all
for group in groups:
    groups_keywords[group] = split_keywords(groups_keywords[group])

# === CLEAN TEXT (GIẢM STOP WORDS ĐỂ GIỮ TỪ QUAN TRỌNG) ===
def clean_text(text):
    if pd.isna(text):
        return []
    text = str(text).lower()
    text = re.sub(r'[^\w\sáàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđ]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    words = text.split()
    # Giảm stop words (chỉ cơ bản, bỏ noisy dài)
    stop_words_basic = {'của', 'và', 'là', 'có', 'một', 'những', 'để', 'cho', 'tôi', 'mình', 'này', 'với', 'như', 'bạn', 'các', 'mà', 'đã', 'trong', 'từ', 'khi', 'thì', 'họ', 'ra', 'lại', 'đi', 'cũng', 'về', 'trên', 'dưới', 'gì', 'ai', 'nào', 'không', 'còn', 'được', 'làm', 'bị', 'cách', 'thế', 'tiki', 'nhà', 'xuất', 'bản'}
    words = [w for w in words if len(w) > 1 and w not in stop_words_basic]  # Giảm len>2 xuống >1, ít stop hơn
    return words

# === GÁN NHÃN (CẢI THIỆN: MATCH TỪ ĐƠN, THÊM N-GRAM NGẮN, GIẢM THRESHOLD) ===
def assign_labels_detailed(row):
    score_dict = {g: 0.0 for g in groups}
    
    # Metadata text (title + authors + category + summary, weight 0.5 - tăng vì đáng tin hơn content)
    text_metadata = (str(row.get('title', '')) + ' ' + str(row.get('authors', '')) + ' ' + 
                     str(row.get('category', '')) + ' ' + str(row.get('summary', ''))).lower()
    words_meta = clean_text(text_metadata)
    
    # Thêm n-gram 2 từ cho metadata (để bắt cụm ngắn)
    ngrams_meta = [' '.join(words_meta[i:i+2]) for i in range(len(words_meta)-1)]
    all_meta = words_meta + ngrams_meta
    
    for group, kws in groups_keywords.items():
        # Exact/partial trên words + ngrams
        exact_matches = sum(1 for word in all_meta if any(kw == word for kw in kws))
        partial_matches = sum(1 for word in all_meta if any(kw in word or word in kw for kw in kws))
        score_dict[group] += (exact_matches + partial_matches * 0.7) / max(len(kws), 1) * 0.5  # Tăng partial weight
    
    # Comments text (weight 0.5)
    comments_text = str(row.get('content', ''))
    if comments_text.strip():
        words_comments = clean_text(comments_text)
        ngrams_comments = [' '.join(words_comments[i:i+2]) for i in range(len(words_comments)-1)]
        all_comments = words_comments + ngrams_comments
        for group, kws in groups_keywords.items():
            exact_matches = sum(1 for word in all_comments if any(kw == word for kw in kws))
            partial_matches = sum(1 for word in all_comments if any(kw in word or word in kw for kw in kws))
            score_dict[group] += (exact_matches + partial_matches * 0.7) / max(len(kws), 1) * 0.5
    
    # Normalize
    total = sum(score_dict.values())
    if total > 0:
        for g in score_dict:
            score_dict[g] = score_dict[g] / total
    
    # Primary: Top, threshold GIẢM XUỐNG 0.15
    top_group = max(score_dict, key=score_dict.get)
    if max(score_dict.values()) < 0.15:  # Giảm để tăng đa dạng
        top_group = 'Đa động lực'
    
    return pd.Series({
        'group_scores': str(score_dict),
        'primary_group': top_group,
        'group_score': score_dict[top_group]
    })

# Áp dụng và lưu
df_books_labeled = df_books.apply(assign_labels_detailed, axis=1)
df_books_labeled = pd.concat([df_books.reset_index(drop=True), df_books_labeled], axis=1)
df_books_labeled.to_csv('labeled_books_fixed.csv', index=False, encoding='utf-8')

# Verify
print("Kết quả gán nhãn mẫu (top 10):")
sample_cols = ['product_id', 'title', 'category', 'primary_group', 'group_score']
print(df_books_labeled[sample_cols].head(10).to_string(index=False))
print("\nPhân bố primary_group sau fix:")
print(df_books_labeled['primary_group'].value_counts())