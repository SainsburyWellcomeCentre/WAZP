import base64
import pathlib as pl

# import pdb
import re
from typing import Any

import dash
import dash_bootstrap_components as dbc
import utils
import yaml
from dash import Input, Output, State, dash_table, html

VIDEO_TYPES = [".avi", ".mp4"]
# TODO: other video extensions? have this in project config file instead?


def get_home_callbacks(app: dash.Dash) -> None:
    """
    Return all home callback functions

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
        """
        Save input config to temp shared memory

        See https://community.plotly.com/t/dash-plotly-share-callback-input-in-another-page-with-dcc-store/44190/2

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
                    cfg = yaml.safe_load(base64.b64decode(content_str))

                    # get metadata fields dict
                    with open(cfg["metadata_fields_file_path"]) as mdf:
                        metadata_fields_dict = yaml.safe_load(mdf)

                    # bundle data
                    data_to_store = {
                        "config": cfg,
                        "metadata_fields": metadata_fields_dict,
                    }

                    # output message
                    if not up_message_state:
                        up_message_state = not up_message_state
                    output_message = (
                        f"Input config for:"
                        f"{cfg['videos_dir_path']} processed successfully."
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
    """
    Return all metadata callback functions

    """

    @app.callback(
        Output("output-data-upload", "children"),
        Input("output-data-upload", "children"),
        State("session-storage", "data"),
    )
    def generate_metadata_table(
        metadata_output_children: list, data_in_storage: dict
    ) -> html.Div:
        """
        Read uploaded config file from cache and return component with:
        - table with metadata per video,
        - auxiliary buttons for common table manipulations

        """

        if not metadata_output_children:
            # get config and metadata fields
            (cfg, metadata_fields_dict) = (
                data_in_storage["config"],
                data_in_storage["metadata_fields"],
            )

            # return table+buttons
            return html.Div(
                [
                    # metadata table
                    utils.metadata_table_component_from_df(
                        utils.df_from_metadata_yaml_files(
                            cfg["videos_dir_path"], metadata_fields_dict
                        )
                    ),
                    # auxiliary buttons
                    html.Div(
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
                    ),
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
        State(
            "session-storage", "data"
        ),
    )
    def add_rows(
        n_clicks_add_row_manually: int,
        n_clicks_add_rows_missing: int,
        table_rows: list[dict],
        table_columns: list[dict],
        cfg_params_in_storage: tuple,
    ) -> tuple[list[dict], int, int]:
        """
        Add rows to metadata table, either:
        - manually
        - based on videos with missing yaml files

        Both are triggered by clicking the corresponding buttons

        """

        # Add empty rows manually
        if n_clicks_add_row_manually > 0 and table_columns:
            table_rows.append({c["id"]: "" for c in table_columns})
            n_clicks_add_row_manually = 0  # reset clicks

        # Add rows for videos w/ missing metadata
        if n_clicks_add_rows_missing > 0 and table_columns:
            # Read config for videos directory
            (cfg, _) = cfg_params_in_storage
            # _, content_str = up_content.split(",")
            # cfg = yaml.safe_load(base64.b64decode(content_str))
            video_dir = cfg["videos_dir_path"]

            # List of files currently shown in table
            list_files_in_tbl = [
                d[cfg["metadata_key_field_str"]] for d in table_rows
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
                and (f.name not in list_files_in_tbl)
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
            if list_files_in_tbl == [""]:
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
        data_previous: list,
        data: list[dict],
        data_page: list[dict],
        list_selected_rows: list[int],
        cfg_params_in_storage: tuple,
        alert_state: bool,
    ) -> tuple[list[int], int, int, bool, str]:
        """
        Modify the set of rows that are selected in metadata table.

        A row's checkbox is modified if:
        - the user edits the data on that row (checkbox set to True)
        - the export button is clicked (checkbox set to False after exporting)
        - the 'select/unselect' all button is clicked
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
            (cfg, _) = cfg_params_in_storage
            utils.export_selected_rows_as_yaml(data, list_selected_rows, cfg)

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


def get_dashboard_callbacks(app):
    @app.callback(
        Output("table-container", "children"),
        Input("table-container", "children"),
        State("session-storage", "data"),
    )
    def create_input_data_table(
        table_container_children: list,
        data_in_storage: dict,
    ):
        """
        Create table of videos with metadata with checkboxes

        """

        if not table_container_children:

            # videos list as df
            (cfg, metadata_fields_dict) = (
                data_in_storage["config"],
                data_in_storage["metadata_fields"],
            )
            df_metadata = utils.df_from_metadata_yaml_files(
                cfg["videos_dir_path"], metadata_fields_dict
            )
            df_metadata = df_metadata[[cfg["metadata_key_field_str"]]]

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

