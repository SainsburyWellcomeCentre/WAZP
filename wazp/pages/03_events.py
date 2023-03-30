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
        html.H1(children="Event tagging"),
        html.Div(
            children="""
        Define events in time.
    """
        ),
    ]
)
