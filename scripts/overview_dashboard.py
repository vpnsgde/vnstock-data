import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dash import Dash, html
import dash_bootstrap_components as dbc

# Import các dashboard con
from dashboard import (
    dash_price_history,
    dash_foreign_trading,
    dash_heatmap,
    # dash_chart_header,
    dash_vnindex_pe,
    dash_goldsjc_price,
    dash_bank_deposit_rate,
    dash_usd_exchange_rate,
    dash_live_currency_rate
)
from dashboard import dash_live_currency_rate

# Khởi tạo app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# ---------------- Layout ----------------
app.layout = dbc.Container([
    dbc.Row(
        dbc.Col(
            html.H1(
                "📊 Vietnam Financial Market Overview Dashboard",
                style={
                    "textAlign": "center",
                    "marginBottom": "100px",
                    "marginTop": "50px"
                }
            ),
            width=12
        )
    ),

    dbc.Row([
        dbc.Col(dash_price_history.layout, width=7),
        dbc.Col(dash_foreign_trading.layout, width=5),
        # dbc.Col(dash_chart_header.layout, width=3),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(dash_heatmap.layout, width=6),
        dbc.Col(dash_vnindex_pe.layout, width=6),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(dash_goldsjc_price.layout, width=6),
        dbc.Col(dash_bank_deposit_rate.layout, width=6),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(dash_usd_exchange_rate.layout, width=6),
        dbc.Col(dash_live_currency_rate.layout, width=6),
    ], className="mb-4"),
], fluid=True)

# ---------------- Callbacks ----------------
dash_price_history.register_callbacks(app)
dash_foreign_trading.register_callbacks(app)
dash_heatmap.register_callbacks(app)
dash_vnindex_pe.register_callbacks(app)
dash_goldsjc_price.register_callbacks(app)
dash_bank_deposit_rate.register_callbacks(app)
dash_usd_exchange_rate.register_callbacks(app)
dash_live_currency_rate.register_callbacks(app)

# ---------------- Run ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=True)
