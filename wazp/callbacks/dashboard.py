import datetime
import math
import os
import pathlib as pl

# import pdb
import re

import dash_bootstrap_components as dbc
import pandas as pd
import utils
import yaml
from dash import Input, Output, State, dash_table, dcc, html

POSE_DATA_STR = "Pose data available?"  # is this ok here?
TRUE_EMOJI = "✔️"
FALSE_EMOJI = "❌"


##########################
# Fns to create components
###########################


def create_video_data_table(app_storage: dict):
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
            list_videos_w_pose_results.append(re.sub("DLC.*$", "", f.stem))

    # append status of h5 file per video to table
    df_metadata[POSE_DATA_STR] = [
        TRUE_EMOJI if v in list_videos_w_pose_results else FALSE_EMOJI
        for v in list_videos_w_metadata
    ]

    # table component
    return dash_table.DataTable(
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
            # "overflowY": "scroll",
            # "overflowX": "scroll",
        },
        style_cell={  # refers to all cells (the whole table)
            "textAlign": "left",
            "padding": 7,
            "fontFamily": "Helvetica",
            # "minWidth": 15,
            # "width": 45,
            # "maxWidth": 450, #450,
        },
        style_header_conditional=[
            {
                "if": {"column_id": "File"},
                # TODO: consider getting file from app_storage
                "backgroundColor": "rgb(200, 200, 400)",
            },
            {
                "if": {"column_id": POSE_DATA_STR},
                # TODO: consider getting file from app_storage
                "textAlign": "center",
            },
        ],
        style_data_conditional=[
            {
                "if": {"column_id": POSE_DATA_STR},
                "textAlign": "center",
                "minWidth": 200,
                "width": 200,
                "maxWidth": 200,
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

    # return videos_table_component


def create_time_slider(app_storage: dict):

    # For now, a slider between events
    offset = 1  # an offset just for visualisation
    max_loc = len(app_storage["config"]["event_tags"]) + offset

    return html.Div(
        dcc.RangeSlider(
            id="time-slider",
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
                                len(app_storage["config"]["event_tags"]) - 1,
                            ]
                            else "#7BB2DD"
                        ),
                        "font-size": "16px",
                    },
                }
                for i, tag in enumerate(app_storage["config"]["event_tags"])
            },
            allowCross=False,
            # tooltip={"placement": "top", "always_visible": True}
        ),
        style={
            "margin-right": "10px",
            "margin-left": "10px",
            "margin-top": "50px",
        },
    )


def create_buttons_and_message():

    select_all_videos_button = html.Button(
        children="Select all rows",
        id="select-all-videos-button",
        n_clicks=0,
        style={
            "margin-right": "10px",
            "margin-left": "10px",
            "margin-top": "60px",
        },
    )

    unselect_all_videos_button = html.Button(
        children="Unselect all rows",
        id="unselect-all-videos-button",
        n_clicks=0,
        style={
            "margin-right": "10px",
            "margin-left": "10px",
            "margin-top": "60px",
        },
    )

    export_button = html.Button(
        children="Export selected data",  # csv? h5?
        id="export-dataframe-button",
        n_clicks=0,
        style={"margin-right": "10px", "margin-left": "10px"},
    )

    export_message = dbc.Alert(
        children="Data export message",
        id="export-message",
        dismissable=True,
        fade=False,
        is_open=False,
        color="success",  # warning or danger
        style={
            "margin-right": "10px",
            "margin-left": "10px",
            "margin-top": "5px",
        },
    )

    return html.Div(
        [
            select_all_videos_button,
            unselect_all_videos_button,
            export_button,
            export_message,
        ]
    )


def create_pose_data_unavailable_popup():

    return dcc.ConfirmDialog(
        id="pose-data-unavailable-message",
        message="",
        displayed=False,
    )


