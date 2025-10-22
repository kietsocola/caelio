import pandas as pd

# Danh sách các file cần gộp
files = [
    "summary_api/books_summary_1.csv",
    "summary_api/books_summary_2.csv",
    "summary_api/books_summary_3.csv",
    "summary_api/books_summary_4.csv",
    "summary_api/books_summary_5.csv"
]

# Đọc và gộp tất cả các file
dfs = [pd.read_csv(f) for f in files]
merged_df = pd.concat(dfs, ignore_index=True)

# Lưu ra file mới
merged_df.to_csv("books_summary_all.csv", index=False)
print("✅ Đã gộp xong, file mới: books_summary_all.csv")
