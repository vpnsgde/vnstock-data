# README - save_to_database.py

## Giới thiệu

File `save_to_database.py` nằm trong thư mục `scripts/`. Đây là script chính để quản lý và khởi tạo cơ sở dữ liệu SQLite cho dự án.  

Chức năng chính của script:
- Khởi tạo 2 database: `basic_info.db` và `price_history.db` trong thư mục `database/`.
- Import dữ liệu từ các file CSV trong thư mục `dataset/` vào database tương ứng.
- Ghi log toàn bộ quá trình vào file `logs/save_to_database.txt`.

## Chức năng chính
 
### 1. Khởi tạo database

Hàm `init_databases()`:
- Kiểm tra sự tồn tại của thư mục `database/`.
- Nếu chưa có, sẽ tự động tạo.
- Tạo ra 2 file database: `basic_info.db` và `price_history.db` nếu chúng chưa tồn tại.

### 2. Import dữ liệu cơ bản (Basic Info)

Hàm `import_basic_info_db()`:
- Đọc các file CSV trong thư mục `dataset/basic_info/`.
- Mỗi file CSV sẽ trở thành một bảng trong `basic_info.db` (tên bảng trùng tên file CSV, bỏ đuôi `.csv`).
- Nếu bảng chưa tồn tại: tạo bảng mới từ file CSV.
- Nếu bảng đã tồn tại: chỉ thêm dữ liệu mới, loại bỏ các dòng trùng lặp.

### 3. Import dữ liệu lịch sử giá (Price History)

Hàm `import_price_history_db()`:
- Duyệt thư mục `dataset/`, bỏ qua thư mục `basic_info/`.
- Mỗi thư mục con được coi là một mã chứng khoán (Symbol).
- Bên trong thư mục con, mỗi file CSV sẽ trở thành một bảng trong `price_history.db` với tên chuẩn hóa: `{Symbol}_{ten_file_csv}`.
- Nếu bảng chưa tồn tại: tạo bảng mới từ file CSV.
- Nếu bảng đã tồn tại: chỉ thêm dữ liệu mới, loại bỏ trùng lặp.

### 4. Ghi log sự kiện

- Mọi sự kiện quan trọng (tạo DB, tạo bảng, cập nhật bảng, số dòng thêm mới, cảnh báo, lỗi) đều được ghi lại vào:
  ```
  logs/save_to_database.txt
  ```
- Đồng thời cũng hiển thị ra màn hình console khi chạy.

## Cách chạy

Trong thư mục gốc của dự án, chạy lệnh sau:
```bash
python scripts/saveto_database.py
```

## Yêu cầu

- Python >= 3.8
- Thư viện:
  - `sqlite3` (tích hợp sẵn)
  - `pandas`
  - `logging` (tích hợp sẵn)

Cài đặt thư viện bổ sung:
```bash
pip install pandas
```

## Cấu trúc thư mục liên quan

```
project_root/
│
├── scripts/
│   └── save_to_database.py
│
├── database/
│   ├── basic_info.db
│   └── price_history.db
│
├── dataset/
│   ├── basic_info/
│   │   ├── companies.csv
│   │   └── sectors.csv
│   │
│   ├── VNM/
│   │   ├── price_daily.csv
│   │   └── dividends.csv
│   │
│   └── FPT/
│       ├── price_daily.csv
│       └── dividends.csv
│
└── logs/
    └── save_to_database.txt
```

## Tóm tắt

`save_to_database.py` là công cụ quan trọng giúp:
- Tự động quản lý cơ sở dữ liệu SQLite cho dự án.
- Đảm bảo dữ liệu CSV trong thư mục `dataset/` luôn được đồng bộ hóa vào database.
- Hạn chế trùng lặp dữ liệu, ghi log chi tiết phục vụ kiểm tra và debug.
