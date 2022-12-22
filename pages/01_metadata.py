# Define the page's content within a variable called layout or
# a function called layout that returns the content.


import base64

import dash
import yaml
from dash import Input, Output, State, callback, dcc, html

import wazp.utils

###############
# Register this page
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
                    wazp.utils.df_from_metadata_yaml_files(video_dir)),
                html.Button('Add Row', id='editing-rows-button', n_clicks=0)
            ]
        )  # returns children of 'output-data-upload'


@callback(
    Output("metadata-table", "data"),
    Input("editing-rows-button", "n_clicks"),
    State("metadata-table", "data"),
    # data = output from df.to_dict("records")
    # (list of dicts, one dict per row)
    State("metadata-table", "columns"),  # table columns
    prevent_initial_call=True  # to avoid errors due to input/output
    # components not existing in initial layout
)
def add_row(n_clicks_add_row, table_rows, table_columns):
    if n_clicks_add_row > 0:
        table_rows.append({c['id']: '' for c in table_columns})
    return table_rows
