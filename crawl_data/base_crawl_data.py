import requests
import pandas as pd
import time
from bs4 import BeautifulSoup
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import threading

# === ⚙️ Cấu hình ===
INPUT_FILE = "dataset/book_data.csv"
OUTPUT_FILE = "summary_api/books_summary_5.csv"
PARTIAL_FILE = "summary_api/books_summary_partial.csv"
MAX_BOOKS = 1000  # 🧠 Sửa ở đây: số lượng sách muốn lấy (VD: 5 sách đầu tiên)
SAVE_EVERY = 20        # auto-save mỗi 20 sách
MAX_WORKERS = 8        # 🧠 Số threads chạy song song (không nên quá 10 để tránh bị ban)
DELAY_BETWEEN_REQUESTS = 0.5  # Giây delay giữa các request trong cùng thread

# === 1. Đọc file CSV gốc ===
df = pd.read_csv(INPUT_FILE)
SKIP = 800  # 🧠 số lượng sách muốn bỏ qua
df = df.iloc[SKIP:SKIP + MAX_BOOKS]
# === 2. Hàm lấy mô tả từ Google Books API ===
def get_description_google(title, author):
    query = f"intitle:{title}+inauthor:{author}"
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&langRestrict=vi"
    try:
        res = requests.get(url, timeout=10).json()
        items = res.get("items", [])
        if not items:
            return None
        volume_info = items[0].get("volumeInfo", {})
        desc = volume_info.get("description")
        if desc:
            return desc.replace("\n", " ").strip()
    except Exception as e:
        print(f"❌ Lỗi Google Books: {e}")
    return None

# === 3. Hàm fallback: Lấy mô tả từ Tiki.vn ===
def get_description_tiki(title):
    try:
        url = f"https://tiki.vn/api/v2/products?q={title}"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10).json()
        data = res.get("data", [])
        if not data:
            return None
        product_id = data[0]["id"]
        detail_url = f"https://tiki.vn/api/v2/products/{product_id}"
        detail_res = requests.get(detail_url, headers=headers, timeout=10).json()
        desc_html = detail_res.get("description")
        if desc_html:
            soup = BeautifulSoup(desc_html, "html.parser")
            return soup.get_text(separator=" ").strip()
    except Exception as e:
        print(f"❌ Lỗi Tiki: {e}")
    return None

# === 4. Hàm xử lý một sách (để chạy trong thread) ===
def process_single_book(row_data):
    """Xử lý một sách và trả về kết quả"""
    i, row = row_data
    product_id = row["product_id"]
    title = row["title"]
    author = row["authors"]
    
    thread_id = threading.current_thread().ident
    print(f"\n📚 [Thread-{thread_id}] ({i+1}/{len(df)}) Đang lấy: {title[:50]}...")

    summary = get_description_google(title, author)
    if summary:
        print(f"✅ [Thread-{thread_id}] Google Books: {title[:30]}...")
    else:
        print(f"⚙️ [Thread-{thread_id}] Thử Tiki: {title[:30]}...")
        summary = get_description_tiki(title)
        if summary:
            print(f"✅ [Thread-{thread_id}] Tiki: {title[:30]}...")
        else:
            print(f"❌ [Thread-{thread_id}] Không tìm thấy: {title[:30]}...")

    # Delay để tránh spam API
    time.sleep(DELAY_BETWEEN_REQUESTS)
    
    return {"product_id": product_id, "summary": summary or "", "index": i}

# === 5. Multithreading processing ===
summaries = []
completed_count = 0
lock = Lock()  # Để thread-safe khi ghi file

# Chuẩn bị dữ liệu cho ThreadPool
book_data = [(i, row) for i, row in df.iterrows()]

print(f"🚀 Bắt đầu xử lý {len(book_data)} sách với {MAX_WORKERS} threads...")

with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    # Submit tất cả tasks
    future_to_book = {executor.submit(process_single_book, book): book for book in book_data}
    
    # Xử lý kết quả khi hoàn thành
    for future in as_completed(future_to_book):
        try:
            result = future.result()
            
            with lock:  # Thread-safe
                summaries.append(result)
                completed_count += 1
                
                print(f"📊 Hoàn thành: {completed_count}/{len(df)} sách")
                
                # Auto-save mỗi SAVE_EVERY sách
                if completed_count % SAVE_EVERY == 0:
                    # Sắp xếp theo index gốc trước khi lưu
                    sorted_summaries = sorted(summaries, key=lambda x: x['index'])
                    temp_df = pd.DataFrame([{k: v for k, v in item.items() if k != 'index'} 
                                          for item in sorted_summaries])
                    temp_df.to_csv(PARTIAL_FILE, index=False, quoting=1)
                    print(f"💾 Auto-save: {PARTIAL_FILE} ({completed_count} sách)")
                    
        except Exception as e:
            print(f"❌ Lỗi xử lý: {e}")

print(f"✅ Hoàn tất tất cả {completed_count} sách!")

# === 6. Ghi ra file cuối (sắp xếp theo thứ tự gốc) ===
sorted_summaries = sorted(summaries, key=lambda x: x['index'])
final_summaries = [{k: v for k, v in item.items() if k != 'index'} for item in sorted_summaries]
output_df = pd.DataFrame(final_summaries)
output_df.to_csv(OUTPUT_FILE, index=False, quoting=1)
print(f"\n✅ Hoàn tất! Đã lưu {OUTPUT_FILE}")

# === 7. Xóa file tạm nếu có ===
if os.path.exists(PARTIAL_FILE):
    os.remove(PARTIAL_FILE)
    print("🧹 Đã xóa file tạm.")
    
print(f"📈 Thống kê: {len([s for s in final_summaries if s['summary']])}/{len(final_summaries)} sách có summary")