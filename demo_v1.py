import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import io
import re
import ast  # Để parse string thành dictionary

# === BƯỚC 1: LOAD DATASET ĐÃ CÓ NHÃN ===
# Load dữ liệu đã được gán nhãn từ file CSV
df_books_labeled = pd.read_csv('result/labeled_books_v3.csv')

# Parse cột group_scores từ string thành dictionary
def parse_group_scores(scores_str):
    try:
        return ast.literal_eval(scores_str)
    except:
        # Fallback nếu parse lỗi
        return {'Chinh phục': 0.2, 'Kiến tạo': 0.2, 'Tri thức': 0.2, 'Tự do': 0.2, 'Kết nối': 0.1, 'Đa động lực': 0.1}

df_books_labeled['group_scores'] = df_books_labeled['group_scores'].apply(parse_group_scores)

# Load comments để bổ sung thông tin nếu cần
df_comments = pd.read_csv('comments.csv')

# === BƯỚC 2: ĐỊNH NGHĨA GROUPS TỪ DỮ LIỆU CÓ SẴN ===
groups = ['Chinh phục', 'Kiến tạo', 'Tri thức', 'Tự do', 'Kết nối', 'Đa động lực']

# Thông tin cơ bản về dataset
print(f"Tổng số sách trong dataset: {len(df_books_labeled)}")
print(f"Unique product_id: {df_books_labeled['product_id'].nunique()}")
print("\nPhân phối nhãn chính:")
print(df_books_labeled['primary_group'].value_counts())

# Kiểm tra và làm sạch dữ liệu
print("\nKiểm tra dữ liệu:")
print("Group scores type:", type(df_books_labeled['group_scores'].iloc[0]))
print("Sample group scores:", df_books_labeled['group_scores'].iloc[0])

# === BƯỚC 5: BỘ CÂU HỎI VÀ TÍNH USER PROFILE ===
def ask_questions():
    print("\n=== BỘ CÂU HỎI GỢI Ý SÁCH ===")
    answers = {}
    
    # Lớp 1: Xác định group chính
    print("1. Mục tiêu quan trọng nhất khi tìm sách?")
    print("A: Truyền cảm hứng/giải quyết vấn đề (Chinh phục)")
    print("B: Khám phá bản thân (Kiến tạo)")
    print("C: Thấu hiểu lĩnh vực (Tri thức)")
    print("D: Thư giãn/thoát ly (Tự do)")
    print("E: Kết nối/đồng cảm (Kết nối)")
    ans1 = input("Chọn (A/B/C/D/E): ").upper()
    group1 = {'A': 'Chinh phục', 'B': 'Kiến tạo', 'C': 'Tri thức', 'D': 'Tự do', 'E': 'Kết nối'}.get(ans1, 'Kết nối')
    
    print("2. Thu hút bởi câu chuyện về?")
    print("A: Hành trình vượt thử thách (CP)")
    print("B: Cá nhân khác biệt (KT)")
    print("C: Phát kiến vĩ đại (TT)")
    print("D: Câu chuyện cuốn hút (TD)")
    print("E: Mối quan hệ sâu sắc (KN)")
    ans2 = input("Chọn (A/B/C/D/E): ").upper()
    group2 = {'A': 'Chinh phục', 'B': 'Kiến tạo', 'C': 'Tri thức', 'D': 'Tự do', 'E': 'Kết nối'}.get(ans2, 'Kết nối')
    
    answers['primary_group'] = group1 if group1 == group2 else 'Đa động lực'
    
    # Lớp 2: Adjusts
    print("3. Nghiêng về? A: Quen thuộc (Openness thấp), B: Mới lạ (Openness cao)")
    openness = input("Chọn (A/B): ").upper() == 'B'  # True = cao
    
    print("4. Là người? A: Đọc sâu, B: Đọc rộng")
    read_style = 'sâu' if input("Chọn (A/B): ").upper() == 'A' else 'rộng'
    
    print("5. Sau đọc xong? A: Giữ riêng (hướng nội), B: Chia sẻ (hướng ngoại)")
    extro = input("Chọn (A/B): ").upper() == 'B'
    
    print("6. Thích câu chuyện? A: Ấm áp có hậu (dễ chịu), B: Gai góc (thách thức)")
    challenge = input("Chọn (A/B): ").upper() == 'B'
    
    print("7. Khi căng thẳng? A: Đối mặt vấn đề, B: Trốn thoát")
    escape = input("Chọn (A/B): ").upper() == 'B'
    
    print("8. Với nhân vật khó khăn? A: Dễ xúc động (đồng cảm cao), B: Tập trung xử lý (đồng cảm thấp)")
    empathy = input("Chọn (A/B): ").upper() == 'A'
    
    # Tính user_scores: Base từ primary_group, adjust theo lớp 2
    user_scores = {g: 0.0 for g in groups}
    base_group = answers['primary_group']
    user_scores[base_group] = 1.0
    
    # Adjusts (từ doc, ví dụ đơn giản: +0.2 nếu match)
    if openness:  # Openness cao: Boost Tri thức, Kiến tạo, etc.
        user_scores['Tri thức'] += 0.2
        user_scores['Kiến tạo'] += 0.2
        user_scores['Kết nối'] += 0.1
    if read_style == 'sâu':
        user_scores['Chinh phục'] += 0.1
        user_scores['Tri thức'] += 0.2
    if extro:
        user_scores['Chinh phục'] += 0.1
        user_scores['Kết nối'] += 0.2
    if challenge:
        user_scores['Tự do'] += 0.2
        user_scores['Tri thức'] += 0.1
    if escape:
        user_scores['Tự do'] += 0.2
        user_scores['Kết nối'] += 0.1
    if empathy:
        user_scores['Kết nối'] += 0.3
        user_scores['Kiến tạo'] += 0.1
    
    # Normalize
    total = sum(user_scores.values())
    if total > 0:
        for g in user_scores:
            user_scores[g] /= total
    
    answers['user_scores'] = user_scores
    return answers

