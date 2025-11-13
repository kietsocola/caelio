"""
Script to import book links from nha_sach_xua_100_with_id.csv into book_links table
Usage: python import_nha_sach_xua_book_links.py <bookstore_id>
"""

import asyncpg
import pandas as pd
import asyncio
import sys
import os
from datetime import datetime

# Database configuration
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'caelio_care',
    'user': 'postgres',
    'password': '123'  # Update this
}

CSV_FILE = 'crawl_data/nha_sach_xua/nha_sach_xua_100_with_id.csv'


async def import_book_links(bookstore_id: int):
    """Import book links from CSV to database"""
    
    # Check if CSV file exists
    if not os.path.exists(CSV_FILE):
        print(f"❌ Error: File not found: {CSV_FILE}")
        return
    
    print(f"📚 Đọc file CSV: {CSV_FILE}")
    df = pd.read_csv(CSV_FILE, encoding='utf-8')
    print(f"✅ Đọc được {len(df)} sách từ file")
    
    # Connect to database
    print(f"\n🔗 Kết nối database...")
    try:
        conn = await asyncpg.connect(**DATABASE_CONFIG)
        print("✅ Kết nối database thành công")
    except Exception as e:
        print(f"❌ Lỗi kết nối database: {e}")
        return
    
    try:
        # Verify bookstore exists
        bookstore = await conn.fetchrow(
            'SELECT id, name FROM bookstores WHERE id = $1',
            bookstore_id
        )
        
        if not bookstore:
            print(f"❌ Không tìm thấy bookstore với ID: {bookstore_id}")
            return
        
        print(f"\n📖 Nhà sách: {bookstore['name']} (ID: {bookstore_id})")
        
        # Statistics
        inserted = 0
        updated = 0
        skipped = 0
        errors = 0
        
        print(f"\n🚀 Bắt đầu import {len(df)} book links...")
        print("=" * 80)
        
        for idx, row in df.iterrows():
            stt = row['STT']
            book_id = row['ID']
            book_title = row['TÊN SÁCH']
            price = row['GIÁ']
            
            # Skip if no ID
            if pd.isna(book_id):
                print(f"⚠️  [{stt:3d}] Bỏ qua: {book_title[:50]:50s} - Không có ID")
                skipped += 1
                continue
            
            # Convert price to float
            try:
                if isinstance(price, str):
                    # Remove any non-numeric characters except decimal point
                    price = float(price.replace(',', '').replace(')', ''))
                else:
                    price = float(price)
            except (ValueError, TypeError):
                print(f"⚠️  [{stt:3d}] Bỏ qua: {book_title[:50]:50s} - Giá không hợp lệ: {price}")
                skipped += 1
                continue
            
            try:
                # Check if book exists in books table
                book_exists = await conn.fetchval(
                    'SELECT EXISTS(SELECT 1 FROM books WHERE product_id = $1)',
                    int(book_id)
                )
                
                if not book_exists:
                    print(f"⚠️  [{stt:3d}] Bỏ qua: {book_title[:50]:50s} - Sách chưa có trong database")
                    skipped += 1
                    continue
                
                # Check if book_link already exists
                existing_link = await conn.fetchrow('''
                    SELECT id FROM book_links
                    WHERE book_id = $1 AND bookstore_id = $2
                ''', int(book_id), bookstore_id)
                
                if existing_link:
                    # Update existing link
                    await conn.execute('''
                        UPDATE book_links
                        SET purchase_url = $1,
                            price = $2,
                            stock_quantity = $3,
                            stock_status = $4,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE book_id = $5 AND bookstore_id = $6
                    ''',
                        '#',  # purchase_url
                        price,
                        1,  # stock_quantity
                        'available',  # stock_status
                        int(book_id),
                        bookstore_id
                    )
                    print(f"🔄 [{stt:3d}] Cập nhật: {book_title[:50]:50s} - {price:>10,.0f}đ")
                    updated += 1
                else:
                    # Insert new link
                    await conn.execute('''
                        INSERT INTO book_links (
                            book_id, bookstore_id, purchase_url, price, 
                            stock_quantity, stock_status
                        )
                        VALUES ($1, $2, $3, $4, $5, $6)
                    ''',
                        int(book_id),
                        bookstore_id,
                        '#',  # purchase_url
                        price,
                        1,  # stock_quantity
                        'available'  # stock_status
                    )
                    print(f"✅ [{stt:3d}] Thêm mới: {book_title[:50]:50s} - {price:>10,.0f}đ")
                    inserted += 1
                
            except Exception as e:
                print(f"❌ [{stt:3d}] Lỗi: {book_title[:50]:50s} - {str(e)}")
                errors += 1
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 KẾT QUẢ IMPORT:")
        print("=" * 80)
        print(f"✅ Thêm mới:     {inserted:>3d} book links")
        print(f"🔄 Cập nhật:     {updated:>3d} book links")
        print(f"⚠️  Bỏ qua:      {skipped:>3d} sách")
        print(f"❌ Lỗi:         {errors:>3d} sách")
        print(f"📚 Tổng cộng:    {len(df):>3d} sách")
        print("=" * 80)
        
        # Verify total book_links for this bookstore
        total_links = await conn.fetchval(
            'SELECT COUNT(*) FROM book_links WHERE bookstore_id = $1',
            bookstore_id
        )
        print(f"\n📖 Tổng số book links của nhà sách '{bookstore['name']}': {total_links}")
        
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await conn.close()
        print("\n✅ Đã đóng kết nối database")