#############################
# Callbacks
###########################
def get_callbacks(app):
    """Return all callback functions for the dashboard tab.

    Parameters
    ----------
    app : dash.Dash
        Dash app object for which these callbacks are defined
    """

    @app.callback(
        Output("input-data-container", "children"),
        Input("input-data-container", "children"),
        State("session-storage", "data"),
    )
    def create_video_data_table_slider_and_buttons(
        input_data_container_children: list, app_storage: dict
    ):

        if not input_data_container_children:

            return [
                create_video_data_table(app_storage),
                create_time_slider(app_storage),
                create_buttons_and_message(),
                create_pose_data_unavailable_popup(),
            ]

    # -----------------------
    @app.callback(
        Output("video-data-table", "selected_rows"),
        Output("select-all-videos-button", "n_clicks"),
        Output("unselect-all-videos-button", "n_clicks"),
        Output("export-dataframe-button", "n_clicks"),
        Output("pose-data-unavailable-message", "message"),
        Output("pose-data-unavailable-message", "displayed"),
        Output("export-message", "children"),
        Output("export-message", "is_open"),
        Output("export-message", "color"),
        Input("video-data-table", "selected_rows"),
        Input("select-all-videos-button", "n_clicks"),
        Input("unselect-all-videos-button", "n_clicks"),
        Input("export-dataframe-button", "n_clicks"),
        State("video-data-table", "data"),
        State("time-slider", "value"),
        State("time-slider", "marks"),
        State("pose-data-unavailable-message", "message"),
        State("pose-data-unavailable-message", "displayed"),
        State("export-message", "children"),
        State("export-message", "is_open"),
        State("export-message", "color"),
        State("session-storage", "data"),
    )
    def modify_rows_selection(
        list_selected_rows: list[int],
        n_clicks_select_all: int,
        n_clicks_unselect_all: int,
        n_clicks_export: int,
        videos_table_data: list[dict],
        slider_start_end_idcs: list,
        slider_marks: dict,
        pose_unavail_message_str: str,
        pose_unavail_message_state: bool,
        export_message_str,
        export_message_state,
        export_message_color,
        app_storage: dict,
    ):
        """Modify the selection status of the rows in the videos table.

        A row's selection status (i.e., its checkbox) is modified if (1) the
        user selects a row for which there is no pose data (then its checkbox
        is set to False), (2) the export button is clicked (then the selected
        rows are reset to False), or (3) the 'select/unselect' all button is
        clicked

        Parameters
        ----------
        n_clicks_export : int
            _description_
        list_selected_rows : list[int]
            _description_
        app_storage : dict
            _description_
        export_message_state : bool
            _description_

        Returns
        -------
        _type_
            _description_
        """
        # TODO: select all rows *per page*
        list_missing_pose_data_bool = [
            videos_table_data[r][POSE_DATA_STR] == FALSE_EMOJI
            for r in range(len(videos_table_data))
        ]

        # -------------------------
        # If pose data is not available: set row to false
        if any([list_missing_pose_data_bool[r] for r in list_selected_rows]):

            # ammend list of selected rows
            list_selected_rows = [
                r
                for r in list_selected_rows
                if not list_missing_pose_data_bool[r]
            ]

            # show popup message
            pose_unavail_message_str = (
                "WARNING: Pose data unavailable "
                "for one or more selected videos"
            )
            pose_unavail_message_state = True

        # ---------------------------
        # If export button is clicked and there is data selected
        if n_clicks_export > 0:
            if not list_selected_rows:
                n_clicks_export = 0

                export_message_str = "No data to export"
                # TODO: add timestamp of message?
                export_message_color = "warning"
                export_message_state = True

            else:

                # ----
                # TODO: export selected dataframe as h5 file
                # build dataframe with subset of the data:
                # - subset of videos
                # - subset of frames per video based on time slider
                #
                # TODO: make this a fn

                # get list of h5 files from list of selected videos
                # TODO: alternative to h5: pickle? csv?
                # TODO: try to make it generic to any pose estim library?
                # (right now DLC)
                list_selected_videos = [
                    videos_table_data[r][
                        app_storage["config"]["metadata_key_field_str"]
                    ]
                    for r in list_selected_rows
                ]

                # build list of corresponding h5 files
                list_h5_file_paths = [
                    pl.Path(
                        app_storage["config"]["pose_estimation_results_path"]
                    )
                    / pl.Path(
                        pl.Path(vd).stem
                        + app_storage["config"]["pose_estimation_model_str"]
                        + ".h5"
                    )
                    for vd in list_selected_videos
                ]

                # read h5 as dataframe and add video row
                # list_df_to_export = [
                #     pd.concat(
                #         [pd.read_hdf(f)],
                #         keys=[vid],
                #         names=[
                #             app_storage["config"]["metadata_key_field_str"]
                #         ],
                #         axis=1,
                #     )  # this pd.concat adds a File level
                #     for f, vid in zip(list_h5_file_paths,
                # list_selected_videos)
                # ]

                # ------------------
                # # filter based on slider
                slider_start_end_labels = [
                    slider_marks[str(x)]["label"]
                    for x in slider_start_end_idcs
                ]
                list_df_to_export = []
                for h5, video in zip(list_h5_file_paths, list_selected_videos):

                    # read h5 as dataframe and add File row
                    df = pd.concat(
                        [pd.read_hdf(h5)],
                        keys=[video],
                        names=[
                            app_storage["config"]["metadata_key_field_str"]
                        ],
                        axis=1,
                    )

                    # get the corresponding metadata file
                    # (built from video filename)
                    yaml_filename = pl.Path(
                        app_storage["config"]["videos_dir_path"]
                    ) / pl.Path(pl.Path(video).stem + ".metadata.yaml")

                    # extract the frame numbers
                    # from the slider position
                    with open(yaml_filename, "r") as yf:
                        metadata = yaml.safe_load(yf)
                        frame_start_end = [
                            metadata["Events"][x]
                            for x in slider_start_end_labels
                        ]

                    # add event tags to dataframe
                    metadata["Events"] = dict(
                        sorted(
                            metadata["Events"].items(),
                            key=lambda item: item[1],
                        )
                    )  # ensure keys are sorted by value
                    list_keys = list(metadata["Events"].keys())
                    list_next_keys = list_keys[1:]
                    list_next_keys.append("NAN")

                    # df['event_tag'] = ''
                    # df.set_index([df.index, 'event_tag'])
                    for ky, next_ky in zip(list_keys, list_next_keys):
                        df.loc[
                            (df.index >= metadata["Events"][ky])
                            & (
                                df.index
                                < metadata["Events"].get(next_ky, math.inf)
                            ),
                            "event_tag",
                        ] = ky

                    # select subset of rows based on
                    # frame numbers from slider (both inclusive)
                    list_df_to_export.append(
                        df[
                            (df.index >= frame_start_end[0])
                            & (df.index <= frame_start_end[1])
                        ]
                    )

                    df = df.set_index([df.index, "event_tag"])
                    # pdb.set_trace()
                # ----
                # concatenate all dataframes
                # pdb.set_trace()
                df = pd.concat(list_df_to_export)
                # pdb.set_trace()

                # ----
                # Save df as h5
                # get output path
                # if not specified in config, use dir where
                # 'start_wazp_server.sh' is at
                output_path = pl.Path(
                    app_storage["config"].get(
                        "dashboard_export_data_path", "."
                    )
                )

                # if dir does not exist create it
                if not output_path.is_dir():
                    os.mkdir(output_path)

                # save as h5 file
                h5_file_path = output_path / pl.Path(
                    "df_export_"
                    + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    + ".h5"
                )
                df.to_hdf(
                    h5_file_path,
                    key="df",
                    mode="w",
                )

                # ----
                # reset
                list_selected_rows = []
                n_clicks_export = 0
                export_message_str = (
                    "Combined dataframe ",
                    f"exported successfully at: '{h5_file_path}'",
                )
                # TODO: add timestamp to message?
                export_message_color = "success"
                export_message_state = True

        # ---------------------------
        # If 'select all' button is clicked
        if n_clicks_select_all > 0:
            list_selected_rows = list(range(len(videos_table_data)))
            n_clicks_select_all = 0

        # ----------------------
        # If unselect all button is clicked
        if n_clicks_unselect_all > 0:
            list_selected_rows = []
            n_clicks_unselect_all = 0

        # # -------------------------
        # # If pose data is not available: set row to false
        # if any([list_missing_pose_data_bool[r] for r in list_selected_rows]):

        #     # ammend list of selected rows
        #     list_selected_rows = [
        #         r
        #         for r in list_selected_rows
        #         if not list_missing_pose_data_bool[r]
        #     ]

        #     # show popup message
        #     pose_unavail_message_str = (
        #         "WARNING: Pose data unavailable "
        #         "for one or more selected videos"
        #     )
        #     pose_unavail_message_state = True

        return (
            list_selected_rows,
            n_clicks_select_all,
            n_clicks_unselect_all,
            n_clicks_export,
            pose_unavail_message_str,
            pose_unavail_message_state,
            export_message_str,
            export_message_state,
            export_message_color,
        )

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

            custom_plot_container_children = dcc.Textarea(  # html.Script(
                value=code_block,
                lang="en",
                contentEditable="true",
                # lang='Python',
                spellCheck="true",
                style={"width": "50%", "height": 400},
            )

        return custom_plot_container_children

        # for df in list_df_to_export:
        #     # get video filename from df
        #     # TODO: not sure this is the best way to check?
        #     if len(df.columns.get_level_values(
        #             app_storage["config"]["metadata_key_field_str"]
        #             ).unique()) != 1:
        #         print('ERROR: dataframe contains data
        # for more than one file.')
        #         break
        #     video_filename = df.columns.get_level_values('File')[0]

        #     # get corresponding metadata file
        #     yaml_filename = pl.Path(
        #         app_storage["config"]["videos_dir_path"]
        #     ) / pl.Path(
        #             pl.Path(video_filename).stem +
        #             ".metadata.yaml"
        #     )

        #     # extract frame numbers for the tags
        #     # selected in slider
        #     with open(yaml_filename, "r") as yf:
        #         metadata = yaml.safe_load(yf)
        #         frame_start_end = [
        #             metadata['Events'][x]
        #             for x in slider_start_end_labels
        #         ]

        #     pdb.set_trace()
        #     # filter rows based on those frame numbers (both inclusive)
        #     df = df[
        #         (df.index <= frame_start_end[0]) &
        #         (df.index >= frame_start_end[1])
        #     ]
