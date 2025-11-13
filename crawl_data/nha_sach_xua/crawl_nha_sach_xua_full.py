import requests
import pandas as pd
import time
from bs4 import BeautifulSoup
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import threading
import random

# === ⚙️ Cấu hình ===
INPUT_FILE = "nha_sach_xua_100.csv"
OUTPUT_FILE = "data_crawl_nha_sach_xua.csv"
PARTIAL_FILE = "data_crawl_nha_sach_xua_partial.csv"
SAVE_EVERY = 10        # auto-save mỗi 10 sách
MAX_WORKERS = 6        # Số threads chạy song song
DELAY_BETWEEN_REQUESTS = 0.8  # Giây delay giữa các request

# === 1. Đọc file CSV gốc ===
print("📖 Đang đọc file nha_sach_xua_100.csv...")
df = pd.read_csv(INPUT_FILE, encoding='utf-8')
print(f"✅ Đã đọc {len(df)} sách từ file")

# === 2. Hàm tìm kiếm sách trên Tiki ===
def search_book_on_tiki(title, author):
    """Tìm kiếm sách trên Tiki và trả về thông tin chi tiết"""
    try:
        # Tìm kiếm sách
        search_query = f"{title} {author}".strip()
        search_url = f"https://tiki.vn/api/v2/products?q={search_query}&limit=5"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json"
        }
        
        search_res = requests.get(search_url, headers=headers, timeout=15)
        search_data = search_res.json()
        
        products = search_data.get("data", [])
        if not products:
            return None
        
        # Lấy sản phẩm đầu tiên (có thể cải thiện bằng matching score)
        product = products[0]
        product_id = product.get("id")
        
        if not product_id:
            return None
        
        # Lấy thông tin chi tiết sản phẩm
        detail_url = f"https://tiki.vn/api/v2/products/{product_id}"
        detail_res = requests.get(detail_url, headers=headers, timeout=15)
        detail_data = detail_res.json()
        
        # Lấy reviews/comments
        review_url = f"https://tiki.vn/api/v2/reviews?product_id={product_id}&limit=5&sort=score%7Cdesc,id%7Cdesc,stars%7Call"
        review_res = requests.get(review_url, headers=headers, timeout=15)
        review_data = review_res.json()
        
        # Parse summary từ description
        summary = ""
        desc_html = detail_data.get("description", "")
        if desc_html:
            soup = BeautifulSoup(desc_html, "html.parser")
            summary = soup.get_text(separator=" ").strip()
            # Giới hạn độ dài summary
            if len(summary) > 500:
                summary = summary[:500] + "..."
        
        # Parse top 5 comments
        comments = []
        reviews_list = review_data.get("data", [])
        for review in reviews_list[:5]:
            comment_text = review.get("content", "").strip()
            if comment_text:
                comments.append(comment_text)
        
        content = " ||| ".join(comments) if comments else ""
        
        # Lấy thông tin sách
        book_info = {
            "product_id": product_id,
            "title": detail_data.get("name", ""),
            "authors": ", ".join([author.get("name", "") for author in detail_data.get("authors", [])]),
            "original_price": detail_data.get("original_price", 0),
            "current_price": detail_data.get("price", 0),
            "quantity": detail_data.get("quantity_sold", {}).get("value", 0),
            "category": detail_data.get("categories", {}).get("name", "") if detail_data.get("categories") else "",
            "n_review": detail_data.get("review_count", 0),
            "avg_rating": detail_data.get("rating_average", 0),
            "pages": 0,  # Tiki không cung cấp thông tin số trang
            "manufacturer": detail_data.get("brand", {}).get("name", "") if detail_data.get("brand") else "",
            "cover_link": detail_data.get("thumbnail_url", ""),
            "summary": summary,
            "content": content
        }
        
        # Tìm số trang trong specifications nếu có
        specs = detail_data.get("specifications", [])
        for spec in specs:
            attributes = spec.get("attributes", [])
            for attr in attributes:
                if attr.get("code") == "number_of_page":
                    try:
                        book_info["pages"] = int(attr.get("value", 0))
                    except:
                        pass
        
        return book_info
        
    except Exception as e:
        print(f"❌ Lỗi tìm kiếm Tiki: {e}")
        return None

# === 3. Hàm fallback: tìm trên Google Books ===
def search_book_on_google(title, author):
    """Fallback: Tìm kiếm trên Google Books"""
    try:
        query = f"intitle:{title}+inauthor:{author}"
        url = f"https://www.googleapis.com/books/v1/volumes?q={query}&langRestrict=vi"
        res = requests.get(url, timeout=10).json()
        
        items = res.get("items", [])
        if not items:
            return None
        
        volume_info = items[0].get("volumeInfo", {})
        
        # Tạo product_id giả từ Google Books ID
        google_id = items[0].get("id", "")
        product_id = hash(google_id) % (10 ** 10)  # Convert to 10 digit number
        
        book_info = {
            "product_id": product_id,
            "title": volume_info.get("title", ""),
            "authors": ", ".join(volume_info.get("authors", [])),
            "original_price": 0,
            "current_price": 0,
            "quantity": 0,
            "category": ", ".join(volume_info.get("categories", [])),
            "n_review": 0,
            "avg_rating": volume_info.get("averageRating", 0),
            "pages": volume_info.get("pageCount", 0),
            "manufacturer": volume_info.get("publisher", ""),
            "cover_link": volume_info.get("imageLinks", {}).get("thumbnail", ""),
            "summary": volume_info.get("description", "").replace("\n", " ").strip(),
            "content": ""
        }
        
        return book_info
        
    except Exception as e:
        print(f"❌ Lỗi Google Books: {e}")
        return None

