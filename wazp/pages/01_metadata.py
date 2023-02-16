import dash
from dash import html

######################
# Add page to registry
#########################
dash.register_page(__name__)


###############
# Layout
################
# Metadata layout
layout = html.Div(
    children=[
        html.H1(children="Metadata"),
        html.Div(
            id="output-metadata", style={"height": "1200px"}, children=[]
        ),  # component to hold the output from the data upload
    ]
)
