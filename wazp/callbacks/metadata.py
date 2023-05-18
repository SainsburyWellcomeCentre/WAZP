import base64
import io
import pathlib as pl
import re

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import yaml
from dash import Input, Output, State, dash_table, dcc, html

from wazp import utils

# TODO: other video extensions? have this in project config file instead?
VIDEO_TYPES = [".avi", ".mp4"]


##########################
# Fns to create components
###########################
def create_metadata_table_component_from_df(
    df: pd.DataFrame,
    config: dict,
) -> dash_table.DataTable:
    """Build a Dash table component populated with the input dataframe.

    Parameters
    ----------
    df : pd.DataFrame
        input dataframe

    Returns
    -------
    dash_table.DataTable
        dash table component built from input dataframe

    """

    # Change format of columns with string 'date' in their name from string to
    # datetime
    # (this is to allow sorting in the Dash table)
    # TODO: review this, is there a more failsafe way?
    list_date_columns = [
        col for col in df.columns.tolist() if "date" in col.lower()
    ]
    for col in list_date_columns:
        df[col] = pd.to_datetime(df[col]).dt.strftime("%Y-%m-%d")

    # dash table component
    table = dash_table.DataTable(
        id="metadata-table",
        data=df.to_dict("records"),
        data_previous=None,
        selected_rows=[],
        columns=[
            {
                "id": c,
                "name": c,
                "hideable": (
                    True if c != config["metadata_key_field_str"] else False
                ),
                "editable": (
                    True
                    if c
                    not in [
                        # config["metadata_key_field_str"],
                        # TODO: make Filename not editable?
                        # (if so, then 'Add empty row' doesnt make sense)
                        "Events",  # TODO: can we not hardcode this?
                        "ROIs",  # TODO: can we not hardcode this?
                    ]
                    else False
                ),
                "presentation": "input",
            }
            for c in df.columns
        ],
        css=[
            {
                "selector": ".dash-spreadsheet td div",
                "rule": """
                    max-height: 20px; min-height: 20px; height: 20px;
                    line-height: 15px;
                    display: block;
                    overflow-y: hidden;
                    """,
            }
        ],  # to fix issue of different cell heights if row is empty;
        # see https://dash.plotly.com/datatable/width#wrapping-onto-multiple-lines-while-constraining-the-height-of-cells # noqa
        row_selectable="multi",
        page_size=25,
        page_action="native",
        fixed_rows={"headers": True},
        # fix header when scrolling vertically
        fixed_columns={"headers": True, "data": 1},
        # fix first column when scrolling laterally
        sort_action="native",
        sort_mode="single",
        tooltip_header={i: {"value": i} for i in df.columns},
        tooltip_data=[
            {
                row_key: {"value": str(row_val), "type": "markdown"}
                for row_key, row_val in row_dict.items()
            }
            for row_dict in df.to_dict("records")
        ],
        style_header={
            "backgroundColor": "rgb(210, 210, 210)",
            "color": "black",
            "fontWeight": "bold",
            "textAlign": "left",
            "fontFamily": "Helvetica",
        },
        style_table={
            "height": "720px",
            "maxHeight": "720px",
            # css overwrites the table height when fixed_rows is enabled;
            # setting height and maxHeight to the same value seems a quick
            # hack to fix it
            # (see https://community.plotly.com/t/setting-datatable-max-height-when-using-fixed-headers/26417/10) # noqa
            "width": "100%",
            "maxWidth": "100%",
            "overflowY": "scroll",
            "overflowX": "scroll",
        },
        style_cell={  # refers to all cells (the whole table)
            "textAlign": "left",
            "padding": 7,
            "minWidth": 70,
            "width": 175,
            "maxWidth": 450,
            "fontFamily": "Helvetica",
        },
        style_data={  # refers to data cells (all except header and filter)
            "color": "black",
            "backgroundColor": "white",
            "overflow": "hidden",
            "textOverflow": "ellipsis",
        },
        style_header_conditional=[
            {
                "if": {"column_id": config["metadata_key_field_str"]},
                # TODO: consider getting file from app_storage
                "backgroundColor": "rgb(200, 200, 400)",
            }
        ],
        style_data_conditional=[
            {
                "if": {
                    "column_id": [config["metadata_key_field_str"]],
                    "row_index": "odd",
                },
                "backgroundColor": "rgb(220, 220, 420)",  # darker blue
            },
            {
                "if": {
                    "column_id": [config["metadata_key_field_str"]],
                    "row_index": "even",
                },
                "backgroundColor": "rgb(235, 235, 255)",  # lighter blue
            },
            {
                "if": {
                    "column_id": [
                        c
                        for c in df.columns
                        if c not in [config["metadata_key_field_str"]]
                    ],
                    "row_index": "odd",
                },
                "backgroundColor": "rgb(240, 240, 240)",  # gray
            },
            {
                "if": {
                    "column_id": [
                        "ROIs",
                        "Events",
                    ],  # TODO can we not hardcode this?
                    "row_index": "odd",
                },
                "backgroundColor": "rgb(180, 180, 180)",
                # to highlight not editable
            },
            {
                "if": {
                    "column_id": [
                        "ROIs",
                        "Events",
                    ],  # TODO can we not hardcode this?
                    "row_index": "even",
                },
                "backgroundColor": "rgb(190, 190, 190)",
                # to highlight not editable
            },
        ],
    )

    return table


