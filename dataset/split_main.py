import pandas as pd

# Đọc file CSV gốc
df = pd.read_csv('dataset/books_full_data.csv')  # đổi 'input.csv' thành tên file của bạn

# Loại bỏ các dòng trùng nhau dựa trên cột 'title', giữ dòng đầu tiên
df_unique = df.drop_duplicates(subset=['title'], keep='first')

# Ghi ra file CSV mới với tất cả cột
df_unique.to_csv("books_unique.csv", index=False)
print("File CSV mới đã được tạo: books_unique.csv")
