# import base64
# import pdb

import dash
import pandas as pd
import plotly.express as px
import yaml
from dash import dash_table, dcc, html

import wazp.utils as utils

dash.register_page(__name__)


##############################
# Build table for input data selection

# dataframe
cfg_path = """/Users/sofia/Documents_local/Zoo_SWC project/
WAZP/sample_project_2/input_config.yaml"""
with open(cfg_path, "r") as stream:
    cfg = yaml.safe_load(stream)  # base64.b64decode(content_str))
video_dir = cfg["videos_dir_path"]
with open(cfg["metadata_fields_file_path"]) as mdf:
    metadata_fields_dict = yaml.safe_load(mdf)

df_metadata = utils.df_from_metadata_yaml_files(
    video_dir, metadata_fields_dict
)
df_metadata = df_metadata[[cfg["metadata_key_field_str"]]]

# table component
table_h5_data = dash_table.DataTable(
    id="hdata-table",
    data=df_metadata.to_dict("records"),
    selected_rows=[],
    row_selectable="multi",
    fixed_rows={"headers": True},
    page_size=4,
    page_action="native",
    sort_action="native",
    sort_mode="single",
    style_table={
        "height": "200px",
        "maxHeight": "200px",
        # css overwrites the table height when fixed_rows is enabled;
        # setting height and maxHeight to the same value seems a quick
        # hack to fix it
        # (see https://community.plotly.com/t/
        # setting-datatable-max-height-when-using-fixed-headers/26417/10)
        "width": "100%",
        "maxWidth": "100%",
        "overflowY": "scroll",
        "overflowX": "scroll",
    },
    style_cell={  # refers to all cells (the whole table)
        "textAlign": "left",
        "padding": 7,
        "fontFamily": "Helvetica",
    },
)

##########################
# Read dataframe for one h5 file
df = pd.DataFrame(
    {
        "x": [1, 2, 1, 2],
        "y": [1, 2, 3, 4],
        "customdata": [1, 2, 3, 4],
        "fruit": ["apple", "apple", "orange", "orange"],
    }
)

########################
# Prepare figures
# Trajectories
fig_trajectories = px.scatter(
    df,
    x="x",
    y="y",
    color="fruit",
    custom_data=["customdata"],
    title="Raw trajectories",
)
fig_trajectories.update_layout(clickmode="event+select")
fig_trajectories.update_traces(marker_size=20)

# Heatmap
fig_heatmap = px.scatter(
    df,
    x="x",
    y="y",
    color="fruit",
    custom_data=["customdata"],
    title="Heatmap",
)
fig_heatmap.update_layout(clickmode="event+select")
fig_heatmap.update_traces(marker_size=20)


# Barplot occupancy
fig_barplot = px.scatter(
    df,
    x="x",
    y="y",
    color="fruit",
    custom_data=["customdata"],
    title="Barplot occupancy",
)
fig_barplot.update_layout(clickmode="event+select")
fig_barplot.update_traces(marker_size=20)


# Entries/exits matrix
fig_entries_exits = px.scatter(
    df,
    x="x",
    y="y",
    color="fruit",
    custom_data=["customdata"],
    title="Entries/exits matrix",
)
fig_entries_exits.update_layout(clickmode="event+select")
fig_entries_exits.update_traces(marker_size=20)


###############
# Dashboard layout
variable_name = ["a", "c", "d"]
layout = html.Div(
    className="row",
    children=[
        html.H1("Dashboard"),
        html.Br(),
        html.H5(
            "Input data", style={"margin-top": "20px", "margin-bottom": "10px"}
        ),
        html.Div(
            [
                table_h5_data,
                html.Hr(),
                html.Div(
                    children=[
                        dcc.Graph(
                            id="graph-trajectories",
                            figure=fig_trajectories,
                            style={"width": "49%", "display": "inline-block"},
                        ),
                        dcc.Graph(
                            id="graph-heatmap",
                            figure=fig_heatmap,
                            style={
                                "width": "49%",
                                "display": "inline-block",
                                "float": "right",
                            },
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        dcc.Graph(
                            id="graph-barplot",
                            figure=fig_barplot,
                            style={"width": "49%", "display": "inline-block"},
                        ),
                        dcc.Graph(
                            id="graph-entries-exits",
                            figure=fig_entries_exits,
                            style={
                                "width": "49%",
                                "display": "inline-block",
                                "float": "right",
                            },
                        ),
                    ]
                ),
            ]
        ),
    ],
)
