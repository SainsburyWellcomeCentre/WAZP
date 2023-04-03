import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

######################
# Add page to registry
#########################
dash.register_page(__name__, path="/")

###############
# Components
################
# Upload component for project config
upload_component = dcc.Upload(
    id="upload-data",
    children=html.Div(
        ["Drag and Drop or ", html.A("Select project config file")]
    ),
    contents=None,
    style={
        "width": "100%",
        "height": "60px",
        "lineHeight": "60px",
        "borderWidth": "1px",
        "borderStyle": "dashed",
        "borderRadius": "5px",
        "textAlign": "center",
        "margin": "10px",
    },
    multiple=False,
)

# Upload message
upload_message = dbc.Alert(
    id="upload-message",
    children="",
    dismissable=False,
    fade=False,
    is_open=False,
    color="light",
    style={
        "textAlign": "left",
        "margin": "10px",
        "width": "100%",
    },
)

###############
# Layout
################
layout = html.Div(
    children=[
        html.H1(children="Home"),
        upload_component,
        upload_message,
    ]
)
