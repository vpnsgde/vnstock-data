# README - Vietnam Financial Market Overview Dashboard

## Giới thiệu
File `app.py` là file chính để khởi tạo và chạy dashboard tổng quan về thị trường tài chính Việt Nam. 
Dashboard này hiển thị các thông tin như giá chứng khoán, giao dịch nước ngoài, heatmap, chỉ số VNIndex PE, giá vàng SJC, lãi suất ngân hàng, tỷ giá USD và tỷ giá tiền tệ trực tiếp.

Dashboard được xây dựng trên **Dash** và sử dụng **Bootstrap** để dễ dàng bố trí layout responsive.

---

## Cấu trúc file

### 1. Import thư viện
```python
from dash import Dash, html
import dash_bootstrap_components as dbc
```

- `Dash`: Tạo ứng dụng Dash.
- `html`: Tạo các component HTML cơ bản (H1, Div, P...).
- `dash_bootstrap_components(dbc)`: Dùng để tạo layout theo Bootstrap.

### 2. Import các dashboard con

```python
from dashboard import (
    dash_price_history,
    dash_foreign_trading,
    dash_heatmap,
    dash_vnindex_pe,
    dash_goldsjc_price,
    dash_bank_deposit_rate,
    dash_usd_exchange_rate,
    dash_live_currency_rate
)
```

- Mỗi dashboard con được tách thành module riêng để dễ quản lý.
- Mỗi module có:
    - `layout`: cấu trúc giao diện.
    - `register_callbacks(app)`: đăng ký callback xử lý tương tác dữ liệu.

### 3. Khởi tạo ứng dụng Dash

```python
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP]) 
```

- Sử dụng theme `Bootstrap` để dashboard đẹp và responsive.

- `__name__` giúp Dash xác định vị trí file và assets.

### 4. Layout tổng thể

```python
app.layout = dbc.Container([...], fluid=True)
```
- `dbc.Container`: khung chính của dashboard.

- `fluid=True`: chiếm toàn bộ chiều ngang màn hình.

- **Dashboard** được chia thành nhiều **Row** và **Col** theo mô hình lưới **Bootstrap**.

**a) Header**

Hiển thị tiêu đề dashboard:

```python
html.H1(
    "📊 Vietnam Financial Market Overview Dashboard",
    style={"textAlign": "center", "marginBottom": "100px", "marginTop": "50px"}
)
```

**b) Các row chính**

- Row 1: Giá chứng khoán và giao dịch nước ngoài

    - `dash_price_history.layout` (7/12)

    - `dash_foreign_trading.layout `(5/12)

- Row 2: Heatmap & VNIndex PE

    - Cả hai chiếm 6/12 ngang bằng nhau.

- Row 3: Giá vàng & lãi suất ngân hàng

    - Cả hai chiếm 6/12 ngang bằng nhau.

- Row 4: Tỷ giá USD & tỷ giá tiền tệ trực tiếp

    - Cả hai chiếm 6/12 ngang bằng nhau.

`className="mb-4"`: thêm khoảng cách giữa các row.

### 5. Đăng ký callback

```python
dash_price_history.register_callbacks(app)
dash_foreign_trading.register_callbacks(app)
...
dash_live_currency_rate.register_callbacks(app)
```

- Mỗi module con có hàm `register_callbacks(app)` để liên kết dữ liệu và tương tác động.

### 6. Chạy ứng dụng

```python
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=True)
```

- `host="0.0.0.0"`: cho phép truy cập từ tất cả IP trong mạng.

- `port=8050`: cổng chạy ứng dụng.

- `debug=True`: bật chế độ gỡ lỗi và tự reload khi thay đổi code.

### Tổng kết

1. Dashboard được chia thành các module con, mỗi module quản lý riêng layout và callback.

2. Sử dụng Bootstrap grid (Row/Col) để bố trí các biểu đồ trực quan, responsive.

3. Header hiển thị tiêu đề, các row chứa từng nhóm thông tin tài chính.

4. Callbacks xử lý tương tác động và cập nhật dữ liệu theo thời gian thực.

5. Chạy server Dash trên cổng 8050, có thể truy cập qua trình duyệt.
