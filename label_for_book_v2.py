import pandas as pd
import numpy as np
import re
from collections import Counter
import io  # Nếu dùng string; bỏ nếu load file

# === LOAD DỮ LIỆU (THAY BẰNG FILE THỰC TẾ) ===
df_books = pd.read_csv('dataset/book_data.csv')
df_comments = pd.read_csv('dataset/comments.csv')
df_summary = pd.read_csv('dataset/summary.csv')  # File mới: product_id, summary

# Merge summary vào df_books để dễ xử lý
df_books = pd.merge(df_books, df_summary, on='product_id', how='left')

# === KEYWORDS TIẾNG VIỆT TỐT HỚN (DỰA TRÊN SUMMARY THỰC TẾ) ===
groups_keywords = {
    'Chinh phục': ['vươn lên', 'nghèo khó', 'khó khăn', 'nghịch cảnh', 'vượt qua', 'bản lĩnh', 'kiên định', 'động lực', 'khởi nghiệp', 'thành công', 'phát triển', 'cố gắng', 'nỗ lực', 'chiến thắng', 'mục tiêu', 'ý chí', 'quyết tâm', 'thử thách', 'đấu tranh', 'tự lập', 'tự cường'],
    'Kiến tạo': ['sáng tạo', 'nghệ thuật', 'thiết kế', 'chữa lành', 'hòa giải', 'nội tâm', 'tự sự', 'biểu đạt', 'cảm hứng', 'tưởng tượng', 'thơ ca', 'văn chương', 'suy ngẫm', 'chiêm nghiệm', 'khám phá', 'tìm kiếm', 'phát hiện', 'trải nghiệm', 'cá nhân', 'bản thân'],
    'Tri thức': ['khoa học', 'giải thích', 'phân tích', 'địa lý', 'chính trị', 'văn hóa', 'tâm lý học', 'lịch sử', 'triết học', 'kiến thức', 'học hỏi', 'hiểu biết', 'nghiên cứu', 'khám phá', 'tư duy', 'logic', 'lý thuyết', 'phương pháp', 'giáo dục', 'trí tuệ', 'nhận thức'],
    'Tự do': ['tự do', 'độc lập', 'phiêu lưu', 'hành trình', 'du lịch', 'khám phá', 'mạo hiểm', 'giải phóng', 'thoát khỏi', 'thao túng', 'kiểm soát', 'lựa chọn', 'quyết định', 'bình thản', 'thư giãn', 'thoải mái', 'tự nhiên', 'không ràng buộc', 'tự chủ', 'không phụ thuộc'],
    'Kết nối': ['gia đình', 'tình cảm', 'yêu thương', 'quan hệ', 'mối quan hệ', 'cảm xúc', 'đồng cảm', 'thấu hiểu', 'chia sẻ', 'gắn kết', 'kết nối', 'tương tác', 'giao tiếp', 'trầm cảm', 'cô đơn', 'mất mát', 'nỗi đau', 'buồn', 'vui', 'hạnh phúc', 'tình yêu'],
    'Đa động lực': ['giao thoa', 'đa tầng', 'phức tạp', 'nhiều chiều', 'tổng hợp', 'kết hợp', 'hỗn hợp', 'đa dạng', 'phong phú', 'đan xen', 'xen kẽ', 'luân phiên', 'thay đổi', 'biến đổi', 'chuyển tiếp', 'linh hoạt', 'thích ứng', 'đa năng', 'toàn diện', 'rộng rãi', 'bao trùm']
}
groups = list(groups_keywords.keys())

