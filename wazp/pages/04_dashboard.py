import dash

# import plotly.express as px
from dash import html

# import dash_bootstrap_components as dbc

######################
# Add page to registry
#########################
dash.register_page(__name__)


######################
# Layout
####################

layout = html.Div(
    className="row",
    children=[
        html.H1("Dashboard & data export"),
        html.Br(),
        html.H5("", style={"margin-top": "20px", "margin-bottom": "20px"}),
        html.Div(children=[], id="export-data-container"),
        html.H5("", style={"margin-top": "10px", "margin-bottom": "20px"}),
        html.Div(children=[], id="plots-container"),
    ],
)