#############################
# Callbacks
###########################
def get_callbacks(app: dash.Dash) -> None:
    """Return all callback functions for the metadata tab.


    Parameters
    ----------
    app : dash.Dash
        Dash app object for which these callbacks are defined

    """

    @app.callback(
        Output("metadata-container", "children"),
        Input("metadata-container", "children"),
        State("session-storage", "data"),
    )
    def create_metadata_table_and_buttons(
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

            metadata_table = create_metadata_table_component_from_df(
                utils.df_from_metadata_yaml_files(
                    app_storage["config"]["videos_dir_path"],
                    app_storage["metadata_fields"],
                ),
                app_storage["config"],
            )

            # TODO: define style of all buttons separately?
            button_style = {
                "outline": False,
                "color": "light",
                "class_name": "w-100",
            }
            auxiliary_buttons_row = dbc.Row(
                [
                    dbc.Col(
                        dbc.Button(
                            children="Check for missing metadata files",
                            id="add-rows-for-missing-button",
                            n_clicks=0,
                            **button_style,
                        ),
                        width="auto",
                    ),
                    dbc.Col(
                        dbc.Button(
                            children="Add empty row",
                            id="add-row-manually-button",
                            n_clicks=0,
                            **button_style,  # {"margin-right": "10px"},
                        ),
                        width="auto",
                    ),
                    dbc.Col(
                        dbc.Button(
                            children="Select all rows",
                            id="select-all-rows-button",
                            n_clicks=0,
                            **button_style,  # {"margin-right": "10px"},
                        ),
                        width="auto",
                    ),
                    dbc.Col(
                        dbc.Button(
                            children="Unselect all rows",
                            id="unselect-all-rows-button",
                            n_clicks=0,
                            **button_style,  # {"margin-right": "10px"},
                        ),
                        width="auto",
                    ),
                    dbc.Col(
                        dbc.Button(
                            children="Export selected rows as yaml",
                            id="export-selected-rows-button",
                            n_clicks=0,
                            **button_style,  # {"margin-right": "10px"},
                        ),
                        width="auto",
                    ),
                    dbc.Col(
                        dcc.Upload(
                            id="upload-spreadsheet",
                            children=dbc.Button(
                                children=(
                                    "Generate yaml files from spreadsheet"
                                ),
                                id="generate-yaml-files-button",
                                n_clicks=0,
                                **button_style,  # {"margin-right": "10px"},
                            ),
                            contents=None,
                            multiple=False,
                        ),
                        width="auto",
                    ),
                ],
                justify="start",
            )

            alert_message_row = dbc.Row(
                dbc.Alert(
                    children="",
                    id="alert",
                    dismissable=True,
                    fade=False,
                    is_open=False,
                ),
            )

            import_message_row = dbc.Row(
                dbc.Alert(
                    children="",
                    id="import-message",
                    dismissable=True,
                    fade=False,
                    is_open=False,
                ),
            )

            # check for missing metadata files
            check_missing_files_tooltip = dbc.Tooltip(
                "Check which videos in the "
                "video directory are metadata "
                "and add a row for each of them. Note "
                "this won't save the metadata.",
                target="add-rows-for-missing-button",
            )

            generate_yaml_tooltip = dbc.Tooltip(
                "Generate YAML files from a selected spreadsheet. "
                "Only rows with a corresponding video (or symlink) "
                "in the video directory will be considered. "
                "ATTENTION! This will overwrite any existing YAML files with "
                "the same name!",
                target="generate-yaml-files-button",
            )

            return html.Div(
                [
                    metadata_table,
                    auxiliary_buttons_row,
                    alert_message_row,
                    import_message_row,
                    check_missing_files_tooltip,
                    generate_yaml_tooltip,
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
            number of clicks on the 'select all' button
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
        list_selected_rows : list[int]
            a list of indices for the currently selected rows
        n_clicks_select_all : int
            number of clicks on the 'select all' button
        n_clicks_unselect_all : int
            number of clicks on the 'unselect all' button
        n_clicks_export : int
            number of clicks on the 'export' button
        alert_state : bool
            visibility of the information message
        alert_message : str
            text of the information message
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

    @app.callback(
        Output("import-message", "is_open"),
        Output("import-message", "children"),
        Output("import-message", "color"),
        Input("upload-spreadsheet", "contents"),
        State("upload-spreadsheet", "filename"),
        State("import-message", "is_open"),
        State("session-storage", "data"),
    )
    def generate_yaml_files_from_spreadsheet(
        spreadsheet_uploaded_content: str,
        spreadsheet_filename: str,
        import_message_state: bool,
        app_storage: dict,
    ):
        """Generate yaml files from spreadsheet

        From example at
        https://dash.plotly.com/dash-core-components/upload#displaying-uploaded-spreadsheet-contents

        Parameters
        ----------
        spreadsheet_uploaded_content : str
            string holding the uploaded content
        spreadsheet_filename : str
            name of the uploaded spreadsheet
        import_message_state : bool
            visibility state of the import message

        Returns
        -------
        import_message_state : bool
            visibility state of the message to display when import is completed
        import_message_text : str
            text of the import message
        import_message_color : str
            color of the import message
        """
        import_message_text = ""
        import_message_color = "warning"

        # if data is uploaded: read uploaded content as a dataframe
        if spreadsheet_uploaded_content is not None:
            _, content_string = spreadsheet_uploaded_content.split(",")
            decoded = base64.b64decode(content_string)
            try:
                # as csv
                if "csv" in pl.Path(spreadsheet_filename).suffix:
                    df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
                # as xls(x)
                elif "xls" in pl.Path(spreadsheet_filename).suffix:
                    df = pd.read_excel(io.BytesIO(decoded))
                else:
                    import_message_state = True
                    import_message_text = "Only csv or xls(x) files accepted"
                    import_message_color = "warning"

                    return (
                        import_message_state,
                        import_message_text,
                        import_message_color,
                    )

            except Exception as e:
                print(e)
                import_message_state = True
                import_message_text = (
                    "There was an error reading" f" this file ({e})."
                )
                import_message_color = "danger"

            # convert all fields in dataframe to strings
            # (otherwise datetime fields are not encoded correctly in the YAML)
            df = df.applymap(str)

            # check if columns in spreadsheet match metadata file:
            # if not, add missing columns
            list_columns = df.columns.tolist()
            list_metadata_fields = list(app_storage["metadata_fields"].keys())
            list_columns_to_add = [
                f for f in list_metadata_fields if f not in list_columns
            ]
            # TODO: warn/break if columns only in spreadsheet?
            for col in list_columns_to_add:
                df[col] = ""

            # convert to list of dictionaries, one per row
            list_dict_per_row = df.to_dict("records")

            # exclude rows that do not exist as a video file or a symlink
            # in the video dir
            # TODO: select whether to overwrite existing YAML?
            video_dir = app_storage["config"]["videos_dir_path"]
            field_to_use_as_filename = app_storage["config"][
                "metadata_key_field_str"
            ]

            list_filepaths_to_check = [
                pl.Path(video_dir, row[field_to_use_as_filename])
                for row in list_dict_per_row
            ]
            list_dict_per_row = [
                row
                for row, fpath in zip(
                    list_dict_per_row, list_filepaths_to_check
                )
                if pl.Path(fpath).is_file() or pl.Path(fpath).is_symlink()
            ]

            # dump as yaml files
            for row in list_dict_per_row:
                yaml_filename = (
                    pl.Path(row[field_to_use_as_filename]).stem
                    + ".metadata.yaml"
                )

                with open(pl.Path(video_dir) / yaml_filename, "w") as yamlf:
                    yaml.dump(row, yamlf, sort_keys=False)

            # update message
            import_message_text = (
                f"{len(list_dict_per_row)} YAML files"
                f" generated in video directory: {video_dir}."
                " Please refresh the page to update the metadata table."
            )
            import_message_color = "success"
            import_message_state = True

        return (
            import_message_state,
            import_message_text,
            import_message_color,
        )
