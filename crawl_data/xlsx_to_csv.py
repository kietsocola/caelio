import pandas as pd
import sys
import os

def xlsx_to_csv(xlsx_path, output_dir=None):
    # Đảm bảo file tồn tại
    if not os.path.exists(xlsx_path):
        print(f"❌ File không tồn tại: {xlsx_path}")
        return

    # Nếu không chỉ định thư mục output, dùng thư mục chứa file nguồn
    if output_dir is None:
        output_dir = os.path.dirname(xlsx_path)

    # Đọc toàn bộ sheet trong file Excel
    xls = pd.ExcelFile(xlsx_path, engine="openpyxl")
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name)
        csv_name = f"{os.path.splitext(os.path.basename(xlsx_path))[0]}_{sheet_name}.csv"
        csv_path = os.path.join(output_dir, csv_name)

        # Ghi file CSV chuẩn UTF-8
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")  # utf-8-sig để Excel mở không lỗi font
        print(f"✅ Đã chuyển sheet '{sheet_name}' → {csv_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("⚙️  Cách dùng: python xlsx_to_csv.py <đường_dẫn_đến_file.xlsx> [thư_mục_output]")
    else:
        xlsx_file = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else None
        xlsx_to_csv(xlsx_file, output_dir)
