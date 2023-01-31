# Define the page's content within a variable called layout or
# a function called layout that returns the content.

import dash
from dash import html

# Register this page
# - dash.page_registry is an ordered dict with :
#   - keys: pages.<name of file under pages dir>
#   - values: a few attributes of the page...including 'layout'
dash.register_page(__name__)


# Metadata layout
layout = html.Div(
    children=[
        html.H1(children="Metadata"),
        html.Div(
            id="output-data-upload", style={"height": "1200px"}, children=[]
        ),  # component to hold the output from the data upload
    ]
)
