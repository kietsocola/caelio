"""
Script to merge data_crawl_nha_sach_xua.csv into books_full_data.csv
Checks for duplicate product_id and only adds new books
"""

import pandas as pd
import os

def main():
    print("📚 Bắt đầu gộp data crawled vào books_full_data.csv...")
    
    # File paths
    crawled_file = 'nha_sach_xua/data_crawl_nha_sach_xua.csv'
    full_data_file = '../dataset/books_full_data.csv'
    output_file = '../dataset/books_full_data_merged.csv'
    backup_file = '../dataset/books_full_data_backup.csv'
    
    # Read files
    print(f"\n📖 Đọc file crawled: {crawled_file}")
    df_crawled = pd.read_csv(crawled_file, encoding='utf-8')
    
    print(f"📖 Đọc file full data: {full_data_file}")
    df_full = pd.read_csv(full_data_file, encoding='utf-8')
    
    print(f"\n✅ File crawled có {len(df_crawled)} sách")
    print(f"✅ File full data có {len(df_full)} sách")
    
    # Backup original file
    print(f"\n💾 Backup file gốc: {backup_file}")
    df_full.to_csv(backup_file, index=False, encoding='utf-8-sig')
    
    # Check for duplicates
    print("\n🔍 Kiểm tra trùng lặp product_id...")
    
    existing_ids = set(df_full['product_id'].astype(str))
    new_books = []
    duplicate_books = []
    
    for idx, row in df_crawled.iterrows():
        product_id = str(row['product_id'])
        title = row['title']
        
        if product_id in existing_ids:
            duplicate_books.append((product_id, title))
            print(f"⚠️  Trùng ID: {product_id} - {title[:50]}")
        else:
            new_books.append(row)
            existing_ids.add(product_id)
            print(f"✅ Thêm mới: {product_id} - {title[:50]}")
    
    # Convert new books to DataFrame
    if new_books:
        df_new = pd.DataFrame(new_books)
        
        # Ensure column order matches books_full_data.csv
        column_order = [
            'product_id', 'title', 'authors', 'original_price', 'current_price', 
            'quantity', 'category', 'n_review', 'avg_rating', 'pages', 
            'manufacturer', 'cover_link', 'summary', 'content'
        ]
        
        # Reorder columns if needed
        if list(df_new.columns) != column_order:
            df_new = df_new[column_order]
        
        # Merge data
        print(f"\n🔗 Gộp {len(new_books)} sách mới vào database...")
        df_merged = pd.concat([df_full, df_new], ignore_index=True)
        
        # Save merged file
        print(f"💾 Lưu file merged: {output_file}")
        df_merged.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        # Also update the original file
        print(f"💾 Cập nhật file gốc: {full_data_file}")
        df_merged.to_csv(full_data_file, index=False, encoding='utf-8-sig')
    else:
        print("\n⚠️  Không có sách mới để thêm!")
        df_merged = df_full
    
    # Print summary
    print("\n" + "="*80)
    print("📊 KẾT QUẢ:")
    print("="*80)
    print(f"📚 Tổng số sách trong file crawled: {len(df_crawled)}")
    print(f"📚 Số sách trong database ban đầu: {len(df_full)}")
    print(f"✅ Số sách mới được thêm: {len(new_books)}")
    print(f"⚠️  Số sách bị trùng ID (bỏ qua): {len(duplicate_books)}")
    print(f"📚 Tổng số sách sau khi merge: {len(df_merged)}")
    
    if duplicate_books:
        print("\n📋 Danh sách sách bị trùng ID:")
        for product_id, title in duplicate_books[:10]:  # Show first 10
            print(f"   - ID {product_id}: {title[:60]}")
        if len(duplicate_books) > 10:
            print(f"   ... và {len(duplicate_books) - 10} sách khác")
    
    print(f"\n✅ Hoàn thành!")
    print(f"   - File merged: {output_file}")
    print(f"   - File gốc đã cập nhật: {full_data_file}")
    print(f"   - File backup: {backup_file}")
    
    # Verify data integrity
    print("\n🔍 Kiểm tra tính toàn vẹn dữ liệu...")
    
    # Check for any duplicate IDs in final file
    duplicate_ids = df_merged[df_merged.duplicated(subset=['product_id'], keep=False)]
    if len(duplicate_ids) > 0:
        print(f"❌ CẢNH BÁO: Phát hiện {len(duplicate_ids)} sách có ID trùng trong file cuối!")
        print(duplicate_ids[['product_id', 'title']].head())
    else:
        print("✅ Không có ID trùng lặp trong file cuối")
    
    # Check for missing required fields
    required_fields = ['product_id', 'title', 'authors']
    for field in required_fields:
        missing = df_merged[field].isna().sum()
        if missing > 0:
            print(f"⚠️  Có {missing} sách thiếu field '{field}'")
        else:
            print(f"✅ Tất cả sách đều có field '{field}'")
    
    print("\n🎉 Merge hoàn tất!")

if __name__ == "__main__":
    main()
