import datetime
import pathlib as pl
import re

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from dash import Input, Output, State, dash_table, dcc, html

from wazp import utils

# from flask_caching import Cache
# from dash.exceptions import PreventUpdate
# import copy

POSE_DATA_STR = "Pose data available?"
TRUE_EMOJI = "✔️"
FALSE_EMOJI = "❌"


################################
# Functions to create components
################################
# TODO: this could be in a layout/custom_components module?
def create_video_data_table(app_storage: dict) -> dash_table.DataTable:
    """Create table to select videos to include in exports and
    in plots.

    Only videos with a matching YAML file are shown.
    The availability of pose estimation data is also shown.


    Parameters
    ----------
    app_storage : dict
        data held in temporary memory storage,
        accessible to all tabs in the app

    Returns
    -------
    dash_table.DataTable
        dash DataTable component to pass to the table container
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
    # TODO for refactoring: have this in utils?
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
    # TODO for refactoring: factor out css style?
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
        },
        style_cell={  # refers to all cells (the whole table)
            "textAlign": "left",
            "padding": 7,
            "fontFamily": "Helvetica",
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


def create_time_slider(app_storage: dict) -> html.Div:
    """Create a time slider component

    The time slider is a dash RangeSlider component
    that allows to define the two sides of an interval

    Parameters
    ----------
    app_storage : dict
        data held in temporary memory storage,
        accessible to all tabs in the app

    Returns
    -------
    html.Div
        html Div component wrapping the slider component
    """
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
        ),
        style={
            "margin-right": "10px",
            "margin-left": "10px",
            "margin-top": "50px",
        },
    )


def create_buttons_and_message() -> html.Div:
    """Create buttons and messages related to
    selecting/unselecting videos in the table
    and for exporting the data.

    Returns
    -------
    html.Div
        html Div component wrapping the buttons
        and messages
    """
    buttons_css_style = {
        "margin-right": "0px",
        "margin-left": "10px",
        "margin-top": "60px",
    }

    select_all_videos_button = html.Button(
        children="Select all rows",
        id="select-all-videos-button",
        n_clicks=0,
        style=buttons_css_style,
    )

    unselect_all_videos_button = html.Button(
        children="Unselect all rows",
        id="unselect-all-videos-button",
        n_clicks=0,
        style=buttons_css_style,
    )

    export_button = html.Button(
        children="Export selected data",  # csv? h5?
        id="export-dataframe-button",
        n_clicks=0,
        style=buttons_css_style,
    )

    clipboard = dcc.Clipboard(
        id="clipboard",
        title="Copy full path",  # tooltip text
        n_clicks=0,
        style={
            "display": "inline",  # visible
            "fontSize": 20,
            "margin-right": "10px",
            "margin-left": "10px",
        },
    )

    clipboard_wrapper = html.Div(
        id="clipboard-wrapper",
        children=[
            clipboard,
        ],
        style={"display": "inline-block"},  # hidden
    )

    export_message = html.Div(
        [
            html.Br(),
            dbc.Alert(
                children=["", clipboard_wrapper],
                id="export-message",
                dismissable=True,
                fade=False,
                is_open=False,
                color="success",  # warning or danger
                style={
                    "margin-right": "0px",
                    "margin-left": "10px",
                    "margin-top": "5px",
                },
            ),
        ],
        style={"display": "float"},  # hidden
    )

    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(select_all_videos_button, width="auto"),
                    dbc.Col(unselect_all_videos_button, width="auto"),
                    dbc.Col(export_button, width="auto"),
                ],
                align="start",
                justify="start",
            ),
            dbc.Row(export_message),
        ]
    )


def create_pose_data_unavailable_popup() -> dcc.ConfirmDialog:
    """Create pop-up message when pose data is
    unavailable for a selected video.

    A message will pop up when a video in the table
    is selected but has no pose data available.

    Returns
    -------
    dcc.ConfirmDialog
        A confirm dialog component
    """

    return dcc.ConfirmDialog(
        id="pose-data-unavailable-message",
        message="",
        displayed=False,
    )


def create_tabs():
    """Create header with tabs

    Returns
    -------
    _type_
        _description_
    """
    return dbc.Tabs(
        [
            dbc.Tab(
                label="Trajectories",
                tab_id="trajectories-tab",
                children=[],
                style={"margin-top": "0px", "margin-bottom": "0px"},
            ),
            dbc.Tab(
                label="Heatmaps",
                tab_id="heatmaps-tab",
                children=[],
                style={"margin-top": "0px", "margin-bottom": "0px"},
            ),
            dbc.Tab(
                label="ROIs barplots",
                tab_id="rois-tab",
                disabled=True,
                style={"margin-top": "0px", "margin-bottom": "0px"},
            ),
        ],
        id="tabs",
        active_tab="trajectories-tab",
        style={"margin-top": "0px", "margin-bottom": "0px"},
    )


def create_tabs_content():
    """Create container for tabs content

    Returns
    -------
    _type_
        _description_
    """
    return html.Div(
        id="tabs-content",
        style={"margin-top": "0px", "margin-bottom": "0px"},
    )


def create_trajectories_tab_content():
    """Create content to display when trajectories tab is selected

    Returns
    -------
    _type_
        _description_
    """
    return html.Div(
        id="trajectories-tabs-content",
        children=[
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Loading(dcc.Graph(id="trajectories-plot")),
                        style={"margin-top": "0px", "margin-bottom": "0px"},
                    ),
                    dbc.Col(
                        [
                            html.P("Color by:"),
                            dcc.Dropdown(
                                id="color-dropdown",
                                options=[
                                    "model_str",
                                    "video_file",
                                    #  'individual', # TODO: fix if individual
                                    # not present!
                                    "frame",
                                    "bodypart",
                                    "likelihood",
                                    "ROI_tag",
                                    "event_tag",
                                ],
                                value="video_file",
                            ),
                            html.Br(),
                            html.P("DLC p-cutoff:"),
                            dcc.Slider(
                                id="pcutoff-slider",
                                value=0.95,
                                min=0.0,
                                max=1.0,
                                step=0.05,
                                marks={i / 10: f"{i/10}" for i in range(11)},
                                # TODO: why start/end marks not showing?
                                tooltip={
                                    "placement": "top",
                                    "always_visible": True,
                                },
                            ),
                        ],
                        style={
                            "margin-top": "35px",
                        },
                    ),
                ],
            )
        ],
        style={"margin-top": "0px"},
    )


def create_heatmaps_tab_content():
    """Create content to display when heatmaps tab is selected

    Returns
    -------
    _type_
        _description_
    """
    return (dcc.Graph(id="heatmap-plot"),)


#############################
# Callbacks
###########################
def get_callbacks(app: dash.Dash) -> None:
    """Return all callback functions for the dashboard tab.

    Parameters
    ----------
    app : dash.Dash
        Dash app object for which these callbacks are defined
    """

    @app.callback(
        Output("export-data-container", "children"),
        Input("export-data-container", "children"),
        State("session-storage", "data"),
    )
    def create_export_components(
        input_data_container_children: list, app_storage: dict
    ) -> list:
        """Create components for the main data container
        in the dashboard tab layout

        Returns a list with the following components:
        - video data table
        - time slider for event tags
        - buttons and messages for (un)selecting and exporting
          data
        - popup message for when pose data is unavailable for
          a selected video

        Parameters
        ----------
        input_data_container_children : list
            children of the input data container
        app_storage : dict
            data held in temporary memory storage,
            accessible to all tabs in the app

        Returns
        -------
        list
            components to pass as children of the main data container
            in the dashboard tab layout
        """

        if not input_data_container_children:
            input_data_container_children = [
                dbc.Row(create_video_data_table(app_storage)),
                dbc.Row(create_time_slider(app_storage)),
                dbc.Row(create_buttons_and_message()),
                create_pose_data_unavailable_popup(),
                # create_dashboard_storage(),
            ]
        return input_data_container_children

    @app.callback(
        Output("plots-container", "children"),
        Input("plots-container", "children"),
    )
    def create_plot_components(
        plot_container_children: list,
    ) -> list:
        """Create components for the main data container
        in the dashboard tab layout

        Returns a list with the following components:
        - video data table
        - time slider for event tags
        - buttons and messages for (un)selecting and exporting
          data
        - popup message for when pose data is unavailable for
          a selected video

        Parameters
        ----------
        input_data_container_children : list
            children of the input data container
        app_storage : dict
            data held in temporary memory storage,
            accessible to all tabs in the app

        Returns
        -------
        list
            components to pass as children of the main data container
            in the dashboard tab layout
        """

        if not plot_container_children:
            plot_container_children = [
                create_tabs(),
                create_tabs_content(),
            ]
        return plot_container_children

    @app.callback(
        Output("tabs-content", "children"), Input("tabs", "active_tab")
    )
    def update_tab_content(tab_id):
        """Update content based on selected tab

        Parameters
        ----------
        tab_id : string
            ID of the selected tab

        Returns
        -------
        _type_
            a single or list of html / dbc components
        """
        if tab_id == "trajectories-tab":
            return create_trajectories_tab_content()
        elif tab_id == "heatmaps-tab":
            return create_heatmaps_tab_content()
        return html.P("Select a tab to display the data")

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
        # Input("dashboard-storage", "data"), #dashboard storage changes
        # if selected rows or timeline changes!
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
        export_message_children: list,
        export_message_state: bool,
        export_message_color,
        app_storage: dict,
    ):  # -> tuple[list, int, int, int, str, bool, list, bool, str]:
        """Modify the selection status of the rows in the videos' table.

        A row's selection status (i.e., its checkbox) is modified if:
        (1) the 'select/unselect' all button is clicked,
        (2) the user selects a row whose video has no pose data
            available. In that case, its checkbox is set to False,
        (3) the export button is clicked. In that case the selected rows
            are reset to False.


        Parameters
        ----------
        list_selected_rows : list[int]
            a list of indices for the currently selected rows
        n_clicks_select_all : int
            number of clicks on the 'select all' button
        n_clicks_unselect_all : int
            number of clicks on the 'unselect all' button
        n_clicks_export : int
            number of clicks on the 'export' button
        videos_table_data : list[dict]
            a list of dictionaries holding the data of each
            row in the videos table
        slider_start_end_idcs : list
            indices for the start and end position of the slider
        slider_marks : dict
            dictionary holding the data of each of the slider marks
        pose_unavail_message_str : str
            text content of the 'pose data unavailable' message
        pose_unavail_message_state : bool
            visibility state of the 'pose data unavailable' message
        export_message_children : list
            children of the export message component
        export_message_state : bool
            visibility state of the export message
        export_message_color : str
            color of the export message
        app_storage : dict
            data held in temporary memory storage,
            accessible to all tabs in the app

        Returns
        -------
        list_selected_rows : list
            a list of indices for the currently selected rows
        n_clicks_select_all : int
            number of clicks on the 'select all' button
        n_clicks_unselect_all : int
             number of clicks on the 'unselect all' button
        n_clicks_export : int
            number of clicks on the 'export' button
        pose_unavail_message_str : str
            text content of the 'pose data unavailable' message
        pose_unavail_message_state : bool
            visibility state of the 'pose data unavailable' message
        export_message_children : list
            children of the export message component
        export_message_state : bool
            visibility state of the export message
        export_message_color : str
            color of the export message
        """

        list_missing_pose_data_bool = [
            videos_table_data[r][POSE_DATA_STR] == FALSE_EMOJI
            for r in range(len(videos_table_data))
        ]

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
        # If export button is clicked
        if n_clicks_export > 0:
            # if no rows are selected show warning
            if not list_selected_rows:
                n_clicks_export = 0

                export_message_children[0] = "No data to export"
                export_message_children[1]["props"]["style"] = {
                    "display": "none"
                }
                export_message_color = "warning"
                export_message_state = True

            # if rows are selected: export combined dataframe
            else:

                # get list of selected videos
                list_selected_videos = [
                    videos_table_data[r][
                        app_storage["config"]["metadata_key_field_str"]
                    ]
                    for r in list_selected_rows
                ]

                # get slider labels
                slider_start_end_labels = [
                    slider_marks[str(x)]["label"]
                    for x in slider_start_end_idcs
                ]

                # get list of dataframes to combine
                # - one dataframe per selected video
                # - we add the fields 'video_file', 'event_tag' and 'ROI'
                # - we select only the frames within the interval
                #   set by the slider
                list_df_to_export = utils.get_dataframes_to_combine(
                    list_selected_videos,
                    slider_start_end_labels,
                    app_storage,
                )

                # concatenate all dataframes
                # NOTE: we explicitly initialise ROI_tags
                # and event_tags columns for all video dataframes
                # with empty strings (then ROIs and events are only assigned
                # if defined for a video)
                # TODO: check if it exists in cache for figure?
                df = pd.concat(list_df_to_export)

                # ---------
                # Export dataframe as h5
                # TODO: provide an option to export as h5 or csv?

                # Get path to output directory
                # if not specified in config, use dir where
                # server was launched from
                output_path = pl.Path(
                    app_storage["config"].get(
                        "dashboard_export_data_path", "."
                    )
                )

                # If output directory does not exist,
                # create it
                output_path.mkdir(parents=True, exist_ok=True)

                # Save combined dataframe as h5 file
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

                # ---------
                # Reset triggers and states
                list_selected_rows = []
                n_clicks_export = 0
                export_message_children[0] = "".join(
                    (
                        "Combined dataframe ",
                        f"exported successfully at: '{h5_file_path}'",
                    )
                )  # this is because max line length in linter
                export_message_children[1]["props"]["style"] = {
                    "display": "inline-block"
                }
                export_message_color = "success"
                export_message_state = True

        return (
            list_selected_rows,
            n_clicks_select_all,
            n_clicks_unselect_all,
            n_clicks_export,
            pose_unavail_message_str,
            pose_unavail_message_state,
            export_message_children,
            export_message_state,
            export_message_color,
        )

    @app.callback(
        Output("clipboard", "content"),
        Output("clipboard", "n_clicks"),
        Input("clipboard", "n_clicks"),
        State("export-message", "children"),
        State("clipboard", "content"),
    )
    def copy_path_from_export_message(
        n_clicks_clipboard: int,
        export_message_children: list,
        clipboard_content: str,
    ) -> tuple[str, int]:
        """Copy fullpath from export message
        to clipboard

        Parameters
        ----------
        n_clicks_clipboard : int
            number of clicks on the clipboard icon
        export_message_children : list
            children of the export message component
        clipboard_content : str
            text content in the clipboard

        Returns
        -------
        clipboard_content : str
            text content in the clipboard
        n_clicks_clipboard : int
            number of clicks on the clipboard icon
        """

        if n_clicks_clipboard > 0:
            # extract strings between single quotes (first match)
            # TODO: is single quotes requirement limiting?
            relative_path = re.findall(
                r"\'([^]]*)\'", export_message_children[0]
            )[0]
            clipboard_content = str(pl.Path(relative_path).resolve())
            n_clicks_clipboard = 0

        return (clipboard_content, n_clicks_clipboard)

    @app.callback(
        Output("trajectories-plot", "figure"),
        Input("video-data-table", "selected_rows"),
        Input("time-slider", "value"),
        State(
            "color-dropdown", "value"
        ),  # TODO: fix, why not Input? (gives odd errors)
        State("video-data-table", "data"),
        State("time-slider", "marks"),
        State("session-storage", "data"),
    )
    def update_trajectory_plot(
        list_selected_rows: list[int],
        slider_start_end_idcs: list,
        color_by_str: str,
        videos_table_data: list[dict],
        slider_marks: dict,
        app_storage: dict,
    ):
        # initialise figure's layout
        fig_layout = {
            "margin": {"l": 20, "b": 20, "t": 40, "r": 20},
            "legend": {
                "orientation": "v",
                "yanchor": "top",
                "y": 1.00,
                "xanchor": "left",
                "x": 0.01,
            },
            "xaxis": {
                "anchor": "y",
                "title": {"text": "x (pixels)"},
                # "range": [0, 1500],
            },
            "yaxis": {
                "anchor": "x",
                "title": {"text": "y (pixels)"},
                "scaleanchor": "x",
                "scaleratio": 1,
            },
        }

        # trigger = dash.callback_context.triggered[0]["prop_id"]

        # fill figure with data
        if list_selected_rows:

            # ammend list of selected rows
            list_missing_pose_data_bool = [
                videos_table_data[r][POSE_DATA_STR] == FALSE_EMOJI
                for r in range(len(videos_table_data))
            ]
            list_selected_rows = [
                r
                for r in list_selected_rows
                if not list_missing_pose_data_bool[r]
            ]

            # get list of selected videos
            list_selected_videos = [
                videos_table_data[r][
                    app_storage["config"]["metadata_key_field_str"]
                ]
                for r in list_selected_rows
            ]

            # get slider labels
            slider_start_end_labels = [
                slider_marks[str(x)]["label"] for x in slider_start_end_idcs
            ]

            # get list of dataframes to combine
            # - one dataframe per selected video
            # - we add the fields 'video_file', 'event_tag' and 'ROI'
            # - we select only the frames within the interval
            #   set by the slider
            list_df_to_export = utils.get_dataframes_to_combine(
                list_selected_videos,
                slider_start_end_labels,
                app_storage,
            )

            # concatenate all dataframes
            # NOTE: we explicitly initialise ROI_tags
            # and event_tags columns for all video dataframes
            # with empty strings (then ROIs and events are only assigned
            # if defined for a video)
            # TODO: check if it exists in cache for figure?
            df = pd.concat(list_df_to_export)

            # plot
            # | 'model_str' | 'video_file' | 'individual'* | 'frame'
            # | 'bodypart' | 'x' | 'y' | 'likelihood' | 'ROI_tag'
            # | 'event_tag' |
            fig = px.scatter(
                df,
                x="x",
                y="y",
                color=color_by_str,
            )
            fig.update_layout(fig_layout)
            return fig

        # if no data selected: return empty figure
        else:
            # TODO: set xlim, ylim from image size
            fig_layout["xaxis"].update({"range": [0, 1500]})  # type: ignore
            fig_layout["yaxis"].update({"range": [0, 1500]})  # type: ignore
            fig_layout.update({"width": 800, "height": 800})

            return go.Figure(
                data=[],
                layout=fig_layout,
            )
