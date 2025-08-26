import requests
import pandas as pd
from dash import dcc, html, Input, Output
import plotly.express as px

API_URL = "https://cafef.vn/du-lieu/ajax/mobile/smart/ajaxbandothitruong.ashx"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/127.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Referer": "https://cafef.vn/"
}

# -------- Layout (for embedding) --------
layout = html.Div([
    html.H2("Market Heatmap (Real-time)", style={"textAlign": "center"}),
    dcc.Graph(id="heatmap"),
    dcc.Interval(
        id="interval-update-heatmap",
        interval=60*1000,  # refresh mỗi 10 giây
        n_intervals=0
    )
], style={"width": "95%", "margin": "auto"})


# -------- Callback registration --------
def register_callbacks(app):
    @app.callback(
        Output("heatmap", "figure"),
        Input("interval-update-heatmap", "n_intervals")
    )
    def update_heatmap(n):
        try:
            response = requests.get(API_URL, headers=HEADERS, timeout=30)
            response.raise_for_status()
            data = response.json()

            records = []
            for item in data.get("Data", []):
                records.append({
                    "symbol": item.get("Symbol"),
                    "name": item.get("Name"),
                    "marketCap": item.get("MarketCap", 0),
                    "changePercent": item.get("ChangePercent", 0),
                    "price": item.get("Price", 0),
                    "volume": item.get("TotalVolume", 0)
                })

            if not records:
                return px.scatter(title="No data available")

            df = pd.DataFrame(records)

            # Treemap
            fig = px.treemap(
                df,
                path=[df["symbol"]],
                values="marketCap",
                color="changePercent",
                color_continuous_scale=['red', 'white', 'green'],
                hover_data=["name", "price", "volume", "changePercent"],
                custom_data=["price", "changePercent"]
            )

            # Text trong ô: price + %change
            fig.data[0].text = [
                f"{row['price']} ({row['changePercent']:.2f}%)"
                for _, row in df.iterrows()
            ]

            # Style
            fig.update_traces(
                textposition="middle center",
                insidetextfont=dict(size=12, color="black"),
                marker=dict(line=dict(width=0.5, color="lightgrey")),
                hoverinfo="skip",
                hovertemplate=None,
                customdata=df[["price", "changePercent"]].values
            )

            fig.update_layout(margin=dict(t=50, l=25, r=25, b=25), height=500)
            return fig

        except Exception as e:
            print("Error fetching data:", e)
            return px.scatter(title="Error fetching data")


# -------- Standalone run --------
# if __name__ == "__main__":
#     from dash import Dash
#     app = Dash(__name__)
#     app.layout = layout
#     register_callbacks(app)
#     app.run(host="0.0.0.0", port=8050, debug=True)
