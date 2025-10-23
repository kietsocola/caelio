import pandas as pd

# Đọc file CSV gốc
df = pd.read_csv('books_unique.csv')  # đổi 'input.csv' thành tên file của bạn

# Chọn các cột cần thiết
# Nếu cột 'n_view' chưa có, tạo mới với giá trị mặc định 0
if 'n_view' not in df.columns:
    df['n_view'] = 0

selected_columns = ['product_id', 'title', 'authors', 'category', 'n_view', 'cover_link']
new_df = df[selected_columns]

# Ghi ra file CSV mới
new_df.to_csv('output.csv', index=False)
print("File CSV mới đã được tạo: output.csv")