async def list_bookstores():
    """List all bookstores in database"""
    try:
        conn = await asyncpg.connect(**DATABASE_CONFIG)
        
        bookstores = await conn.fetch(
            'SELECT id, name, address, commission_rate FROM bookstores ORDER BY id'
        )
        
        if not bookstores:
            print("❌ Không có nhà sách nào trong database")
            print("💡 Hãy tạo nhà sách trước bằng API hoặc SQL")
        else:
            print("\n📚 DANH SÁCH NHÀ SÁCH:")
            print("=" * 100)
            print(f"{'ID':<5} {'Tên nhà sách':<40} {'Địa chỉ':<40} {'Hoa hồng':<10}")
            print("=" * 100)
            for bs in bookstores:
                print(f"{bs['id']:<5} {bs['name']:<40} {bs['address']:<40} {bs['commission_rate']:<10.1f}%")
            print("=" * 100)
            print(f"\nTổng: {len(bookstores)} nhà sách")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Lỗi kết nối database: {e}")


def print_usage():
    """Print usage instructions"""
    print("\n" + "=" * 80)
    print("HƯỚNG DẪN SỬ DỤNG:")
    print("=" * 80)
    print("\n1. Import book links cho một nhà sách:")
    print("   python import_nha_sach_xua_book_links.py <bookstore_id>")
    print("   Ví dụ: python import_nha_sach_xua_book_links.py 1")
    print("\n2. Xem danh sách nhà sách:")
    print("   python import_nha_sach_xua_book_links.py --list")
    print("\n3. Hiển thị hướng dẫn:")
    print("   python import_nha_sach_xua_book_links.py --help")
    print("\n" + "=" * 80)
    print(f"\n📁 File CSV: {CSV_FILE}")
    print("📝 Mapping:")
    print("   - book_id        = ID (từ CSV)")
    print("   - price          = GIÁ (từ CSV)")
    print("   - purchase_url   = '#'")
    print("   - stock_quantity = 1")
    print("   - stock_status   = 'available'")
    print("=" * 80 + "\n")


async def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("❌ Thiếu tham số!")
        print_usage()
        return
    
    arg = sys.argv[1]
    
    if arg in ['--help', '-h', 'help']:
        print_usage()
    elif arg in ['--list', '-l', 'list']:
        await list_bookstores()
    else:
        try:
            bookstore_id = int(arg)
            await import_book_links(bookstore_id)
        except ValueError:
            print(f"❌ Bookstore ID không hợp lệ: {arg}")
            print("💡 Bookstore ID phải là số nguyên")
            print_usage()


if __name__ == "__main__":
    # Update database config from environment if available
    if 'DB_PASSWORD' in os.environ:
        DATABASE_CONFIG['password'] = os.environ['DB_PASSWORD']
    
    asyncio.run(main())
