from dash import html

# 👉 Layout để import vào overview_dashboard
layout = html.Div([
    html.H2("Live CAFEF Chart", style={"textAlign": "center"}),

    # Nhúng iframe
    html.Iframe(
        src="https://msh-iframe.cafef.vn/chart-for-cafef-web/chart-header",
        style={
            "width": "100%",   # full width
            "height": "600px",
            "border": "none"
        }
    )
])

# 👉 Vì không có callback, chỉ cần pass
def register_callbacks(app):
    pass
