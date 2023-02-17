import pathlib as pl

# import pdb
import re

import dash
import dash_bootstrap_components as dbc
import utils
from dash import Input, Output, State, html

VIDEO_TYPES = [".avi", ".mp4"]
# TODO: other video extensions? have this in project config file instead?


def get_callbacks(app: dash.Dash) -> None:
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
    def create_metadata_table(
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
                        children="Select all rows",
                        id="select-all-rows-button",
                        n_clicks=0,
                        style={"margin-right": "10px"},
                    ),
                    html.Button(
                        children="Unselect all rows",
                        id="unselect-all-rows-button",
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
                if str(f).endswith(".metadata.yaml"):
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
                        c["id"]: vid
                        if c["id"]
                        == app_storage["config"]["metadata_key_field_str"]
                        else ""
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
        Output("unselect-all-rows-button", "n_clicks"),
        Output("export-selected-rows-button", "n_clicks"),
        Output("alert", "is_open"),
        Output("alert", "children"),
        Input("select-all-rows-button", "n_clicks"),
        Input("unselect-all-rows-button", "n_clicks"),
        Input("export-selected-rows-button", "n_clicks"),
        Input("metadata-table", "data_previous"),
        State("metadata-table", "data"),
        State("metadata-table", "selected_rows"),
        State("session-storage", "data"),
        State("alert", "is_open"),
    )
    def modify_rows_selection(
        n_clicks_select_all: int,
        n_clicks_unselect_all: int,
        n_clicks_export: int,
        data_previous: list[dict],
        data: list[dict],
        list_selected_rows: list[int],
        app_storage: dict,
        alert_state: bool,
    ) -> tuple[list[int], int, int, int, bool, str]:
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
        # TODO: select all rows *per page*?

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
        # TODO: add if not list_selected_rows: message--no data to export
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
            list_files = [
                data[i][app_storage["config"]["metadata_key_field_str"]]
                for i in list_selected_rows
            ]
            alert_message = f"""Successfully exported
            {len(list_selected_rows)} yaml files: {list_files}"""

            # reset selected rows and nclicks
            list_selected_rows = []
            n_clicks_export = 0

        # ---------------------------
        # If 'select all' button is clicked
        if n_clicks_select_all > 0:
            list_selected_rows = list(range(len(data)))
            n_clicks_select_all = 0

        # ----------------------
        # If unselect all button is clicked
        if n_clicks_unselect_all > 0:
            list_selected_rows = []
            n_clicks_unselect_all = 0

        return (
            list_selected_rows,
            n_clicks_select_all,
            n_clicks_unselect_all,
            n_clicks_export,
            alert_state,
            alert_message,
        )