# === 4. Hàm xử lý một sách ===
def process_single_book(row_data):
    """Xử lý một sách và trả về kết quả đầy đủ"""
    i, row = row_data
    stt = row.get("STT", i + 1)
    title = row["TÊN SÁCH"]
    author = row["TÁC GIẢ"]
    
    thread_id = threading.current_thread().ident
    print(f"\n📚 [Thread-{thread_id}] ({i+1}/{len(df)}) Đang crawl: {title[:50]}...")
    
    # Thử tìm trên Tiki trước
    book_info = search_book_on_tiki(title, author)
    
    if book_info:
        print(f"✅ [Thread-{thread_id}] Tiki: {title[:30]}... (ID: {book_info['product_id']})")
    else:
        # Fallback sang Google Books
        print(f"⚙️ [Thread-{thread_id}] Thử Google Books: {title[:30]}...")
        book_info = search_book_on_google(title, author)
        
        if book_info:
            print(f"✅ [Thread-{thread_id}] Google Books: {title[:30]}...")
        else:
            print(f"❌ [Thread-{thread_id}] Không tìm thấy: {title[:30]}...")
            # Tạo entry rỗng nếu không tìm thấy
            book_info = {
                "product_id": hash(title) % (10 ** 10),
                "title": title,
                "authors": author,
                "original_price": 0,
                "current_price": 0,
                "quantity": 0,
                "category": row.get("THỂ LOẠI", ""),
                "n_review": 0,
                "avg_rating": 0,
                "pages": 0,
                "manufacturer": "",
                "cover_link": "",
                "summary": "",
                "content": ""
            }
    
    # Thêm index để sắp xếp sau
    book_info["index"] = i
    
    # Delay để tránh spam API
    time.sleep(DELAY_BETWEEN_REQUESTS + random.uniform(0, 0.5))
    
    return book_info

# === 5. Multithreading processing ===
books_data = []
completed_count = 0
lock = Lock()

# Chuẩn bị dữ liệu cho ThreadPool
book_data_list = [(i, row) for i, row in df.iterrows()]

print(f"\n🚀 Bắt đầu crawl {len(book_data_list)} sách với {MAX_WORKERS} threads...")
print("=" * 80)

with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    # Submit tất cả tasks
    future_to_book = {executor.submit(process_single_book, book): book for book in book_data_list}
    
    # Xử lý kết quả khi hoàn thành
    for future in as_completed(future_to_book):
        try:
            result = future.result()
            
            with lock:  # Thread-safe
                books_data.append(result)
                completed_count += 1
                
                print(f"\n📊 Tiến độ: {completed_count}/{len(df)} sách ({completed_count*100//len(df)}%)")
                
                # Auto-save mỗi SAVE_EVERY sách
                if completed_count % SAVE_EVERY == 0:
                    # Sắp xếp theo index gốc trước khi lưu
                    sorted_books = sorted(books_data, key=lambda x: x['index'])
                    temp_df = pd.DataFrame([{k: v for k, v in item.items() if k != 'index'} 
                                          for item in sorted_books])
                    temp_df.to_csv(PARTIAL_FILE, index=False, encoding='utf-8-sig')
                    print(f"💾 Auto-save: {PARTIAL_FILE} ({completed_count} sách)")
                    
        except Exception as e:
            print(f"❌ Lỗi xử lý: {e}")

print(f"\n✅ Hoàn tất crawl {completed_count} sách!")
print("=" * 80)

# === 6. Ghi ra file cuối (sắp xếp theo thứ tự gốc) ===
sorted_books = sorted(books_data, key=lambda x: x['index'])
final_books = [{k: v for k, v in item.items() if k != 'index'} for item in sorted_books]
output_df = pd.DataFrame(final_books)

# Sắp xếp lại columns theo thứ tự giống books_full_data.csv
column_order = [
    'product_id', 'title', 'authors', 'original_price', 'current_price', 
    'quantity', 'category', 'n_review', 'avg_rating', 'pages', 
    'manufacturer', 'cover_link', 'summary', 'content'
]
output_df = output_df[column_order]

output_df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
print(f"\n✅ Hoàn tất! Đã lưu {OUTPUT_FILE}")

# === 7. Xóa file tạm nếu có ===
if os.path.exists(PARTIAL_FILE):
    os.remove(PARTIAL_FILE)
    print("🧹 Đã xóa file tạm.")

# === 8. Thống kê ===
print("\n" + "=" * 80)
print("📈 THỐNG KÊ:")
print(f"   - Tổng số sách: {len(final_books)}")
print(f"   - Có summary: {len([b for b in final_books if b['summary']])}/{len(final_books)}")
print(f"   - Có content (comments): {len([b for b in final_books if b['content']])}/{len(final_books)}")
print(f"   - Có product_id hợp lệ: {len([b for b in final_books if b['product_id'] > 0])}/{len(final_books)}")
print("=" * 80)

print("\n🎉 Crawl hoàn tất! File đã được lưu tại:", OUTPUT_FILE)
