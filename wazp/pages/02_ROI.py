import dash
from dash import html

######################
# Add page to registry
#########################
dash.register_page(__name__)

###############
# Layout
################
layout = html.Div(
    children=[
        html.H1(children="ROI definition"),
        html.Div(
            children="""
            This is the ROI definition page content.
        """
        ),
    ]
)
