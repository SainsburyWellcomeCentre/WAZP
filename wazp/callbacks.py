import base64
import pathlib as pl

# import pdb
import re
from typing import Any, Optional

import dash
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objs as go
import utils
import yaml
from dash import Input, Output, State, dash_table, html
from PIL import Image

VIDEO_TYPES = [".avi", ".mp4"]
# TODO: other video extensions? have this in project config file instead?
ROI_CMAP = px.colors.qualitative.Dark24
# TODO: make colomap this a project config parameter?


def get_home_callbacks(app: dash.Dash) -> None:
    """Return all callback functions for the home tab.

    Parameters
    ----------
    app : dash.Dash
        Dash app object for which these callbacks are defined
    """

    @app.callback(
        Output("session-storage", "data"),
        Output("upload-message", "is_open"),
        Output("upload-message", "children"),
        Output("upload-message", "color"),
        Input("upload-data", "contents"),
        State("upload-data", "filename"),
        State("upload-message", "is_open"),
    )
    def save_input_config_to_storage(
        up_content: str, up_filename: str, up_message_state: bool
    ) -> tuple[dict[Any, Any], bool, str, str]:
        """Save project configuration file to temporary memory storage for the current session.

        See https://community.plotly.com/t/dash-plotly-share-callback-input-in-another-page-with-dcc-store/44190/2

        Parameters
        ----------
        up_content : str
            data from the project config file upload
        up_filename : str
            name of the uploaded file (project config file)
        up_message_state : bool
            visibility of the upload message

        Returns
        -------
        data_to_store : dict
            dictionary with the following keys and values:
            - 'config': a dict with the project configuration parameters
            - 'metadata_fields': a dict with a set of attributes (description, type...)
            for each metadata field
        up_message_state : bool
            visibility of the upload message
        output_message : str
            content of the upload message
        output_color : str
            color of the upload message
        """  # noqa

        data_to_store = dict()

        # default parameters for confirmation message
        output_message = ""
        output_color = "light"
        if up_content is not None:
            _, content_str = up_content.split(",")
            try:
                if "yaml" in up_filename:
                    # get config
                    config = yaml.safe_load(base64.b64decode(content_str))

                    # get metadata fields dict
                    with open(config["metadata_fields_file_path"]) as mdf:
                        metadata_fields_dict = yaml.safe_load(mdf)

                    # bundle data
                    data_to_store = {
                        "config": config,
                        "metadata_fields": metadata_fields_dict,
                    }

                    # output message
                    if not up_message_state:
                        up_message_state = not up_message_state
                    output_message = (
                        f"Input config for:"
                        f"{config['videos_dir_path']} processed successfully."
                    )
                    output_color = "success"
                    # TODO: print path to config file instead?

            except Exception as e:
                print(e)  # TODO: check this, it prints something odd
                if not up_message_state:
                    up_message_state = not up_message_state
                output_message = (
                    "There was an error processing the config file."
                )
                output_color = "danger"

        return (data_to_store, up_message_state, output_message, output_color)