# === BƯỚC 6: MATCH VÀ GỢI Ý ===
def recommend_books(answers, df_labeled, top_n=5):
    print(f"Debug: Số sách để recommend: {len(df_labeled)}")
    print(f"Debug: User scores: {answers['user_scores']}")
    
    # Vector user và sách
    user_vec = np.array([answers['user_scores'][g] for g in groups])
    print(f"Debug: User vector shape: {user_vec.shape}")
    
    # Tạo book vectors từ group_scores dictionary
    book_vecs = []
    for idx, row in df_labeled.iterrows():
        if isinstance(row['group_scores'], dict):
            book_vec = [row['group_scores'].get(g, 0.0) for g in groups]
        else:
            print(f"Warning: group_scores không phải dict tại index {idx}: {type(row['group_scores'])}")
            book_vec = [0.0] * len(groups)  # Default vector
        book_vecs.append(book_vec)
    
    book_vecs = np.array(book_vecs)
    print(f"Debug: Book vectors shape: {book_vecs.shape}")
    
    if len(book_vecs) == 0:
        print("Không có sách nào để recommend!")
        return pd.DataFrame()
    
    # Cosine similarity
    sims = cosine_similarity([user_vec], book_vecs)[0]
    
    # Score hybrid: sim * avg_rating (đảm bảo avg_rating là số)
    avg_ratings = pd.to_numeric(df_labeled['avg_rating'], errors='coerce').fillna(3.0)
    scores = sims * avg_ratings.values / 5.0
    
    # Top N
    top_idx = np.argsort(scores)[::-1][:top_n]
    recs = df_labeled.iloc[top_idx].copy()
    recs['match_score'] = scores[top_idx]
    recs['reason'] = recs.apply(lambda r: f"Match {r['primary_group']} ({r['match_score']:.2f}), phù hợp {answers['primary_group']}", axis=1)
    
    return recs[['title', 'authors', 'category', 'avg_rating', 'match_score', 'reason']]

# === CHẠY HỆ THỐNG ===
if __name__ == "__main__":
    # Debug info
    print("=== DEBUG INFO ===")
    print(f"Tổng số sách đã có nhãn: {len(df_books_labeled)}")
    
    # Kiểm tra một vài sách đã được label
    print("\nSample labeled books:")
    for i in range(min(3, len(df_books_labeled))):
        row = df_books_labeled.iloc[i]
        print(f"- {row['title']}: {row['primary_group']} (score: {row['group_score']:.3f})")
    
    print("\n" + "="*50)
    answers = ask_questions()
    recommendations = recommend_books(answers, df_books_labeled)
    print("\n=== GỢI Ý TOP 5 SÁCH ===")
    if not recommendations.empty:
        print(recommendations.to_string(index=False))
    else:
        print("Không tìm thấy sách phù hợp!")