# === CLEAN TEXT ĐƠN GIẢN VÀ HIỆU QUẢ ===
def clean_text(text):
    if pd.isna(text):
        return []
    text = str(text).lower()
    # Giữ tiếng Việt: Loại dấu câu/emoji/số, nhưng giữ accent
    text = re.sub(r'[^\w\sáàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđ]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    words = text.split()
    # Stop words cơ bản (chỉ giữ những từ thực sự không có ý nghĩa)
    stop_words_basic = {'của', 'và', 'là', 'có', 'một', 'những', 'để', 'cho', 'tôi', 'mình', 'sách', 'cuốn', 'này', 'với', 'như', 'bạn', 'các', 'mà', 'đã', 'trong', 'từ', 'khi', 'thì', 'họ', 'ra', 'lại', 'đi', 'cũng', 'về', 'trên', 'dưới', 'gì', 'ai', 'nào', 'không', 'còn', 'được', 'làm', 'bị', 'cách', 'thế', 'tiki', 'nhà', 'xuất', 'bản'}
    words = [w for w in words if len(w) > 2 and w not in stop_words_basic]
    return words

# === GÁN NHÃN ĐƯỢC CẢI THIỆN (TĂNG IMPACT CỦA SUMMARY) ===
def assign_labels_detailed(row, df_comments):
    score_dict = {g: 0.0 for g in groups}
    
    # 1. Summary text (weight 0.6 - QUAN TRỌNG NHẤT)
    text_summary = str(row.get('summary', ''))
    words_summary = clean_text(text_summary)
    # Debug chỉ cho sách đầu tiên
    if row.get('product_id') == 74021317:
        print(f"Đang xử lý: {row.get('title', 'Unknown')}")
        print(f"Summary words: {words_summary[:10]}...")
    
    for group, kws in groups_keywords.items():
        matches = 0
        matched_words = []
        
        # Exact match (điểm cao)
        for word in words_summary:
            for kw in kws:
                if kw == word:
                    matches += 2.0  # Điểm cao cho exact match
                    matched_words.append(word)
                elif kw in word or word in kw:
                    matches += 1.0  # Điểm thấp hơn cho partial match
                    matched_words.append(f"{word}~{kw}")
        
        if matches > 0:
            print(f"  {group}: {matches} matches {matched_words[:3]}")
        
        score_dict[group] += matches * 0.6  # Không chia cho len(kws) để giữ impact
    
    # 2. Metadata text (title + category, weight 0.2)
    text_metadata = (str(row.get('title', '')) + ' ' + str(row.get('category', '')))
    words_meta = clean_text(text_metadata)
    
    for group, kws in groups_keywords.items():
        matches = sum(2.0 if any(kw == word for kw in kws) else 
                     1.0 if any(kw in word or word in kw for kw in kws) else 0 
                     for word in words_meta)
        score_dict[group] += matches * 0.2
    
    # 3. Comments text (weight 0.2 - giảm xuống vì ít reliable)
    comments = df_comments[df_comments['product_id'] == row['product_id']]['content'].dropna()
    if not comments.empty and len(comments) > 0:
        # Chỉ lấy 3 comments đầu để tránh noise
        sample_comments = comments.head(3)
        all_comments_text = ' '.join(sample_comments)
        words_comments = clean_text(all_comments_text)
        
        for group, kws in groups_keywords.items():
            matches = sum(1.0 if any(kw == word for kw in kws) else 
                         0.5 if any(kw in word or word in kw for kw in kws) else 0 
                         for word in words_comments[:50])  # Giới hạn words để tránh quá tải
            score_dict[group] += matches * 0.2
    
    # 4. Normalize và chọn primary (CẢI THIỆN)
    total = sum(score_dict.values())
    if total > 0:
        for g in score_dict:
            score_dict[g] = score_dict[g] / total
    else:
        # Nếu không match gì, đặt default
        score_dict['Đa động lực'] = 1.0
    
    # Primary group với threshold thấp hơn
    top_group = max(score_dict, key=score_dict.get)
    top_score = max(score_dict.values())
    
    print(f"  Final scores: {dict(sorted(score_dict.items(), key=lambda x: x[1], reverse=True))}")
    print(f"  Primary: {top_group} ({top_score:.3f})")
    
    return pd.Series({
        'group_scores': score_dict,  # Giữ dict thay vì string
        'primary_group': top_group,
        'group_score': top_score
    })

# Áp dụng và lưu CSV
df_books_labeled = df_books.apply(lambda row: assign_labels_detailed(row, df_comments), axis=1)
df_books_labeled = pd.concat([df_books.reset_index(drop=True), df_books_labeled], axis=1)

# Convert group_scores dict thành string để lưu CSV
df_books_labeled['group_scores'] = df_books_labeled['group_scores'].apply(lambda x: str(x) if isinstance(x, dict) else str(x))

df_books_labeled.to_csv('labeled_books_v3.csv', index=False, encoding='utf-8')

# Verify (in ra để kiểm tra)
print("Kết quả gán nhãn mẫu:")
print(df_books_labeled[['product_id', 'title', 'category', 'primary_group', 'group_score', 'group_scores']])
print("\nPhân bố primary_group (để kiểm tra không sai lệch):")
print(df_books_labeled['primary_group'].value_counts())