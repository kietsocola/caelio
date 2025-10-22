import pandas as pd

# Đọc 3 file
books = pd.read_csv("dataset/book_data.csv")
summaries = pd.read_csv("dataset/books_summary_all.csv")
comments = pd.read_csv("dataset/comments.csv")

comments_grouped = (
    comments.groupby("product_id")["content"]
    .apply(lambda x: " ||| ".join(x.dropna().astype(str)))
    .reset_index()
)

merged = pd.merge(books, summaries, on="product_id", how="left")
final_df = pd.merge(merged, comments_grouped, on="product_id", how="left")

# Lưu ra file mới
final_df.to_csv("books_full_data.csv", index=False)
print("✅ Đã gộp xong thành books_full_data.csv")
