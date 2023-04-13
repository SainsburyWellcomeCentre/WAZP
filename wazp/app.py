# -*- coding: utf-8 -*-

import pdb

import dash
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html

import wazp.callbacks.dashboard as dashboard
import wazp.callbacks.metadata as metadata
import wazp.callbacks.roi as roi
from wazp.callbacks.home import *
from wazp.initialise import app

app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
    # TODO: is there an alternative to prevent error w/ chained callbacks?
)


###############
# Components
###############
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

# Sidebar component
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
                    href=page["relative_path"],  # url of each page
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

# Main content component
content = html.Div(
    id="page-content",
    children=dash.page_container,
    style=CONTENT_STYLE,
)

# Storage component for the session
storage = dcc.Store(
    id="session-storage",
    storage_type="session",
    data=tuple(),
)

###############
# Layout
################
app.layout = html.Div(
    [
        dcc.Location(id="url"),
        sidebar,
        content,
        storage,
    ]
)


###############
# Callbacks
################
# home.random_function()  # get_callbacks(app)
# app.(save_input_config_to_storage)
metadata.get_callbacks(app)
roi.get_callbacks(app)
dashboard.get_callbacks(app)


def startwazp():
    app.run_server(debug=True)


###############
# Driver
################
if __name__ == "__main__":
    startwazp()
