import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

dash.register_page(__name__, path="/")

# Define upload component
upload = dcc.Upload(
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
    multiple=False,  # allow multiple files upload
)

# Define layout for home page
layout = html.Div(
    children=[
        html.H1(children="Home"),
        upload,
        dbc.Alert(
            children="",
            id="upload-message",
            dismissable=False,
            fade=False,
            is_open=False,
            color="light",
        ),
    ]
)
