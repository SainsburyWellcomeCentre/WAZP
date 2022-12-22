# -*- coding: utf-8 -*-
# From :
# https://dash.plotly.com/dash-core-components/tabs#method-1.-content-as-callback
# https://dash.plotly.com/urls
# Sidebar:
# https://dash-bootstrap-components.opensource.faculty.ai/examples/simple-sidebar/page-2
#
# Notes:
# - dash.page_registry is an ordered dict:
#   - keys: pages.<name of file under pages dir>
#   - values: a few attributes of the page...including 'layout'

import dash
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html

#######################
# initialise app
app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],  # dbc.themes.DARKLY
)

#############################
# Sidebar
# style
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}
# component
sidebar = html.Div(
    [
        html.H2("WAZP 🐝", className="display-4"),
        html.Hr(),
        html.P(
            [
                "Wasp",
                html.Br(),
                "Animal-tracking",
                html.Br(),
                "Zoo project with",
                html.Br(),
                "Pose estimation",
            ],
            className="lead",
        ),
        dbc.Nav(
            children=[
                dcc.Link(
                    children=f"{page['name']}",
                    href=page["relative_path"],  # the url
                )
                for page in dash.page_registry.values()
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

###############################
# Main content
# style (to the right of the sidebar and some padding.)
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}
# component
content = html.Div(
    id="page-content", style=CONTENT_STYLE, children=dash.page_container
)

###########################
# Define app layout
app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

######################
# Driver
if __name__ == "__main__":
    app.run_server(debug=True)
