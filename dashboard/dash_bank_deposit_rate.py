import requests
import pandas as pd
import plotly.express as px
from dash import dcc, html, Input, Output

# URL dữ liệu
API_URL = "https://cafef.vn/du-lieu/ajax/ajaxlaisuatnganhang.ashx"

# Các bank cần giữ lại
KEEP_SYMBOLS = ["VCB", "BID", "CTG", "AGR", "ACB", "TPB", "MBB", "HDB", "STB", "TCB", "VIB", "VPB"]

def fetch_data():
    """Fetch and normalize interest rate data from API"""
    try:
        response = requests.get(API_URL, timeout=30)
        response.raise_for_status()
        data = response.json()["Data"]
    except Exception as e:
        print("Error fetching data:", e)
        return pd.DataFrame()

    records = []
    for bank in data:
        bank_name = bank["name"]
        bank_symbol = bank["symbol"]
        if bank_symbol == "agribank":  # chuẩn hóa tên
            bank_symbol = "AGR"

        for rate in bank["interestRates"]:
            records.append({
                "bank_name": bank_name,
                "bank_symbol": bank_symbol,
                "deposit_months": rate["deposit"],
                "interest_rate": pd.to_numeric(rate["value"], errors="coerce")
            })

    df = pd.DataFrame(records)

    # Lọc mốc 3,6,9,12 tháng
    df = df[df["deposit_months"].isin([3, 6, 9, 12])]

    # Giữ các bank quan trọng
    df = df[df["bank_symbol"].isin(KEEP_SYMBOLS)]
    return df


# 👉 Layout cho overview_dashboard
layout = html.Div([
    html.H2("Bank Deposit Interest Rates",
            style={"textAlign": "center"}),

    dcc.Dropdown(
        id="bank_filter",
        options=[{"label": b, "value": b} for b in KEEP_SYMBOLS],
        value=KEEP_SYMBOLS,
        multi=True
    ),

    dcc.Graph(id="interest_rate_chart", style={"height": "600px"}),

    # Interval để refetch dữ liệu mỗi 60 giây
    dcc.Interval(id="interval_update", interval=60*1000, n_intervals=0)
])


# 👉 Callback được đăng ký từ file tổng
def register_callbacks(app):
    @app.callback(
        Output("interest_rate_chart", "figure"),
        Input("bank_filter", "value"),
        Input("interval_update", "n_intervals")
    )
    def update_chart(selected_banks, n):
        df = fetch_data()
        dff = df[df["bank_symbol"].isin(selected_banks)]

        fig = px.line(
            dff,
            x="deposit_months",
            y="interest_rate",
            color="bank_symbol",
            markers=True,
            title="Interest Rates by Deposit Months (3, 6, 9, 12)"
        )

        # Hover hiển thị bank symbol và lãi suất %
        for trace in fig.data:
            trace.customdata = [[trace.name]] * len(trace.x)
            trace.hovertemplate = "%{customdata[0]} (%{y:.2f}%)<extra></extra>"

        # Reorder traces theo lãi suất trung bình (cao -> thấp)
        if len(fig.data) > 0:
            sorted_traces = sorted(fig.data, key=lambda tr: -sum(tr.y)/len(tr.y))
            fig.data = tuple(sorted_traces)

        fig.update_layout(
            xaxis_title="Deposit Months",
            yaxis_title="Interest Rate (%)",
            hovermode="x unified",
            legend_title="Bank Symbol",
            height=600
        )
        return fig
