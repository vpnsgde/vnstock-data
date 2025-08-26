# README - basic_info.py

## GIỚI THIỆU

File `basic_info.py` nằm trong thư mục `scripts/`. Đây là một script **ETL (Extract - Transform - Load)** có nhiệm vụ thu thập dữ liệu cơ bản từ API của **CafeF** và **SSI**, sau đó xử lý và xuất ra các file CSV trong thư mục `./dataset/basic_info/`.

**Mục tiêu chính:**
- **Extract**: Lấy dữ liệu từ các API công khai.
- **Transform**: Lọc các trường quan trọng, sắp xếp, xử lý định dạng ngày tháng.
- **Load**: Xuất dữ liệu thành file CSV để dễ dàng quản lý và phân tích.

---

## CÁC CHỨC NĂNG CHÍNH

**1. Thu thập thông tin ngân hàng**
- Hàm: `save_banks_info()`
- API: `https://cafef.vn/du-lieu/ajax/pagenew/databusiness/BankList.ashx`
- Xuất file: `banks_info.csv`
- Trường dữ liệu:
  - `Index` (số thứ tự)
  - `Symbol` (mã ngân hàng)
  - `FullName` (tên đầy đủ)
  - `TradeCenterId` (sàn giao dịch: HOSE, HNX, UPCOM)

---

**2. Thu thập thông tin công ty chứng khoán**
- Hàm: `save_brokers_info()`
- API:` https://cafef.vn/du-lieu/ajax/pagenew/databusiness/stocklist.ashx`
- Xuất file: `brokers_info.csv`
- Trường dữ liệu: giống như ngân hàng (`Symbol`, `FullName`, `TradeCenterId`, `Index`).

---

**3. Thu thập thông tin quỹ đầu tư**
- Hàm: `save_funds_info()`
- API: `https://cafef.vn/du-lieu/ajax/pagenew/databusiness/fund.ashx`
- Xuất file: `funds_info.csv`
- Trường dữ liệu:
  - `Index` (số thứ tự)
  - `StockSymbol` (mã quỹ)
  - `FullName` (tên quỹ)
  - `ManagementCompany` (công ty quản lý)
  - `Type` (loại quỹ)
  - `PlaceRegistration` (nơi đăng ký)
  - `NetAssetsValue` (giá trị tài sản ròng)
  - `CurrencyName` (đơn vị tiền tệ)
  - `EstablishedDate` (ngày thành lập, đã được xử lý từ timestamp về dạng *YYYY-MM-DD*)

---

**4. Thu thập thông tin ngành nghề**
- Hàm: `save_sectors_info()`
- API: `https://iboard-api.ssi.com.vn/statistics/company/sectors-data`
- Xuất file: `sectors_info.csv`
- Trường dữ liệu:
  - `industry_name_vi` (tên ngành tiếng Việt)
  - `industry_name_vn` (tên ngành bản địa hoá)
  - `industry_name_en` (tên ngành tiếng Anh)
  - `industry_code` (mã ngành)
  - `industry_level` (cấp độ ngành)
  - `industry_close_index` (chỉ số ngành)
  - `company_symbols` (danh sách mã cổ phiếu thuộc ngành, cách nhau bởi dấu ,)

---

**5. Thu thập danh sách công ty niêm yết (VNAllshare)**
- Hàm: `save_companies_vnallshare()`
- API: `https://cafef.vn/du-lieu/ajax/pagenew/databusiness/congtyniemyet.ashx?take=1661`
- Xuất file: `companies_vnallshare.csv`
- Trường dữ liệu:
  - `Index` (số thứ tự)
  - `Symbol` (mã cổ phiếu)
  - `TradeCenterId` (sàn giao dịch)
  - `CategoryId` (ID loại hình doanh nghiệp)
  - `CompanyName` (tên công ty)
  - `CategoryName` (tên loại hình doanh nghiệp)

---

## CÁCH SỬ DỤNG

1. Chạy trực tiếp file `basic_info.py`:
`   python scripts/basic_info.py
`
2. Script sẽ tự động:
   - Gọi tất cả các hàm thu thập dữ liệu.
   - Xuất 5 file CSV tương ứng vào thư mục `./dataset/basic_info/`.

3. Các file được tạo:
   - `banks_info.csv`
   - `brokers_info.csv`
   - `funds_info.csv`
   - `sectors_info.csv`
   - `companies_vnallshare.csv`

---

## GHI CHÚ KỸ THUẬT

- Headers: script sử dụng **HEADERS_CAFEF** và **HEADERS_SSI** để giả lập trình duyệt, tránh bị chặn `request`.
- Xử lý ngày tháng: trường `EstablishedDate` trong dữ liệu quỹ có định dạng `/Date(1687651200000)/`. Script đã xử lý về chuẩn ISO YYYY-MM-DD.
- Thư mục lưu file: nếu thư mục `./dataset/basic_info/` chưa tồn tại, script sẽ tự động tạo.

---

## KẾT LUẬN

File `basic_info.py` là công cụ hữu ích để:
- Thu thập dữ liệu cơ bản về ngân hàng, công ty chứng khoán, quỹ đầu tư, ngành nghề và toàn bộ công ty niêm yết tại Việt Nam.
- Tạo nguồn dữ liệu CSV chuẩn hoá, phục vụ cho các bước phân tích hoặc nhập vào cơ sở dữ liệu sau này.
