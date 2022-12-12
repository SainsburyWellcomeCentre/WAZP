# Define the page's content within a variable called layout or 
# a function called layout that returns the content.
#
# File upload component:
# https://dash.plotly.com/dash-core-components/upload

import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import pandas as pd
import os
import yaml
import io
import base64

import pdb

###############
# Register this page
dash.register_page(__name__)


####################
# Read yamls in dir as pandas dataframe

def df_from_metadata_yaml_files(parent_dir):
    # TODO: refactor, I think it could be more compact (see below)

    list_metadata_files = [el for el in os.listdir(parent_dir) if el.endswith("metadata.yaml")]

    list_df_metadata = []
    for yl in list_metadata_files:
        with open(os.path.join(parent_dir, yl)) as f:
            list_df_metadata.append(
                pd.DataFrame.from_dict(
                    yaml.safe_load(f), 
                    orient='index'))
    return pd.concat(list_df_metadata, ignore_index=True, axis=1).T # TODO review why transpose required

# TODO: previous approach with json, can I do it as compact?
# read_fn = lambda x: pd.read_json(os.path.join(parent_dir, x), orient="index")
# df = pd.concat(map(read_fn, list_metadata_files), ignore_index=True, axis=1)


###############
# Define table component from pandas dataframe
# TODO: check table style options (see Table class)

def generate_tbl_component(parent_dir):
    # ##########################
    # Using html dash components
    # dataframe = df_from_metadata_yaml_files(parent_dir)
    # table = html.Table(
    #     children =
    #     [  # define table head?
    #         html.Thead(html.Tr([html.Th(col, style={'width':'15%'}) for col in dataframe.columns])), 
    #         # define table body
    #         html.Tbody(
    #             [
    #                 html.Tr(
    #                     [
    #                         html.Td(dataframe.iloc[i][col], style={'width':'15%'})
    #                         for col in dataframe.columns
    #                     ]
    #                 )
    #                 for i in range(len(dataframe)) #range(min(len(dataframe), max_rows))
    #             ]
    #         ),
    #     ],
    #     style={'width':'100%',}
    # )
    #########

    ######### 
    # Using bootstrap components
    table = dbc.Table.from_dataframe(
        df_from_metadata_yaml_files(parent_dir),
        bordered=True, 
        hover=False,# True
        responsive=True, # if True, table can be scrolled horizontally?
        striped=True, # applies zebra striping to the rows
        size='sm',
        style={'width':'100%',}
        )
    ############

    return dbc.Container(table, className="p-5")

######################
# Define upload component
upload = dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select project config file')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=False)


########################
# Define layout
layout = html.Div(
    children=[
        html.H1(children="Metadata"),
        upload, # upload component
        html.Div(id='output-data-upload'), # component to hold output from data upload
    ]
)


#####################################
# Callbacks

@callback(
    Output('output-data-upload', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'), #State('upload-data', 'last-modified'),
)
def update_file_drop_output(up_content, up_filename):
    if up_content is not None:
        content_type, content_str = up_content.split(',')
        try:
            if 'yaml' in up_filename:
                cfg = yaml.safe_load(base64.b64decode(content_str))
                video_dir = cfg['videos_dir_path']

        except Exception as e:
            print(e)
            return html.Div(['There was an error processing this file.'])

        return generate_tbl_component(video_dir) #returns children of 'output-data-upload'
