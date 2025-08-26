import requests
import pandas as pd
from dash import dash_table, html

API_URL = "https://cafef.vn/du-lieu/ajax/mobile/smart/ajaxtygia.ashx"

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
    """Fetch and process USD currency pairs from CAFEF API"""
    response = requests.get(API_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    data = response.json()

    if "Data" not in data:
        raise ValueError("Unexpected JSON structure from API")

    df = pd.DataFrame(data["Data"])

    if "Code" not in df.columns or "CurrentRate" not in df.columns:
        raise ValueError("Missing expected fields 'Code' or 'CurrentRate'")

    # Filter USD at end (…USD)
    df_usd_end = df[df["Code"].str.endswith("USD", na=False)]

    # Filter USD at beginning (USD…)
    df_usd_start = df[df["Code"].str.startswith("USD", na=False)]

    # Combine: USD at end first, then USD at start
    df_final = pd.concat([df_usd_end, df_usd_start], ignore_index=True)
    return df_final


# Build DataTable (one-time fetch for static display)
df_final = fetch_data()

layout = html.Div([
    html.H2("Live Currency Rates (USD Pairs)", 
            style={"textAlign": "center", "marginBottom": "20px"}),

    dash_table.DataTable(
        columns=[
            {"name": "Code", "id": "Code"},
            {"name": "Current Rate", "id": "CurrentRate"},
        ],
        data=df_final.to_dict("records"),

        # Style
        style_cell={
            'textAlign': 'center',
            'padding': '8px',
            'fontFamily': 'Arial',
            'fontSize': '14px'
        },
        style_header={
            'backgroundColor': '#2C3E50',
            'color': 'white',
            'fontWeight': 'bold',
            'textAlign': 'center'
        },
        style_data_conditional=[
            {
                "if": {"column_id": "CurrentRate", "filter_query": "{CurrentRate} >= 1.5"},
                "backgroundColor": "#FFCCCC",
                "color": "black"
            },
            {
                "if": {"column_id": "CurrentRate", "filter_query": "{CurrentRate} < 1.5"},
                "backgroundColor": "#CCFFCC",
                "color": "black"
            }
        ],
        style_table={
            'width': '60%',
            'margin': 'auto',
            'border': '1px solid #ccc',
            'borderRadius': '8px',
            'overflow': 'hidden',
            'boxShadow': '0px 2px 5px rgba(0,0,0,0.2)'
        },
        page_size=9  # show 9 rows per page
    )
])

def register_callbacks(app):
    """No callbacks for now, but placeholder for future updates"""
    pass
