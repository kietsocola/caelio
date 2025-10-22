import pandas as pd
import numpy as np
import re
from collections import Counter
import io  # Nếu dùng string; bỏ nếu load file

# === LOAD DỮ LIỆU (THAY BẰNG FILE THỰC TẾ) ===
df_books = pd.read_csv('book_data.csv')
df_comments = pd.read_csv('comments.csv')
# === ĐỊNH NGHĨA GROUPS KEYWORDS MỞ RỘNG (TỪ DOC + BIẾN THỂ ĐỂ KHÔNG BỎ XÓT) ===
groups_keywords = {
    'Chinh phục': ['hồi ký khởi nghiệp', 'phát triển bản thân', 'tiểu thuyết hiện thực', 'vươn lên', 'nghèo khó', 'phi hư cấu truyền cảm hứng', 'kỷ luật', 'năng suất', 'leadership', 'resilience', 'thất bại', 'tái thiết', 'nghịch cảnh', 'bản lĩnh', 'động lực', 'grit', 'mindset', 'khởi nghiệp', 'doanh nhân', 'vượt nghịch cảnh', 'tái lập nghị lực'],
    'Kiến tạo': ['tiểu thuyết hiện đại', 'hậu hiện đại', 'văn học thử nghiệm', 'phi tuyến tính', 'tiểu luận', 'triết học bản ngã', 'tự do cá nhân', 'nghệ thuật', 'thiết kế', 'sáng tạo tư duy', 'art therapy', 'expressive writing', 'journaling', 'sáng tạo', 'bản ngã', 'tự truyện sáng tạo', 'phong cách sống', 'design thinking', 'thơ hậu hiện đại', 'chữa lành bản thân', 'hòa giải bản thân', 'tự sự nội tâm'],
    'Tri thức': ['khoa học phổ thông', 'non-fiction phân tích xã hội', 'lịch sử tư tưởng', 'tiểu thuyết ý niệm', 'philosophical fiction', 'speculative fiction', 'biographies thinker', 'inventors', 'tâm lý học', 'stoicism', 'mindfulness', 'phân tích xã hội', 'tư tưởng', 'nhà khoa học', 'lịch sử', 'khoa học viễn tưởng', 'triết học hiện đại', 'công nghệ', 'xã hội học', 'tư duy phản biện', 'nhận thức', 'lý thuyết xã hội'],
    'Tự do': ['hồi ký du hành', 'văn học phiêu lưu', 'triết học hiện sinh', 'tiểu thuyết dystopia', 'văn học phản kháng', 'kafka', 'orwell', 'camus', 'self-help tự do', 'travelogue', 'du hành nội tâm', 'hiện sinh', 'dystopia', 'phản kháng', 'tự do tinh thần', 'truyện ngắn tối giản', 'văn xuôi siêu thực', 'eat pray love', 'wild', 'flow', 'hiện sinh lạnh', 'phi nhân bản'],
    'Kết nối': ['tiểu thuyết tình cảm', 'gia đình', 'xã hội', 'văn học hiện sinh', 'tản văn nhân sinh', 'tâm lý học cảm xúc', 'giao tiếp', 'đồng cảm', 'chữa lành', 'tâm lý trị liệu', 'tình cảm', 'gia đình xã hội', 'tản văn', 'cảm xúc', 'đồng cảm', 'healing', 'tâm lý giao tiếp', 'feel-good', 'nhân văn', 'mối quan hệ', 'xung đột người với người', 'mất mát'],
    'Đa động lực': ['tiểu thuyết đa tuyến', 'murakami', 'márquez', 'non-fiction tổng hợp', 'sapiens', 'midnight library', 'ký triết lý', 'tạp văn', 'giao thoa xã hội tâm lý triết học công nghệ', 'đa tầng', 'phản tư', 'giao thoa', 'tổng hợp', 'suy tưởng', 'biên niên', 'hybrid literature', 'cloud atlas', 'catch-22', 'nhiều lớp cảm xúc', 'mở kết']
}
groups = list(groups_keywords.keys())

