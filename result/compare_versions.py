import pandas as pd
import ast

# Load 2 files
df1 = pd.read_csv('labeled_books.csv')
df2 = pd.read_csv('labeled_books_v3.csv')

# Lọc sách đầu tiên để so sánh
book1 = df1[df1['product_id'] == 74021317].iloc[0]
book2 = df2[df2['product_id'] == 74021317].iloc[0]

print('=== SÁCH: Cây Cam Ngọt Của Tôi ===')
print('VERSION 1 (không summary):')
scores1 = ast.literal_eval(book1['group_scores'])
for k, v in scores1.items():
    print(f'  {k}: {v:.4f}')
print(f'Primary: {book1["primary_group"]} ({book1["group_score"]:.4f})')

print('\nVERSION 2 (có summary):')
scores2 = ast.literal_eval(book2['group_scores'])  
for k, v in scores2.items():
    print(f'  {k}: {v:.4f}')
print(f'Primary: {book2["primary_group"]} ({book2["group_score"]:.4f})')

print('\n=== SO SÁNH KHÁC BIỆT ===')
for k in scores1.keys():
    diff = scores2[k] - scores1[k]
    print(f'{k}: {diff:+.4f} ({scores1[k]:.4f} -> {scores2[k]:.4f})')

# So sánh tổng quan
print(f'\n=== TỔNG QUAN KHÁC BIỆT ===')
print(f'Version 1 có {len(df1)} dòng, Version 2 có {len(df2)} dòng')
print(f'Version 1 có cột summary: {"summary" in df1.columns}')  
print(f'Version 2 có cột summary: {"summary" in df2.columns}')

# Kiểm tra xem có sách nào thay đổi primary group không
merged = pd.merge(df1[['product_id', 'primary_group']], df2[['product_id', 'primary_group']], on='product_id', suffixes=('_v1', '_v2'))
changed = merged[merged['primary_group_v1'] != merged['primary_group_v2']]
print(f'\nSố sách thay đổi primary group: {len(changed)}')
if len(changed) > 0:
    print('Các sách thay đổi:')
    for _, row in changed.head(5).iterrows():
        print(f'  Product {row["product_id"]}: {row["primary_group_v1"]} -> {row["primary_group_v2"]}')