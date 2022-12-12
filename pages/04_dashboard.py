import dash
from dash import html, dcc

dash.register_page(__name__)

layout = html.Div(
    children=[
        html.H1(children="Dashboard"),
        html.Div(
            children="""
        This is the Dashboard page content.
    """
        ),
    ]
)
