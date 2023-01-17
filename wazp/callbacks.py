import base64
import pathlib as pl

import re

import pandas as pd
import yaml
from dash import Input, Output, State, html

import wazp.utils

##########
VIDEO_TYPES = [".avi", ".mp4"]
# TODO: other video extensions? have this in project config file instead?


##########
def get_metadata_callbacks(app):

    #####################################
    # Config file upload
    @app.callback(
        Output("output-data-upload", "children"),
        Input("upload-data", "contents"),
        State("upload-data", "filename"),
        # State('upload-data', 'last-modified'),
    )
    def update_file_drop_output(up_content, up_filename):
        """
        Read uploaded project config file and return component to visualise
        table with metadata per video. The component includes auxiliary buttons.
        """
        if up_content is not None:
            _, content_str = up_content.split(",")
            try:
                if "yaml" in up_filename:
                    # get config
                    cfg = yaml.safe_load(base64.b64decode(content_str))
                    # get video dir
                    video_dir = cfg["videos_dir_path"]
                    # get metadata fields dict
                    with open(cfg["metadata_fields_file_path"]) as mdf:
                        metadata_fields_dict = yaml.safe_load(mdf)

            except Exception as e:
                print(e)
                return html.Div(["There was an error processing this file."])

            return html.Div(
                [
                    wazp.utils.metadata_tbl_component_from_df(
                        wazp.utils.df_from_metadata_yaml_files(
                            video_dir, metadata_fields_dict
                        )
                    ),
                    html.Div(
                        [
                            html.Button(
                                children="Check for missing metadata files",
                                id="add-rows-for-missing-button",
                                n_clicks=0,
                                style={"margin-right": "10px"}
                            ),
                            html.Button(
                                children="Add empty row",
                                id="add-row-manually-button",
                                n_clicks=0,
                                style={"margin-right": "10px"}
                            ),
                            html.Button(
                                children="Export selected rows as yaml",
                                id="export-selected-rows-button",
                                n_clicks=0,
                                style={"margin-right": "10px"}
                            ),
                        ]
                    ),
                ]
            )  # returns children of 'output-data-upload'

    ############################################################
    # Add rows to table (manually or for missing files)
    @app.callback(
        Output("metadata-table", "data"),
        Output("add-row-manually-button", "n_clicks"),
        Output("add-rows-for-missing-button", "n_clicks"),
        Input("add-row-manually-button", "n_clicks"),
        Input("add-rows-for-missing-button", "n_clicks"),
        State("metadata-table", "data"),  # (list of dicts, one dict per row)
        State("metadata-table", "columns"),  # table columns
        State("upload-data", "contents"),
        # prevent_initial_call=True,  # to avoid errors due to input/output
        # components not existing in initial layout---TODO: fails if I refresh!
    )
    def add_rows(
        n_clicks_add_row_manually,
        n_clicks_add_rows_missing,
        table_rows,
        table_columns,
        up_content,
    ):
        """
        Add rows to table, either manually or by checking missing files
        """

        # Manually
        if n_clicks_add_row_manually > 0 and table_columns:
            table_rows.append({c["id"]: "" for c in table_columns})
            n_clicks_add_row_manually = 0
            # reset manual clicks
            # (otherwise triggered anytime a button is clicked)

        # For missing files
        if n_clicks_add_rows_missing > 0 and table_columns:
            # Get list of Files currently in table
            list_files_in_tbl = [
                d["File"] for d in table_rows
            ]  # TODO check if a better way?

            # Read config for videos directory
            _, content_str = up_content.split(",")
            cfg = yaml.safe_load(base64.b64decode(content_str))
            video_dir = cfg["videos_dir_path"]

            # Get list of videos without metadata and not in table
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

            # Add a row for every 'missing' video
            for vid in list_videos_wo_metadata:
                table_rows.append(
                    {
                        c["id"]: vid if c["id"] == "File" else ""
                        for c in table_columns
                    }
                )
                n_clicks_add_rows_missing = 0  # reset clicks

            # If the original table had only one empty row: pop it
            # (it occurs if initially no yaml files)
            # TODO: this is a bit hacky maybe? is there a better way
            if list_files_in_tbl == [""]:
                table_rows = table_rows[1:]

        return table_rows, n_clicks_add_row_manually, n_clicks_add_rows_missing

    ###########################
    # If a cell has been edited: change state (checkbox) of the row
    # https://community.plotly.com/t/detecting-changed-cell-in-editable-datatable/26219/5
    # https://dash.plotly.com/datatable/editable#adding-or-removing-rows
    @app.callback(
        Output("metadata-table", "selected_rows"),
        Input("metadata-table", "data_previous"),
        State("metadata-table", "data"),
        State("metadata-table", "selected_rows"),
    )
    def set_edited_row_checkbox_to_true(
        data_previous,
        data,
        list_selected_rows,
    ):
        # pdb.set_trace()
        if data_previous is not None:

            # TODO: potentially faster by comparing dicts rather than dfs?
            # (find the dict in the 'data' list with same key but diff value)
            df = pd.DataFrame(data=data)
            df_previous = pd.DataFrame(data_previous)
            df_diff = df.merge(df_previous, how="outer", indicator=True).loc[
                lambda x: x["_merge"] == "left_only"
            ]

            # update selected rows
            # could pandas indices and dash indices  mismatch?
            list_selected_rows += [
                i for i in df_diff.index.tolist()
                if i not in list_selected_rows
                ]
            # list_selected_rows += df_diff.index.tolist()
            # list_selected_rows = list(set(list_selected_rows))

        return list_selected_rows

    #########################
    # Export selected rows as yaml
    @app.callback(
        # Output("metadata-table", "selected_rows"),
        Output("export-selected-rows-button", "n_clicks"),
        Input("export-selected-rows-button", "n_clicks"),
        State("metadata-table", "data"),
        State("metadata-table", "selected_rows"),
        State("upload-data", "contents"),
        State("upload-data", "filename"),
    )
    def export_selected_rows_as_yaml(
        n_clicks_export,
        data,
        list_selected_rows,
        up_content,
        up_filename
    ):
        if n_clicks_export > 0:

            # Get config from uploaded file
            if up_content is not None:
                _, content_str = up_content.split(",")
            try:
                if "yaml" in up_filename:
                    cfg = yaml.safe_load(base64.b64decode(content_str))
                    video_dir = cfg["videos_dir_path"]
                    metadata_key_str = cfg["metadata_key_field_str"]
            except Exception as e:
                print(e)
                return html.Div(["There was an error processing this file."])

            # Export selected rows
            for row in [data[i] for i in list_selected_rows]:
                # extract key per row (typically, the value under 'File')
                key = row[metadata_key_str].split('.')[0]  # remove video extension

                # write each row to yaml
                yaml_filename = key + ".metadata.yaml"
                with open(pl.Path(video_dir) / yaml_filename, "w") as yamlf:
                    yaml.dump(row, yamlf, sort_keys=False)

            n_clicks_export = 0
            return n_clicks_export