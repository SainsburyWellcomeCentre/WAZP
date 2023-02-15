import pathlib as pl
import re

import dash_bootstrap_components as dbc
import utils
from dash import Input, Output, State, dash_table, dcc, html


def get_callbacks(app):
    """Return all callback functions for the dashboard tab.

    Parameters
    ----------
    app : dash.Dash
        Dash app object for which these callbacks are defined
    """

    @app.callback(
        Output("videos-table-container", "children"),
        Input("videos-table-container", "children"),
        State("session-storage", "data"),
    )
    def create_input_data_table(
        table_container_children: list, app_storage: dict
    ):
        """Create table to select videos to include in plots.

        Only videos with a matching YAML file are shown.
        If a video has a metadata YAML file, but no pose estimation results:
        they appear grayed out and cannot be selected.


        Parameters
        ----------
        table_container_children : list
            list of html elements to pass to the table container
        app_storage : dict
            data held in temporary memory storage,
            accessible to all tabs in the app

        Returns
        -------
        table_container_children
            list of html elements to pass to the table container
        """

        # Create table of videos with metadata with checkboxes
        if not table_container_children:

            # video metadata as dataframe with File column only
            df_metadata = utils.df_from_metadata_yaml_files(
                app_storage["config"]["videos_dir_path"],
                app_storage["metadata_fields"],
            )
            df_metadata = df_metadata[
                [app_storage["config"]["metadata_key_field_str"]]
            ]

            # list of metadata files
            list_videos_w_metadata = [
                pl.Path(v).stem
                for v in df_metadata[
                    app_storage["config"]["metadata_key_field_str"]
                ].tolist()
            ]

            # list of videos w/ h5 files
            # TODO: this in utils?
            list_videos_w_pose_results = []
            for f in pl.Path(
                app_storage["config"]["pose_estimation_results_path"]
            ).iterdir():
                if str(f).endswith(".h5"):
                    list_videos_w_pose_results.append(
                        re.sub("DLC.*$", "", f.stem)
                    )

            # append status of h5 to table
            pose_data_str = "Pose data available?"
            df_metadata[pose_data_str] = [
                "✔️" if v in list_videos_w_pose_results else "❌"
                for v in list_videos_w_metadata
            ]

            # table component
            table_container_children = [
                dash_table.DataTable(
                    id="video-data-table",
                    data=df_metadata.to_dict("records"),
                    selected_rows=[],
                    editable=False,
                    row_selectable="multi",
                    fixed_rows={"headers": True},
                    page_size=4,
                    page_action="native",
                    sort_action="native",
                    sort_mode="single",
                    style_header={
                        "backgroundColor": "rgb(210, 210, 210)",
                        "color": "black",
                        "fontWeight": "bold",
                        "textAlign": "left",
                        "fontFamily": "Helvetica",
                    },
                    style_table={
                        "height": "200px",
                        "maxHeight": "200px",
                        "width": "100%",
                        "maxWidth": "100%",
                        "overflowY": "scroll",
                        "overflowX": "scroll",
                    },
                    style_cell={  # refers to all cells (the whole table)
                        "textAlign": "left",
                        "padding": 7,
                        "fontFamily": "Helvetica",
                        "minWidth": 15,
                        "width": 55,
                        "maxWidth": 450,
                    },
                    style_header_conditional=[
                        {
                            "if": {"column_id": "File"},
                            # TODO: consider getting file from app_storage
                            "backgroundColor": "rgb(200, 200, 400)",
                        }
                    ],
                    style_data_conditional=[
                        {
                            "if": {"column_id": pose_data_str},
                            "textAlign": "center",
                        },
                        {
                            "if": {
                                "column_id": app_storage["config"][
                                    "metadata_key_field_str"
                                ],
                                "row_index": "odd",
                            },
                            # count starts with 0 (even) at first row with data
                            "backgroundColor": "rgb(220, 220, 420)",
                            # darker blue
                        },
                        {
                            "if": {
                                "column_id": app_storage["config"][
                                    "metadata_key_field_str"
                                ],
                                "row_index": "even",
                            },
                            "backgroundColor": "rgb(235, 235, 255)",
                            # lighter blue
                        },
                    ],
                )
            ]

        return table_container_children

    @app.callback(
        Output("slider-container", "children"),
        Input("slider-container", "children"),
        State("session-storage", "data"),
    )
    def create_time_slider(slider_container_children: list, app_storage: dict):

        # For now, a slider between events
        if not slider_container_children:
            offset = 1
            max_loc = len(app_storage["config"]["event_tags"]) + offset
            slider_container_children = dcc.RangeSlider(
                min=0,  # TODO: based on max number of frames to first event
                max=max_loc,
                # TODO: max number of frames after last event in a video?
                step=1,
                value=[offset, max_loc - offset],
                marks={
                    i
                    + offset: {
                        "label": tag,
                        "style": {
                            "color": (
                                "#055099"
                                if i
                                in [
                                    0,
                                    len(app_storage["config"]["event_tags"])
                                    - 1,
                                ]
                                else "#7BB2DD"
                            ),
                            "font-size": "16px",
                        },
                    }
                    for i, tag in enumerate(
                        app_storage["config"]["event_tags"]
                    )
                },
                allowCross=False,
                # tooltip={"placement": "top", "always_visible": True}
            )

        return slider_container_children

    @app.callback(
        Output("export-container", "children"),
        Input("export-container", "children"),
        State("session-storage", "data"),
    )
    def create_export_button_and_message(
        export_container_children, app_storage
    ):
        if not export_container_children:  # TODO: Do I need this?

            export_button = html.Button(
                children="Export selected data",  # csv? h5?
                id="export-df-button",
                n_clicks=0,
                style={"margin-right": "10px", "margin-left": "10px"},
            )

            export_message = dbc.Alert(
                children="Data export message",
                id="export-message",
                dismissable=True,
                fade=False,
                is_open=True,
                style={
                    "margin-right": "10px",
                    "margin-left": "10px",
                    "margin-top": "5px",
                },
            )

            export_container_children = html.Div(
                [
                    export_button,
                    export_message,
                ]
            )

        return export_container_children

    @app.callback(
        Output("custom-plot-container", "children"),
        Input("custom-plot-container", "children"),
        State("session-storage", "data"),
    )
    def create_custom_plots(custom_plot_container_children, app_storage):
        if not custom_plot_container_children:

            code_block = """
                import dash
                import pandas as pd
                import plotly.express as px
                from dash import dcc, html

                ######################
                # Add page to registry
                #########################
                dash.register_page(__name__)


                ##########################
                # Read dataframe for one h5 file
                # TODO: this will be part of the figs' callbacks
                h5_file_path = (
                    "sample_project/pose_estimation_results/"
                    "jwaspE_nectar-open-close_controlDLC_"
                    "resnet50_jwasp_femaleandmaleSep12shuffle1_1000000.h5"
                )
                df_trajectories = pd.read_hdf(h5_file_path.replace("\n", ""))
                df_trajectories.columns = df_trajectories.columns.droplevel()


                ########################
                # Prepare figures --- TODO: this will be updated with callbacks
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
                    # xaxis_range=[0,1300],
                    # yaxis_range=[0,1100]
                )
                fig_trajectories.update_yaxes(
                    scaleanchor="x",
                    scaleratio=1,
                )
                fig_trajectories.update_traces(marker_size=5)
            """

            custom_plot_container_children = html.Script(
                code_block,
                lang="en",
                contentEditable="true",
                # lang='Python',
                spellCheck="true",
            )

        return custom_plot_container_children
