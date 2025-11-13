"""
Script to add ID column to nha_sach_xua_100.csv from data_crawl_nha_sach_xua.csv
Since crawl script preserves order, we can match by row position directly.
"""

import pandas as pd

def main():
    print("📚 Bắt đầu thêm cột ID vào nha_sach_xua_100.csv...")
    
    # Read the files
    original_file = 'nha_sach_xua/nha_sach_xua_100.csv'
    crawled_file = '../dataset/data_crawl_nha_sach_xua.csv'
    output_file = 'nha_sach_xua/nha_sach_xua_100_with_id.csv'
    
    print(f"\n📖 Đọc file gốc: {original_file}")
    df_original = pd.read_csv(original_file, encoding='utf-8')
    
    print(f"📖 Đọc file crawled: {crawled_file}")
    df_crawled = pd.read_csv(crawled_file, encoding='utf-8')
    
    print(f"\n✅ File gốc có {len(df_original)} sách")
    print(f"✅ File crawled có {len(df_crawled)} sách")
    
    # Verify same length
    if len(df_original) != len(df_crawled):
        print(f"\n⚠️ CẢNH BÁO: Số lượng sách khác nhau!")
        print(f"   File gốc: {len(df_original)} sách")
        print(f"   File crawled: {len(df_crawled)} sách")
        print(f"   Sẽ chỉ thêm ID cho {min(len(df_original), len(df_crawled))} sách đầu tiên.")
    
    # Add ID column by matching row position
    df_original['ID'] = None
    
    print("\n🔗 Thêm ID theo thứ tự...")
    matched_count = 0
    
    for idx in range(min(len(df_original), len(df_crawled))):
        product_id = df_crawled.loc[idx, 'product_id']
        stt = df_original.loc[idx, 'STT']
        title_original = df_original.loc[idx, 'TÊN SÁCH']
        title_crawled = df_crawled.loc[idx, 'title']
        
        df_original.at[idx, 'ID'] = product_id
        matched_count += 1
        
        # Show matching info
        print(f"✅ [{stt:3d}] {title_original[:50]:50s} -> ID: {product_id}")
        
        # Warn if titles seem very different (optional check)
        if title_original.lower()[:10] not in title_crawled.lower() and \
           title_crawled.lower()[:10] not in title_original.lower():
            print(f"   ⚠️  Lưu ý: Tên sách có thể khác: '{title_crawled[:40]}...'")
    
    # Reorder columns: ID first, then the rest
    cols = ['ID'] + [col for col in df_original.columns if col != 'ID']
    df_original = df_original[cols]
    
    # Save to new file
    print(f"\n💾 Lưu file mới: {output_file}")
    df_original.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    # Print summary
    print("\n" + "="*70)
    print("📊 KẾT QUẢ:")
    print("="*70)
    print(f"✅ Đã thêm ID cho: {matched_count}/{len(df_original)} sách")
    
    if matched_count < len(df_original):
        print(f"⚠️  Còn {len(df_original) - matched_count} sách chưa có ID")
    
    print(f"\n✅ Hoàn thành! File đã lưu tại: {output_file}")
    print("\n💡 Lưu ý: Script này match theo thứ tự dòng vì crawl script đã giữ đúng thứ tự gốc.")

if __name__ == "__main__":
    main()
