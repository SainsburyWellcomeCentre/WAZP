import pathlib as pl
import re

import dash_bootstrap_components as dbc
import utils
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
                "if": {"column_id": POSE_DATA_STR},
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

    # return videos_table_component


def create_time_slider(app_storage: dict):

    # For now, a slider between events
    offset = 1  # an offset just for visualisation
    max_loc = len(app_storage["config"]["event_tags"]) + offset

    return dcc.RangeSlider(
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
    )


def create_buttons_and_message():

    select_all_rows_button = html.Button(
        children="Select/unselect all rows",
        id="select-all-videos-button",
        n_clicks=None,
        style={"margin-right": "10px", "margin-left": "10px"},
    )

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

    return html.Div(
        [
            select_all_rows_button,
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
    def create_video_data_table_slider_and_export(
        input_data_container_children: list, app_storage: dict
    ):

        if not input_data_container_children:

            return [
                create_video_data_table(app_storage),
                create_time_slider(app_storage),
                create_buttons_and_message(),
                create_pose_data_unavailable_popup(),
            ]

    @app.callback(
        Output("video-data-table", "selected_rows"),
        Output("pose-data-unavailable-message", "message"),
        Output("pose-data-unavailable-message", "displayed"),
        # Output("export-df-button", "n_clicks"),
        # Output("export-message", "is_open"),
        # Output("export-message", "children"),
        Input("video-data-table", "selected_rows"),
        Input("select-all-videos-button", "n_clicks"),
        State("video-data-table", "data"),
        # State(
        #     "video-data-table", "derived_viewport_data"
        # ),
        State("pose-data-unavailable-message", "message"),
        State("pose-data-unavailable-message", "displayed"),
    )
    def modify_rows_selection(
        list_selected_rows: list[int],
        n_clicks_select_all: int,
        videos_table_data: list[dict],
        pose_unavail_message_str: str,
        pose_unavail_message_state: bool,
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

        # export_message = ''
        # If the export button is clicked:
        # # export selected rows and unselect all
        # # if (n_clicks_export > 0) and list_selected_rows:
        # if list_selected_rows and (n_clicks_select_all > 0):
        # and list_selected_rows:
        #     print('PATATA')

        # If pose data is not available: set to false
        if (
            videos_table_data and list_selected_rows
        ):  # and n_clicks_select_all:

            print(n_clicks_select_all)

            # ### If 'select/unselect all' button is clicked
            # if (
            #     n_clicks_select_all % 2 != 0 and n_clicks_select_all > 0
            # ):  # if odd number of clicks: select all
            #     list_selected_rows = list(range(len(videos_table_data)))
            # elif (
            #     n_clicks_select_all % 2 == 0 and n_clicks_select_all > 0
            # ):  # if even number of clicks: unselect all
            #     list_selected_rows = []

            # Check rows with missing pose data within those selected
            list_missing_pose_data_bool = [
                videos_table_data[r][POSE_DATA_STR] == FALSE_EMOJI
                for r in list_selected_rows
            ]

            # If pose data is not available: set to false
            if any(list_missing_pose_data_bool):
                # ammend list of selected rows
                list_selected_rows = [
                    r
                    for r in list_selected_rows
                    if videos_table_data[r][POSE_DATA_STR] == TRUE_EMOJI
                ]

                # show popup message
                pose_unavail_message_str = (
                    "WARNING: Pose data unavailable for the selected video"
                )
                pose_unavail_message_state = True

        return (
            list_selected_rows,
            # n_clicks_select_all,
            pose_unavail_message_str,
            pose_unavail_message_state,
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
