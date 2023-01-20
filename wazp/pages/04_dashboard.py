# import base64
# import pdb

# import pathlib as pl
# import pdb

import dash

# import dash_bootstrap_components as dbc
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
with open(cfg_path.replace("\n", ""), "r") as stream:
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
h5_file_path = """/Users/sofia/Documents_local/Zoo_SWC project/WAZP/
sample_project_2/pose_estimation_results/jwaspE_nectar-open-
close_controlDLC_resnet50_jwasp_femaleandmaleSep12shuffle1_1000000.h5"""
df_trajectories = pd.read_hdf(h5_file_path.replace("\n", ""))
df_trajectories.columns = df_trajectories.columns.droplevel()


########################
# Prepare figures
# Trajectories
fig_trajectories = px.scatter(
    df_trajectories["head"],
    x="x",
    y="y",
    labels={
        "x": "x-axis (px)",
        "y": "y-axis (px)",
        "likelihood": "likelihood",
    },
    color="likelihood",
    custom_data=df_trajectories["head"].columns,
    title="Raw trajectories",
)
fig_trajectories.update_layout(
    clickmode="event+select",
    # title={
    #     'text': 1, #"Raw trajectories",
    #     'y': 0.9,
    #     'x': 0.5,
    #     'xanchor': 'center',
    #     'yanchor': 'top'
    # }
)
fig_trajectories.update_yaxes(
    scaleanchor="x",
    scaleratio=1,
)
fig_trajectories.update_traces(marker_size=5)

# Heatmap
fig_heatmap = px.scatter(
    df_trajectories["head"],
    x="x",
    y="y",
    color="likelihood",
    custom_data=df_trajectories["head"].columns,
    title="Heatmap",
)
fig_heatmap.update_layout(clickmode="event+select")
fig_heatmap.update_traces(marker_size=5)


# Barplot occupancy
fig_barplot = px.scatter(
    df_trajectories["head"],
    x="x",
    y="y",
    color="likelihood",
    custom_data=df_trajectories["head"].columns,
    title="Barplot occupancy",
)
fig_barplot.update_layout(clickmode="event+select")
fig_barplot.update_traces(marker_size=5)


# Entries/exits matrix
fig_entries_exits = px.scatter(
    df_trajectories["head"],
    x="x",
    y="y",
    color="likelihood",
    custom_data=df_trajectories["head"].columns,
    title="Entries/exits matrix",
)
fig_entries_exits.update_layout(clickmode="event+select")
fig_entries_exits.update_traces(marker_size=5)


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
        html.Div(children=[], id="table-container"),
        html.Div(
            [
                html.Hr(),
                html.Div(  # first row
                    children=[
                        html.Div(  # figure and radio item first row left
                            [
                                dcc.Graph(
                                    id="graph-trajectories",
                                    figure=fig_trajectories,
                                    style={
                                        "width": "85%",
                                        "display": "inline-block",
                                    },
                                ),
                                dcc.RadioItems(
                                    ["likelihood", "frame", "input data"],
                                    "likelihood",
                                    style={
                                        "width": "15%",
                                        "float": "right",
                                        "margin-top": "110px",
                                    },
                                    labelStyle={
                                        "display": "block",
                                        "fontSize": ".8rem",
                                    },
                                ),
                            ],
                            style={"width": "49%", "display": "inline-block"},
                        ),
                        dcc.Graph(  # figure first row right
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
                html.Div(  # second row figures
                    children=[
                        dcc.Graph(
                            id="graph-barplot",
                            figure=fig_barplot,
                            style={"width": "42%", "display": "inline-block"},
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
