import requests
import pandas as pd
import plotly.express as px
from dash import dcc, html
import dash_bootstrap_components as dbc

# --------- API headers ----------
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/127.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Referer": "https://cafef.vn/",
}

def fetch_foreign_data(type_: str):
    """Fetch foreign trading data (buy/sell)"""
    url = f"https://cafef.vn/du-lieu/ajax/mobile/smart/ajaxkhoingoai.ashx?type={type_}"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    json_data = resp.json()
    data = json_data.get("Data", [])
    return pd.DataFrame(data)


# --------- Data processing ----------
df_buy = fetch_foreign_data("buy")[["Symbol", "Value"]].copy()
df_sell = fetch_foreign_data("sell")[["Symbol", "Value"]].copy()

# Convert to float
df_buy["Value"] = df_buy["Value"].astype(float)
df_sell["Value"] = df_sell["Value"].astype(float)

# Convert to bn VND
df_buy["Value"] = (df_buy["Value"] / 1e9).round(2)
df_sell["Value"] = (df_sell["Value"] / 1e9).round(2)

# Top 10
df_buy_top = df_buy.nlargest(10, "Value").sort_values("Value", ascending=True)
df_sell_top = df_sell.nlargest(10, "Value").sort_values("Value", ascending=False)

# --------- Plotly charts ----------
fig_buy = px.bar(
    df_buy_top,
    x="Value",
    y="Symbol",
    orientation="h",
    text="Value",
    color_discrete_sequence=["green"],
)
fig_buy.update_traces(
    texttemplate="%{text:.2f}",
    textposition="outside",
    hoverinfo="skip",
    hovertemplate=None,
)
fig_buy.update_layout(
    title="Top 10 Net Buy (bn VND)",
    xaxis_title="Value (bn VND)",
    yaxis_title="",
    bargap=0.3,
    height=500,
)

fig_sell = px.bar(
    df_sell_top,
    x="Value",
    y="Symbol",
    orientation="h",
    text="Value",
    color_discrete_sequence=["red"],
)
fig_sell.update_traces(
    texttemplate="%{text:.2f}",
    textposition="outside",
    hoverinfo="skip",
    hovertemplate=None,
)
fig_sell.update_layout(
    title="Top 10 Net Sell (bn VND)",
    xaxis_title="Value (bn VND)",
    yaxis_title="",
    bargap=0.3,
    height=500,
    yaxis_side="right",  # Symbol label sang phải
)

# --------- Layout (for embedding) ----------
layout = dbc.Container([
    html.H2("Foreign Trading (Real-time)", style={"textAlign": "center", "marginBottom": "30px"}),

    dbc.Row([
        dbc.Col(dcc.Graph(figure=fig_sell), width=6),  # Net Sell bên trái
        dbc.Col(dcc.Graph(figure=fig_buy), width=6),   # Net Buy bên phải
    ])
], fluid=True)


# --------- Callbacks (not needed, placeholder for consistency) ----------
def register_callbacks(app):
    pass
