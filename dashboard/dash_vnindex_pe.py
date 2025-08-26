import requests
import pandas as pd
from dash import dcc, html
import plotly.graph_objects as go
from datetime import datetime, timedelta

# API URL
API_URL = "https://cafef.vn/du-lieu/Ajax/PageNew/FinanceData/GetDataChartPE.ashx"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/127.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Referer": "https://cafef.vn/",
}

# ---------- Core Logic ----------
def get_figure():
    # Fetch JSON
    resp = requests.get(API_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    json_data = resp.json()

    # Extract DataChart
    data_chart = json_data.get("Data", {}).get("DataChart", [])
    df = pd.DataFrame(data_chart)

    if df.empty:
        return go.Figure().update_layout(title="No data available")

    # Ensure correct datatypes
    df['Time'] = pd.to_datetime(df['TimeStamp'], unit='s', errors='coerce')
    df['Pe'] = pd.to_numeric(df['Pe'], errors='coerce')
    df['Index'] = pd.to_numeric(df['Index'], errors='coerce')
    df = df.dropna(subset=['Time', 'Pe', 'Index'])

    # Filter last 3 years
    three_years_ago = datetime.now() - timedelta(days=3*365)
    df = df[df['Time'] >= three_years_ago]

    # Build figure
    fig = go.Figure()

    # PE trace (left y-axis)
    fig.add_trace(go.Scatter(
        x=df['Time'],
        y=df['Pe'],
        mode='lines',
        name='PE',
        yaxis='y1',
        hovertemplate='PE: %{y}<extra></extra>'
    ))

    # Index trace (right y-axis)
    fig.add_trace(go.Scatter(
        x=df['Time'],
        y=df['Index'],
        mode='lines',
        name='Index',
        yaxis='y2',
        hovertemplate='Index: %{y}<extra></extra>'
    ))

    # -------- Thêm padding bên phải cho trục X --------
    if not df.empty:
        date_range = df['Time'].max() - df['Time'].min()
        padding = date_range / 10  # padding 1/10
        x_start = df['Time'].min()
        x_end = df['Time'].max() + padding
    else:
        x_start, x_end = None, None

    # Update layout for dual y-axis
    fig.update_layout(
        title='VNIndex PE and Index (Last 3 Years)',
        xaxis=dict(title='Time', range=[x_start, x_end]),
        yaxis=dict(title='PE', side='left'),
        yaxis2=dict(title='Index', overlaying='y', side='right'),
        hovermode='x unified',
        height=600
    )

    return fig

# ---------- Layout (for embedding) ----------
layout = html.Div([
    html.H2("VNIndex & PE Interactive Chart", style={"textAlign": "center"}),
    dcc.Graph(figure=get_figure(), id="vnindex-pe-chart")
])

# (optional) nếu file này không có callback thì thêm stub rỗng
def register_callbacks(app):
    pass
