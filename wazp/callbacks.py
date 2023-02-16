import base64
import pathlib as pl

# import pdb
import re
from typing import Any, Optional

import dash
import dash_bootstrap_components as dbc
import plotly.express as px
import utils
import yaml
from dash import Input, Output, State, dash_table, html

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
