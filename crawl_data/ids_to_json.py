import csv
import json

# Đường dẫn file CSV đầu vào
csv_file = "nha_sach_xua/nha_sach_xua_100_with_id.csv"

# Đường dẫn file JSON đầu ra
json_file = "ids.json"

# Danh sách chứa ID
ids = []

# Đọc file CSV với encoding utf-8-sig để xử lý BOM
with open(csv_file, newline='', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Lấy ID và strip whitespace
        id_value = row.get("ID", "").strip()
        if id_value:  # Only add non-empty IDs
            ids.append(id_value)

# Ghi ra file JSON
with open(json_file, "w", encoding='utf-8') as f:
    json.dump(ids, f, ensure_ascii=False, indent=4)

print(f"✅ Đã tạo file {json_file} chứa {len(ids)} ID.")
