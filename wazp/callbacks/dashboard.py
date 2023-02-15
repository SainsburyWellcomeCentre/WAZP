import pathlib as pl
import re

import utils
from dash import Input, Output, State, dash_table


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

            # # list of videos with metadata but no h5 file
            # list_videos_w_missing_pose_results = [
            #    v for v in list_videos_w_metadata
            #    if v not in list_videos_w_pose_results
            # ]
            # # TODO: use sets and (non-symmetric) differnece?

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
