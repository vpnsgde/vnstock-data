import pandas as pd
from dash import dcc, html, Input, Output
import plotly.express as px
import os

# ---------- Dataset ----------
companies_file = "./dataset/basic_info/companies_vnallshare.csv"
df_companies = pd.read_csv(companies_file)
symbols = df_companies['Symbol'].tolist()

# ---------- Layout ----------
layout = html.Div([
    # html.H2("VN Stock Price History Viewer"),
    html.H2(
        "VN Stock Price History Viewer",
        style={"textAlign": "center"}
    ),
    
    html.Div([
        html.Label("Select Symbol:"),
        dcc.Dropdown(
            id="symbol-dropdown",
            options=[{"label": s, "value": s} for s in symbols],
            value="VNINDEX",
            clearable=False
        ),
    ], style={"width": "40%", "display": "inline-block", "margin-right": "20px"}),
    
    html.Div([
        html.Label("Select Time Range:"),
        dcc.Dropdown(
            id="range-dropdown",
            options=[
                {"label": "10 Years", "value": "10y"},
                {"label": "All", "value": "all"}
            ],
            value="10y",
            clearable=False
        ),
    ], style={"width": "20%", "display": "inline-block"}),
    
    dcc.Graph(
        id="price-history-chart",
        style={"height": "500px", "width": "100%"}  # full width
    )
])

# ---------- Callback (need Dash instance to register) ----------
def register_callbacks(app):
    @app.callback(
        Output("price-history-chart", "figure"),
        Input("symbol-dropdown", "value"),
        Input("range-dropdown", "value")
    )
    def update_chart(symbol, time_range):
        price_file = f"./dataset/{symbol}/PriceHistory.csv"
        
        if not os.path.exists(price_file):
            return px.line(title=f"No data for {symbol}")
        
        df_price = pd.read_csv(price_file)
        df_price['Ngay'] = pd.to_datetime(df_price['Ngay'], format="%d/%m/%Y")
        df_price['GiaDieuChinh'] = pd.to_numeric(df_price['GiaDieuChinh'], errors='coerce')
        df_price = df_price.sort_values("Ngay")
        
        # Filter by 10 years if selected
        if time_range == "10y":
            ten_years_ago = df_price['Ngay'].max() - pd.DateOffset(years=10)
            df_price = df_price[df_price['Ngay'] >= ten_years_ago]
        
        # Line chart in red with custom hover
        fig = px.line(
            df_price, x='Ngay', y='GiaDieuChinh',
            title=f"{symbol} Price History",
            hover_data={'Ngay': True, 'GiaDieuChinh': True},
            labels={'Ngay': 'Date', 'GiaDieuChinh': 'Price'}
        )
        fig.update_traces(
            line=dict(color='red', width=2),
            hovertemplate='%{x|%d/%m/%Y}, %{y:.2f}'
        )
        
        # Padding 1/5 date range on right
        date_range = df_price['Ngay'].max() - df_price['Ngay'].min()
        padding = date_range / 6
        x_end = df_price['Ngay'].max() + padding
        
        # Layout
        fig.update_layout(
            xaxis=dict(range=[df_price['Ngay'].min(), x_end]),
            xaxis_title="Date",
            yaxis_title="Adjusted Price",
            margin=dict(l=50, r=50, t=50, b=50),
            height=500
        )
        
        return fig


# ---------- Standalone run ----------
# if __name__ == "__main__":
#     from dash import Dash
#     app = Dash(__name__)
#     app.layout = layout
#     register_callbacks(app)
#     app.run(host="0.0.0.0", port=8050, debug=True)
