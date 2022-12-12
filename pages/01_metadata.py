# Define the page's content within a variable called layout or 
# a function called layout that returns the content.

import dash
from dash import html, dcc

dash.register_page(__name__)

layout = html.Div(
    children=[
        html.H1(children="This is the Metadata page"),
        html.Div(
            children="""
        This is the Metadata page content.
    """
        ),
    ]
)