# === CLEAN TEXT NÂNG CAO (ĐỂ KHÔNG BỎ XÓT TỪ TIẾNG VIỆT) ===
def clean_text(text):
    if pd.isna(text):
        return []
    text = str(text).lower()
    # Giữ tiếng Việt: Loại dấu câu/emoji/số, nhưng giữ accent
    text = re.sub(r'[^\w\sáàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđ]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    words = text.split()
    # Stop words mở rộng (tiếng Việt phổ biến + từ chung)
    stop_words_extended = {'của', 'và', 'là', 'có', 'một', 'những', 'để', 'cho', 'tôi', 'mình', 'sách', 'cuốn', 'cậu', 'bé', 'này', 'với', 'như', 'bạn', 'các', 'mà', 'đã', 'trong', 'từ', 'khi', 'thì', 'họ', 'ra', 'lại', 'đi', 'cũng', 'về', 'trên', 'dưới', 'gì', 'ai', 'nào', 'không', 'còn', 'được', 'làm', 'bị', 'cách', 'thế', 'nào', 'tiki', 'nhà', 'xuất', 'bản', 'giao', 'hàng', 'đọc', 'sẽ', 'mà', 'cho', 'mình', 'cảm', 'thấy', 'rất', 'thì', 'đây', 'là', 'có', 'không', 'và', 'của', 'trong', 'như', 'được', 'bạn', 'các', 'tôi', 'một', 'những', 'để', 'cho', 'tôi', 'mình', 'sách', 'cuốn', 'cậu', 'bé', 'này', 'với', 'như', 'bạn', 'các', 'mà', 'đã', 'trong', 'từ', 'khi', 'thì', 'họ', 'ra', 'lại', 'đi', 'cũng', 'về', 'trên', 'dưới', 'gì', 'ai', 'nào', 'không', 'còn', 'được', 'làm', 'bị', 'cách', 'thế', 'nào', 'nhận', 'xét', 'nội', 'dung', 'bản', 'thân', 'mới', 'nửa', 'đầu', 'sau', 'cười', 'giận', 'nghịch', 'ngợm', 'ngưỡng', 'mộ', 'tài', 'năng', 'yêu', 'quý', 'tính', 'cách', 'dễ', 'thương', 'đến', 'khoảng', 'phần', 'khóc', 'sướt', 'mướt', 'luôn', 'cuộc', 'đời', 'đối', 'xử', 'bất', 'công', 'vẫn', 'còn', 'quá', 'nhỏ', 'hiểu', 'thế', 'sự', 'chết', 'dẫu', 'biết', 'cuộc', 'sống', 'khó', 'khăn', 'trải', 'qua', 'thuở', 'trở', 'thành', 'hành', 'trang', 'đường', 'mọi', 'thứ', 'đều', 'mặt', 'tích', 'cực', 'thương', 'tiếc', 'tuổi', 'thơ', 'đầy', 'tươi', 'đẹp', 'hồn', 'nhiên', 'giết', 'chết', 'sớm', 'nói', 'chung', 'cực', 'khuyên', 'nên', 'mua', 'chứa', 'chất', 'câu', 'chuyện', 'khác', 'tầng', 'ý', 'nghĩa', 'nữa', 'lúc', 'nhận', 'hình', 'thức', 'ổn', 'cong', 'vênh', 'xước', 'gãy', 'đơn', 'hàng', 'hài', 'lòng', 'phần', 'nội', 'dung', 'liên', 'tục', 'tiếng', 'nửa', 'đầu', 'vui', 'giận', 'đôi', 'khi', 'tức', 'tối', 'dịu', 'ngay', 'bởi', 'những', 'hành', 'động', 'ấm', 'áp', 'dành', 'người', 'thương', 'yêu', 'sau', 'tan', 'vỡ', 'dằn', 'xé', 'tiếc', 'nuối', 'xót', 'xa', 'phẫn', 'nộ', 'đủ', 'cả', 'day', 'dứt', 'khiến', 'người', 'ta', 'hoài', 'niệm', 'tuổi', 'thơ', 'thật', 'sự', 'nuối', 'tiếc', 'dù', 'chuyện', 'vui', 'buồn', 'thứ', 'trôi', 'qua', 'chính', 'dĩ', 'vãng', 'quyển', 'buồn', 'hồi', 'ức', 'trải', 'nghiệm', 'nhưng', 'đáng', 'rất', 'đáng', 'tìm', 'tình', 'yêu', 'thương', 'sự', 'mất', 'mát', 'chắc', 'chắn', 'gợi', 'ý', 'mọi', 'người', 'dù', 'biết', 'rằng', 'hot', 'rồi', 'cùng', 'cười', 'trước', 'trò', 'tinh', 'quái', 'trí', 'tưởng', 'tượng', 'tuyệt', 'vời', 'ước', 'mơ', 'trẻ', 'con', 'zé', 'xót', 'xa', 'em', 'bị', 'đánh', 'đập', 'đau', 'đớn', 'người', 'bạn', 'em', 'yêu', 'nhất', 'lần', 'lượt', 'ra', 'đi', 'tiếc', 'nuối', 'nhận', 'ra', 'rằng', 'đứa', 'trẻ', 'chưa', 'đầy', 'tuổi', 'như', 'em', 'biết', 'quá', 'nhiều', 'mức', 'sự', 'hồn', 'nhiên', 'mơ', 'mộng', 'trẻ', 'con', 'em', 'sẽ', 'không', 'bao', 'giờ', 'quay', 'trở', 'lại', 'có', 'thể', 'hiểu', 'tại', 'sao', 'cuốn', 'sách', 'này', 'lại', 'hot', 'đến', 'vậy', 'lối', 'viết', 'rất', 'nhẹ', 'nhàng', 'trong', 'sáng', 'dễ', 'hiểu', 'quá', 'đủ', 'tiếp', 'cận', 'độc', 'giả', 'mọi', 'lứa', 'tuổi', 'cảm', 'xúc', 'đem', 'lại', 'thì', 'mạnh', 'mẽ', 'vô', 'cùng', 'cuối', 'cùng', 'cảm', 'ơn', 'tiki', 'nhã', 'nam', 'cùng', 'chiến', 'dịch', 'dọn', 'kho', 'lý', 'do', 'cuối', 'cùng', 'khiến', 'mình', 'hạ', 'quyết', 'tâm', 'rước', 'ẻm', 'về', 'nhà', 'đã', 'đem', 'đến', 'mình', 'cuốn', 'sách', 'tuyệt', 'vời', 'đáng', 'đồng', 'tiền', 'bát', 'gạo'}
    words = [w for w in words if len(w) > 2 and w not in stop_words_extended]
    return words

# === GÁN NHÃN KỸ LƯỜNG (KHÔNG BỎ XÓT/SAI LỆCH) ===
def assign_labels_detailed(row, df_comments):
    score_dict = {g: 0.0 for g in groups}
    
    # Metadata text (title + authors + category, weight 0.4)
    text_metadata = (str(row.get('title', '')) + ' ' + str(row.get('authors', '')) + ' ' + str(row.get('category', ''))).lower()
    words_meta = clean_text(text_metadata)
    
    for group, kws in groups_keywords.items():
        # Exact match
        exact_matches = sum(1 for word in words_meta if any(kw == word for kw in kws))
        # Partial match (substring để bắt biến thể, e.g., "khởi nghiệp" chứa "nghiệp")
        partial_matches = sum(1 for word in words_meta if any(kw in word or word in kw for kw in kws))
        score_dict[group] += (exact_matches + partial_matches * 0.5) / (len(kws) * 2) * 0.4
    
    # Comments text (weight 0.6)
    comments = df_comments[df_comments['product_id'] == row['product_id']]['content'].dropna()
    if not comments.empty:
        all_comments_text = ' '.join(comments)
        words_comments = clean_text(all_comments_text)
        for group, kws in groups_keywords.items():
            exact_matches = sum(1 for word in words_comments if any(kw == word for kw in kws))
            partial_matches = sum(1 for word in words_comments if any(kw in word or word in kw for kw in kws))
            score_dict[group] += (exact_matches + partial_matches * 0.5) / (len(kws) * 2) * 0.6
    
    # Normalize (softmax-like)
    total = sum(score_dict.values())
    if total > 0:
        for g in score_dict:
            score_dict[g] = score_dict[g] / total
    
    # Primary group: Top, tie/low → Đa động lực (threshold 0.3 tránh sai lệch)
    top_group = max(score_dict, key=score_dict.get)
    if max(score_dict.values()) < 0.3:
        top_group = 'Đa động lực'
    
    return pd.Series({
        'group_scores': str(score_dict),  # String cho CSV
        'primary_group': top_group,
        'group_score': score_dict[top_group]
    })

# Áp dụng và lưu CSV
df_books_labeled = df_books.apply(lambda row: assign_labels_detailed(row, df_comments), axis=1)
df_books_labeled = pd.concat([df_books.reset_index(drop=True), df_books_labeled], axis=1)
df_books_labeled.to_csv('labeled_books.csv', index=False, encoding='utf-8')

# Verify (in ra để kiểm tra)
print("Kết quả gán nhãn mẫu:")
print(df_books_labeled[['product_id', 'title', 'category', 'primary_group', 'group_score', 'group_scores']])
print("\nPhân bố primary_group (để kiểm tra không sai lệch):")
print(df_books_labeled['primary_group'].value_counts())