def get_metadata_callbacks(app: dash.Dash) -> None:
    """Return all callback functions for the metadata tab.


    Parameters
    ----------
    app : dash.Dash
        Dash app object for which these callbacks are defined

    """

    @app.callback(
        Output("output-metadata", "children"),
        Input("output-metadata", "children"),
        State("session-storage", "data"),
    )
    def generate_metadata_table(
        metadata_output_children: list, app_storage: dict
    ) -> html.Div:
        """Generate html component with a table holding the
        metadata per video and with auxiliary buttons for
        common table manipulations.

        The project configuration file is read from temporary
        memory storage for the current session.

        Parameters
        ----------
        metadata_output_children : list
            list of html components that will be passed to
            the metadata tab's output component
        app_storage : dict
            data held in temporary memory storage,
            accessible to all tabs in the app

        Returns
        -------
        html.Div
            html component holding the metadata dash_table and
            the auxiliary buttons for common table manipulations
        """

        if not metadata_output_children:

            metadata_table = utils.metadata_table_component_from_df(
                utils.df_from_metadata_yaml_files(
                    app_storage["config"]["videos_dir_path"],
                    app_storage["metadata_fields"],
                )
            )

            auxiliary_buttons = html.Div(
                [
                    html.Button(
                        children="Check for missing metadata files",
                        id="add-rows-for-missing-button",
                        n_clicks=0,
                        style={"margin-right": "10px"},
                    ),
                    html.Button(
                        children="Add empty row",
                        id="add-row-manually-button",
                        n_clicks=0,
                        style={"margin-right": "10px"},
                    ),
                    html.Button(
                        children="Select/unselect all rows",
                        id="select-all-rows-button",
                        n_clicks=0,
                        style={"margin-right": "10px"},
                    ),
                    html.Button(
                        children="Export selected rows as yaml",
                        id="export-selected-rows-button",
                        n_clicks=0,
                        style={"margin-right": "10px"},
                    ),
                    dbc.Alert(
                        children="",
                        id="alert",
                        dismissable=True,
                        fade=False,
                        is_open=False,
                    ),
                ]
            )

            return html.Div(
                [
                    metadata_table,
                    auxiliary_buttons,
                ]
            )

    @app.callback(
        Output("metadata-table", "data"),
        Output("add-row-manually-button", "n_clicks"),
        Output("add-rows-for-missing-button", "n_clicks"),
        Input("add-row-manually-button", "n_clicks"),
        Input("add-rows-for-missing-button", "n_clicks"),
        State("metadata-table", "data"),
        State("metadata-table", "columns"),
        State("session-storage", "data"),
    )
    def add_rows(
        n_clicks_add_row_manually: int,
        n_clicks_add_rows_missing: int,
        table_rows: list[dict],
        table_columns: list[dict],
        app_storage: dict,
    ) -> tuple[list[dict], int, int]:
        """Add rows to metadata table.

        Rows are added either manually or semiautomatically based on videos
        with missing yaml files. Both actions are triggered by clicking the
        corresponding buttons

        Parameters
        ----------
        n_clicks_add_row_manually : int
            number of clicks on the 'add row manually' button
        n_clicks_add_rows_missing : int
            number of clicks on the 'add missing rows' button
        table_rows : list[dict]
            a list of dictionaries holding the data of each row in the table
        table_columns : list[dict]
            a list of dictionaries holding the data of each column in the table
        app_storage : dict
            data held in temporary memory storage,
            accessible to all tabs in the app

        Returns
        -------
        table_rows : list[dict]
            a list of dictionaries holding the data of each row in the table

        n_clicks_add_row_manually : int
            number of clicks on the 'add row manually' button

        n_clicks_add_rows_missing : int
            number of clicks on the 'add missing rows' button
        """

        # Add empty rows manually
        if n_clicks_add_row_manually > 0 and table_columns:
            table_rows.append({c["id"]: "" for c in table_columns})
            n_clicks_add_row_manually = 0  # reset clicks

        # Add rows for videos w/ missing metadata
        if n_clicks_add_rows_missing > 0 and table_columns:
            # Read config for videos directory
            video_dir = app_storage["config"]["videos_dir_path"]

            # List of files currently shown in table
            list_files_in_table = [
                d[app_storage["config"]["metadata_key_field_str"]]
                for d in table_rows
            ]

            # List of videos w/o metadata and not in table
            list_video_files = []
            list_metadata_files = []
            for f in pl.Path(video_dir).iterdir():
                if str(f).endswith("metadata.yaml"):
                    list_metadata_files.append(
                        re.sub(".metadata$", "", f.stem)
                    )
                elif any(v in str(f) for v in VIDEO_TYPES):
                    list_video_files.append(f)  # list of PosixPaths
            list_videos_wo_metadata = [
                f.name
                for f in list_video_files
                if (f.stem not in list_metadata_files)
                and (f.name not in list_files_in_table)
            ]

            # Add a row for every video w/o metadata
            for vid in list_videos_wo_metadata:
                table_rows.append(
                    {
                        c["id"]: vid if c["id"] == "File" else ""
                        for c in table_columns
                    }
                )
                n_clicks_add_rows_missing = 0  # reset clicks

            # If the original table had only one empty row: pop it
            # (it occurs if initially there are no yaml files)
            # TODO: this is a bit hacky maybe? is there a better way?
            if list_files_in_table == [""]:
                table_rows = table_rows[1:]

        return table_rows, n_clicks_add_row_manually, n_clicks_add_rows_missing

    @app.callback(
        Output("metadata-table", "selected_rows"),
        Output("select-all-rows-button", "n_clicks"),
        Output("export-selected-rows-button", "n_clicks"),
        Output("alert", "is_open"),
        Output("alert", "children"),
        Input("select-all-rows-button", "n_clicks"),
        Input("export-selected-rows-button", "n_clicks"),
        Input("metadata-table", "data_previous"),
        State("metadata-table", "data"),
        State(
            "metadata-table", "derived_viewport_data"
        ),  # data on the current page
        State("metadata-table", "selected_rows"),
        State("session-storage", "data"),
        State("alert", "is_open"),
    )
    def modify_rows_selection(
        n_clicks_select_all: int,
        n_clicks_export: int,
        data_previous: list[dict],
        data: list[dict],
        data_page: list[dict],
        list_selected_rows: list[int],
        app_storage: dict,
        alert_state: bool,
    ) -> tuple[list[int], int, int, bool, str]:
        """Modify the selection status of the rows in the metadata table.

        A row's selection status (i.e., its checkbox) is modified if (1) the
        user edits the data on that row (then its checkbox is set to True),
        (2) the export button is clicked (then the selected rows are reset
        to False), or (3) the 'select/unselect' all button is clicked

        Parameters
        ----------
        n_clicks_select_all : int
            number of clicks on the 'select/unselect all' button
        n_clicks_export : int
            number of clicks on the 'export' button
        data_previous : list[dict]
            a list of dictionaries holding the previous state of the table
            (read-only)
        data : list[dict]
            a list of dictionaries holding the table data
        data_page : list[dict]
            a list of dictionaries holding the data of the table in
            the current page
        list_selected_rows : list[int]
            a list of indices for the currently selected rows
        app_storage : dict
            data held in temporary memory storage,
            accessible to all tabs in the app
        alert_state : bool
            visibility of the information message

        Returns
        -------
        tuple[list[int], int, int, bool, str]
            _description_
        """

        # Initialise alert message w empty
        alert_message = ""

        # If there is an edit to the row data: set checkbox to True
        if data_previous is not None:
            list_selected_rows = utils.set_edited_row_checkbox_to_true(
                data_previous,
                data,
                list_selected_rows,
            )

        # If the export button is clicked: export selected rows and unselect
        if (n_clicks_export > 0) and list_selected_rows:

            # export yaml files
            utils.export_selected_rows_as_yaml(
                data, list_selected_rows, app_storage["config"]
            )

            # display alert if successful import
            # TODO: what is a better way to check if export was successful?
            # TODO: add timestamp? remove name of files in message?
            if not alert_state:
                alert_state = not alert_state
            list_files = [data[i]["File"] for i in list_selected_rows]
            alert_message = f"""Successfully exported
            {len(list_selected_rows)} yaml files: {list_files}"""

            # reset selected rows and nclicks
            list_selected_rows = []
            n_clicks_export = 0

        # If 'select/unselect all' button is clicked
        if (
            n_clicks_select_all % 2 != 0 and n_clicks_select_all > 0
        ):  # if odd number of clicks: select all
            list_selected_rows = list(range(len(data_page)))
        elif (
            n_clicks_select_all % 2 == 0 and n_clicks_select_all > 0
        ):  # if even number of clicks: unselect all
            list_selected_rows = []

        return (
            list_selected_rows,
            n_clicks_select_all,
            n_clicks_export,
            alert_state,
            alert_message,
        )


