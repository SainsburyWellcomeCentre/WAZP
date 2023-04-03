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
        html.H5(
            "Input data", style={"margin-top": "20px", "margin-bottom": "20px"}
        ),
        html.Div(children=[], id="input-data-container"),
        html.Div(children=[], id="custom-plot-container"),
        html.Div(
            [
                # html.Hr(),
                html.Div(children=[]),
                html.Div(children=[]),
            ]
        ),
    ],
)
