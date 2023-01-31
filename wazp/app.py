# -*- coding: utf-8 -*-

import callbacks
import dash
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html

# Initialise app
app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
    # TODO: is there an alternative to prevent error w/ chained callbacks?
)

# Sidebar style
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# Sidebar component definition
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

# Main content style
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

# Main content component definition
content = html.Div(
    id="page-content", style=CONTENT_STYLE, children=dash.page_container
)


# Define app layout
app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


# Load callbacks
callbacks.get_metadata_callbacks(app)


# Driver
if __name__ == "__main__":
    app.run_server(debug=True)
