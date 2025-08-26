import requests
import pandas as pd
import plotly.express as px
from dash import dcc, html, Output, Input
from datetime import datetime

# --------- Helper function ----------
def parse_dotnet_date(dotnet_date):
    """Convert .NET date string (/Date(…)/) -> datetime"""
    if not dotnet_date:
        return None
    timestamp = int(dotnet_date.strip("/Date()")) / 1000
    return datetime.fromtimestamp(timestamp)

# --------- API config ----------
API_URL = "https://cafef.vn/du-lieu/ajax/exchangerate/AjaxRateCurrencyByNameAndDate.ashx?name=USD&date=1y"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/127.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Referer": "https://cafef.vn/",
}

def fetch_data():
    """Fetch USD exchange rates from CAFEF API"""
    resp = requests.get(API_URL, headers=HEADERS, timeout=30)
    data = resp.json()
    records = []
    for cur in data.get("Data", []):
        rec = {
            "currencyName": cur.get("currencyName"),
            "price": cur.get("price"),
            "createdAt": parse_dotnet_date(cur.get("createdAt")),
            "tagType": cur.get("tagType"),
            "bank": cur.get("bank"),
        }
        records.append(rec)
    df = pd.DataFrame(records)
    df = df.dropna(subset=["createdAt"]).sort_values("createdAt")
    return df


# --------- Layout (for embedding) ----------
layout = html.Div([
    html.H2("USD Exchange Rate Dashboard", style={"textAlign": "center"}),

    dcc.Graph(id="rate-graph"),

    # Interval: auto refresh mỗi 10 giây
    dcc.Interval(
        id="interval-component-dollar",
        interval=60 * 1000,  # 10 giây
        n_intervals=0
    )
])


# --------- Callbacks ----------
def register_callbacks(app):
    @app.callback(
        Output("rate-graph", "figure"),
        Input("interval-component-dollar", "n_intervals")
    )
    def update_graph(n):
        df = fetch_data()
        fig = px.line(
            df,
            x="createdAt",
            y="price",
            title="USD Exchange Rate (Vietcombank)",
            markers=False,
            labels={"createdAt": "Date", "price": "Exchange Rate (VND)"},
            hover_data={
                "createdAt": True,
                "price": True,
                "currencyName": False,
                "bank": False,
                "tagType": False,
            },
        )
        fig.update_traces(
            hovertemplate="Date: %{x|%Y-%m-%d}<br>Price: %{y} VND"
        )
        fig.update_layout(
            title_x=0.5,
            plot_bgcolor="white",
            xaxis=dict(showgrid=True, gridcolor="lightgrey"),
            yaxis=dict(showgrid=True, gridcolor="lightgrey"),
            font=dict(size=14),
        )
        return fig
