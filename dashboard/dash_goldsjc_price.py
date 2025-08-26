import requests
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html

# API endpoint
url = "https://cafef.vn/du-lieu/Ajax/ajaxgoldpricehistory.ashx?index=all"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/127.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Referer": "https://cafef.vn/",
}
resp = requests.get(url, headers=HEADERS, timeout=30).json()

# Extract gold price histories
histories = resp["Data"]["goldPriceWorldHistories"]

# Build rows
rows = []
for h in histories:
    rows.append({
        "name": h["name"],
        "buyPrice": h["buyPrice"],
        "sellPrice": h["sellPrice"],
        "date": h["createdAt"].split("T")[0]  # only keep YYYY-MM-DD
    })

# Convert to DataFrame
df = pd.DataFrame(rows)

# Ensure datetime format
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date")

# Create line chart
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df["date"],
    y=df["buyPrice"],
    mode="lines",
    name="Buy Price",
    line=dict(color="blue")
))

fig.add_trace(go.Scatter(
    x=df["date"],
    y=df["sellPrice"],
    mode="lines",
    name="Sell Price",
    line=dict(color="red")
))

# Unified hover
fig.update_layout(
    title="SJC Gold Price (Buy vs Sell)",
    title_x=0.5,
    hovermode="x unified",
    plot_bgcolor="white",
    xaxis=dict(showgrid=True, gridcolor="lightgrey"),
    yaxis=dict(showgrid=True, gridcolor="lightgrey", title="Price (million VND/tael)"),
    font=dict(size=14),
    legend=dict(title="", orientation="h", y=-0.2, x=0.5, xanchor="center"),
    hoverlabel=dict(font_size=11),
    height=600 
)

# Hover template
fig.update_traces(
    hovertemplate="%{y}tr VND"
)

# Export layout để dùng trong overview_dashboard
layout = html.Div([
    html.H2("SJC Gold Price Dashboard", style={"textAlign": "center"}),
    dcc.Graph(figure=fig, id="gold_chart")
])

# Nếu có callback thì thêm ở đây, hiện tại không cần
def register_callbacks(app):
    pass