def get_roi_callbacks(app):
    """
    Return all callback functions for the ROI tab.

    Parameters
    ----------
    app : dash.Dash
        Dash app object for which these callbacks are defined
    """

    @app.callback(
        [
            Output("video-select", "options"),
            Output("video-select", "value"),
        ],
        Input("session-storage", "data"),
    )
    def update_video_select_options(
        app_storage: dict,
    ) -> Optional[tuple[list, str]]:
        """Update the options of the video select dropdown.

        Parameters
        ----------
        app_storage : dict
            data held in temporary memory storage,
            accessible to all tabs in the app

        Returns
        -------
        list
            list of dictionaries with keys 'label' and 'value'
        str
            value of the first video in the list
        """
        if "config" in app_storage.keys():
            # Get videos directory from stored config
            config = app_storage["config"]
            videos_dir = config["videos_dir_path"]
            # get all videos in the videos directory
            video_paths = []
            for video_type in VIDEO_TYPES:
                video_paths += [
                    p for p in pl.Path(videos_dir).glob(f"*{video_type}")
                ]
            video_paths.sort()
            video_names = [p.name for p in video_paths]
            video_paths_str = [p.absolute().as_posix() for p in video_paths]
            # Video names become the labels and video paths the values
            # of the video select dropdown
            options = [
                {"label": v, "value": p}
                for v, p in zip(video_names, video_paths_str)
            ]
            value = video_paths_str[0]
            return options, value
        else:
            return dash.no_update, dash.no_update

    @app.callback(
        [
            Output("roi-select", "options"),
            Output("roi-select", "value"),
            Output("roi-colors-storage", "data"),
        ],
        Input("session-storage", "data"),
    )
    def update_roi_select_options(
        app_storage: dict,
    ) -> Optional[tuple[list[dict], str, dict]]:
        """Update the options of the ROI select dropdown.

        Parameters
        ----------
        app_storage : dict
            data held in temporary memory storage,
            accessible to all tabs in the app

        Returns
        -------
        list[dict]
            list of dictionaries with keys 'label' and 'value'
        str
            value of the first ROI in the list
        dict
            dictionary with the folowing keys:
                - roi2color: dict mapping ROI names to colors
                - color2roi: dict mapping colors to ROI names
        """
        if "config" in app_storage.keys():
            # Get ROI names from stored config
            config = app_storage["config"]
            roi_names = config["roi_names"]
            options = [{"label": r, "value": r} for r in roi_names]
            value = roi_names[0]

            # Get ROI-to-color mapping
            roi_color_mapping = utils.assign_roi_colors(
                roi_names, cmap=ROI_CMAP
            )

            return options, value, roi_color_mapping
        else:
            return dash.no_update, dash.no_update, dash.no_update

    @app.callback(
        [
            Output("frame-input", "max"),
            Output("num-frames-storage", "data"),
        ],
        Input("video-select", "value"),
        State("num-frames-storage", "data"),
    )
    def update_frame_input_max(
        video_path: str, num_frames_storage: dict
    ) -> tuple[int, dict]:
        """
        Update the maximum frame input value when a new video
        is selected. Read the value from storage if available,
        otherwise get from the video file (slower)
        and add it to storage for reuse.

        Parameters
        ----------
        video_path : str
            Path to the video file.
        num_frames_storage : dict
            Dictionary storing the number of frames for each video.

        Returns
        -------
        int
            Maximum frame input value.
        dict
            Updated dictionary storing the number of frames for each video.
        """
        video_name = pl.Path(video_path).name
        if video_path in num_frames_storage.keys():
            num_frames = num_frames_storage[video_name]
            return num_frames, dash.no_update
        else:
            num_frames = int(utils.get_num_frames(video_path))
            updated_num_frames_storage = num_frames_storage.copy()
            updated_num_frames_storage[video_name] = num_frames
        return num_frames, updated_num_frames_storage

    @app.callback(
        Output("roi-table", "data"),
        [
            Input("video-select", "value"),
            Input("frame-graph", "relayoutData"),
        ],
        [
            State("roi-table", "data"),
            State("roi-storage", "data"),
            State("roi-colors-storage", "data"),
        ],
    )
    def update_table_entries(
        video_path: str,
        graph_relayout: dict,
        roi_table: list,
        roi_storage: dict,
        roi_color_mapping: dict,
    ) -> list:
        # Get trigger for callback
        trigger = [p["prop_id"] for p in dash.callback_context.triggered][0]

        if trigger == "frame-graph.relayoutData":
            if "shapes" in graph_relayout.keys():
                # this means that a shapes has been created,
                # so, add it as a new row in the table
                roi_table = [
                    utils.shape_to_table_row(sh, roi_color_mapping)
                    for sh in graph_relayout["shapes"]
                ]
                return roi_table
            elif re.match(
                "shapes\[[0-9]+\].path", list(graph_relayout.keys())[0]
            ):
                # this means a shape was updated,
                # so, update only its corresponding row in the table
                roi_table = utils.roi_table_shape_resize(
                    roi_table, graph_relayout
                )
                return roi_table
            else:
                return dash.no_update

        else:
            # this means that a new video was selected,
            # so we load the stored shapes for that video (if any)
            roi_table = []
            video_name = pl.Path(video_path).name
            if video_name in roi_storage.keys():
                for sh in roi_storage[video_name]["shapes"]:
                    roi_table.append(
                        utils.shape_to_table_row(sh, roi_color_mapping)
                    )
            return roi_table

    @app.callback(
        Output("roi-table", "style_data_conditional"),
        Input("roi-table", "data"),
        State("roi-colors-storage", "data"),
    )
    def set_table_roi_color(roi_table: list, roi_color_mapping: dict) -> list:
        """
        Set the color of the ROI names in the ROI table
        based on the color assigned to that ROI shape.

        Parameters
        ----------
        roi_table : list
            List of dictionaries with ROI table data.
        roi_color_mapping : dict
            Dictionary with the folowing keys:
                - roi2color: dict mapping ROI names to colors
                - color2roi: dict mapping colors to ROI names

        Returns
        -------
        list[dict]
            List of dictionaries with conditional formatting
            rules for the ROI table.
        """
        if len(roi_table) == 0:
            return dash.no_update
        else:
            cond_format = []
            roi2color = roi_color_mapping["roi2color"]
            for roi in roi2color.keys():
                cond_format.append(
                    {
                        "if": {
                            "column_id": "ROI",
                            "filter_query": f"{{ROI}} = {roi}",
                        },
                        "color": roi2color[roi],
                    }
                )
            return cond_format

    # TODO: refactor this callback into smaller ones
    @app.callback(
        [
            Output("frame-graph", "figure"),
            Output("frame-status-alert", "children"),
            Output("frame-status-alert", "color"),
            Output("frame-status-alert", "is_open"),
            Output("roi-storage", "data"),
        ],
        [
            Input("roi-table", "data"),
            Input("video-select", "value"),
            Input("frame-input", "value"),
            Input("roi-select", "value"),
        ],
        [
            State("roi-storage", "data"),
            State("roi-colors-storage", "data"),
        ],
    )
    def update_frame_graph(
        roi_table,
        video_path,
        frame_idx,
        roi_value,
        roi_storage,
        roi_color_mapping,
    ) -> tuple[go.Figure, str, str, bool, dict]:
        # Get info from stored config
        video_path = pl.Path(video_path)
        video_name = video_path.name

        # Cache frames in a .WAZP folder in the home directory
        frames_dir = pl.Path.home() / ".WAZP" / "roi_frames"
        frames_dir.mkdir(parents=True, exist_ok=True)
        frame_path = frames_dir / f"{video_path.stem}_frame-{frame_idx}.png"

        # Get trigger for callback
        trigger = [p["prop_id"] for p in dash.callback_context.triggered][0]

        # Status display under the frame graph
        alert_msg = f"Defining ROIs on frame {frame_idx} from {video_name}"
        alert_color = "light"
        alert_is_open = True

        # When a new video or frame is selected
        # Extract roi frame if it doesn't exist
        if (trigger == "video-select.value") or (
            trigger == "frame-input.value"
        ):
            if frame_idx is None:
                alert_msg = "Please select a valid frame number"
                alert_color = "warning"
                alert_is_open = True
                return (
                    dash.no_update,
                    alert_msg,
                    alert_color,
                    alert_is_open,
                    dash.no_update,
                )

            if frame_path.exists():
                alert_msg = (
                    f"Showing cached frame {frame_idx} from {video_name}"
                )
                alert_color = "success"
                alert_is_open = True
            else:
                print(f"Extracting frame {frame_idx} for {video_name}")
                try:
                    utils.extract_frame(
                        video_path.as_posix(), frame_idx, frame_path.as_posix()
                    )
                    alert_msg = (
                        f"Extracted frame {frame_idx} from {video_name}"
                    )
                    alert_color = "success"
                    alert_is_open = True
                except Exception as e:
                    print(e)
                    alert_msg = (
                        f"Failed to extract frame "
                        f"{frame_idx} from {video_name}"
                    )
                    alert_color = "danger"
                    alert_is_open = True
                    return (
                        dash.no_update,
                        alert_msg,
                        alert_color,
                        alert_is_open,
                        dash.no_update,
                    )

        # Convert table rows to shapes
        table_shapes = [
            utils.table_row_to_shape(sh, roi_color_mapping) for sh in roi_table
        ]

        # Update ROI store with new video name if it doesn't exist
        if video_name not in roi_storage.keys():
            roi_storage[video_name] = {"shapes": []}
        # Find which of the stored shapes are new
        stored_shapes = roi_storage[video_name]["shapes"]
        new_shapes_i, old_shapes_i = [], []
        for i, shape in enumerate(table_shapes):
            if utils.shape_in_list(stored_shapes)(shape):
                old_shapes_i.append(i)
            else:
                new_shapes_i.append(i)
        # Add timestamps to the new shapes
        for i in new_shapes_i:
            table_shapes[i]["timestamp"] = utils.time_passed(
                roi_storage["start_time"]
            )
        # Copy previous timestamps to the old shapes
        for i in old_shapes_i:
            old_i = utils.index_of_shape(stored_shapes, table_shapes[i])
            table_shapes[i]["timestamp"] = stored_shapes[old_i]["timestamp"]
        # Update roi store
        roi_storage[video_name]["shapes"] = table_shapes
        # load extracted frame
        new_frame = Image.open(frame_path)
        new_fig = px.imshow(new_frame)
        new_fig.update_layout(
            shapes=[
                utils.shape_data_remove_timestamp(sh) for sh in table_shapes
            ],
            newshape_line_color=roi_color_mapping["roi2color"][roi_value],
            dragmode="drawclosedpath",
            margin=dict(l=0, r=0, t=0, b=0),
            yaxis={"visible": False, "showticklabels": False},
            xaxis={"visible": False, "showticklabels": False},
        )

        return new_fig, alert_msg, alert_color, alert_is_open, roi_storage


def get_dashboard_callbacks(app):
    """Return all callback functions for the dashboard tab.

    Parameters
    ----------
    app : dash.Dash
        Dash app object for which these callbacks are defined
    """

    @app.callback(
        Output("table-container", "children"),
        Input("table-container", "children"),
        State("session-storage", "data"),
    )
    def create_input_data_table(
        table_container_children: list,
        app_storage: dict,
    ):
        """Create table to select videos to include in plots.

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

            # videos list as df
            df_metadata = utils.df_from_metadata_yaml_files(
                app_storage["config"]["videos_dir_path"],
                app_storage["metadata_fields"],
            )
            df_metadata = df_metadata[
                [app_storage["config"]["metadata_key_field_str"]]
            ]

            # table component
            table_container_children = [
                dash_table.DataTable(
                    id="input-data-table",
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
            ]
        return table_container_children
