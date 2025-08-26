import sqlite3
import os

# Thư mục database
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database")

# Danh sách các database
DATABASES = ["basic_info.db", "price_history.db"]

def clear_database(db_path):
    """Xóa toàn bộ dữ liệu trong tất cả các bảng nhưng giữ nguyên cấu trúc và tối ưu dung lượng"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Lấy danh sách bảng
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    for (table_name,) in tables:
        # Bỏ qua các bảng hệ thống nếu có (ví dụ sqlite_sequence)
        if table_name.startswith("sqlite_"):
            continue
        sql = f"DELETE FROM {table_name};"
        print(f"Clearing table: {table_name}")
        cursor.execute(sql)
    
    conn.commit()
    
    # Tối ưu dung lượng database
    print("Running VACUUM to reclaim space...")
    cursor.execute("VACUUM;")
    conn.close()
    
    print(f"All tables cleared and database vacuumed: {os.path.basename(db_path)}\n")

if __name__ == "__main__":
    for db_name in DATABASES:
        db_path = os.path.join(DB_DIR, db_name)
        if os.path.exists(db_path):
            clear_database(db_path)
        else:
            print(f"Database not found: {db_name}")
