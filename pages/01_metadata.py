# Define the page's content within a variable called layout or
# a function called layout that returns the content.

import base64
import pathlib as pl
import re

import dash
import yaml
from dash import Input, Output, State, callback, dcc, html

import wazp.utils

##########
VIDEO_TYPES = [".avi", ".mp4"]  # others?


###############
# Register this page
# Notes:
# - dash.page_registry is an ordered dict:
#   - keys: pages.<name of file under pages dir>
#   - values: a few attributes of the page...including 'layout'
dash.register_page(__name__)

######################
# Define upload component
upload = dcc.Upload(
    id="upload-data",
    children=html.Div(
        ["Drag and Drop or ", html.A("Select project config file")]
    ),
    style={
        "width": "100%",
        "height": "60px",
        "lineHeight": "60px",
        "borderWidth": "1px",
        "borderStyle": "dashed",
        "borderRadius": "5px",
        "textAlign": "center",
        "margin": "10px",
    },
    # Allow multiple files to be uploaded
    multiple=False,
)


########################
# Define layout
layout = html.Div(
    children=[
        html.H1(children="Metadata"),
        upload,  # upload component
        html.Div(
            id="output-data-upload", style={"height": "1200px"}
        ),  # component to hold the output from the data upload
    ]
)


#####################################
# Callbacks
# Config file upload
@callback(
    Output("output-data-upload", "children"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),  # State('upload-data', 'last-modified'),
)
def update_file_drop_output(up_content, up_filename):
    if up_content is not None:
        _, content_str = up_content.split(",")
        try:
            if "yaml" in up_filename:
                cfg = yaml.safe_load(base64.b64decode(content_str))
                video_dir = cfg["videos_dir_path"]

        except Exception as e:
            print(e)
            return html.Div(["There was an error processing this file."])

        return html.Div(
            [
                wazp.utils.metadata_tbl_component_from_df(
                    wazp.utils.df_from_metadata_yaml_files(video_dir)
                ),
                html.Div(
                    [
                        html.Button(
                            children="Check for missing metadata files",
                            id="add-rows-for-missing-button",
                            n_clicks=0,
                        ),
                        html.Button(
                            children="Add row manually",
                            id="add-row-manually-button",
                            n_clicks=0,
                        ),
                    ]
                ),
            ]
        )  # returns children of 'output-data-upload'


# Add rows to table (manually or for missing files)
@callback(
    Output("metadata-table", "data"),
    Output("add-row-manually-button", "n_clicks"),
    Output("add-rows-for-missing-button", "n_clicks"),
    Input("add-row-manually-button", "n_clicks"),
    Input("add-rows-for-missing-button", "n_clicks"),
    State(
        "metadata-table", "data"
    ),  # data = output from df.to_dict("records")
    # (list of dicts, one dict per row)
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
    if n_clicks_add_row_manually > 0:
        table_rows.append({c["id"]: "" for c in table_columns})
        n_clicks_add_row_manually = 0  # reset manual clicks

    # For missing files
    if n_clicks_add_rows_missing > 0:
        # Get list of files shown in table
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
                list_metadata_files.append(re.sub(".metadata$", "", f.stem))
            elif any(v in str(f) for v in VIDEO_TYPES):
                list_video_files.append(f)  # list of PosixPaths

        list_videos_wo_metadata = [
            f.name
            for f in list_video_files
            if (f.stem not in list_metadata_files)
            and (f.name not in list_files_in_tbl)
        ]
        # list(
        #     set([
        #         vf.stem for vf in list_video_files
        #         ]) - set(list_metadata_files)
        #     # Not symmetric OJO!set(li1).symmetric_difference(set(li2))
        # )

        # Add a row for every video
        for vid in list_videos_wo_metadata:
            table_rows.append(
                {
                    c["id"]: vid if c["id"] == "File" else ""
                    for c in table_columns
                }
            )
            n_clicks_add_rows_missing = 0  # reset clicks

    return table_rows, n_clicks_add_row_manually, n_clicks_add_rows_missing
