# Define the page's content within a variable called layout or
# a function called layout that returns the content.

import dash
from dash import dcc, html


###############
# Register this page
# Notes:
# - dash.page_registry is an ordered dict:
#   - keys: pages.<name of file under pages dir>
#   - values: a few attributes of the page...including 'layout'
dash.register_page(__name__)

######################
# Define upload component
upload = dcc.Upload(
    id="upload-data",
    children=html.Div(
        ["Drag and Drop or ", html.A("Select project config file")]
    ),
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
    # Allow multiple files to be uploaded
    multiple=False,
)


########################
# Define layout
layout = html.Div(
    children=[
        html.H1(children="Metadata"),
        upload,  # upload component
        html.Div(
            id="output-data-upload", style={"height": "1200px"}
        ),  # component to hold the output from the data upload
    ]
)
