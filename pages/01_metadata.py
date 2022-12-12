# Define the page's content within a variable called layout or 
# a function called layout that returns the content.

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
import os
import yaml

import pdb

###############
# Register this page
dash.register_page(__name__)


####################
# Read yamls in dir as pandas dataframe
# TODO: refactor, I think it could be more compact (see below)
parent_dir = "/Users/sofia/Documents_local/Zoo_SWC project/WAZP/sample_project/videos"
list_metadata_files = [el for el in os.listdir(parent_dir) if el.endswith("metadata.yaml")]

list_df_metadata = []
for yl in list_metadata_files:
    with open(os.path.join(parent_dir, yl)) as f:
        list_df_metadata.append(
            pd.DataFrame.from_dict(
                yaml.safe_load(f), 
                orient='index'))
df = pd.concat(list_df_metadata, ignore_index=True, axis=1).T # TODO review why transpose required

# TODO: previous approach with json, can I do it as compact?
# read_fn = lambda x: pd.read_json(os.path.join(parent_dir, x), orient="index")
# df = pd.concat(map(read_fn, list_metadata_files), ignore_index=True, axis=1)


###############
# Define table component from pandas dataframe
# TODO: check table style options (see Table class)
table = dbc.Table.from_dataframe(
    df,
    bordered=True, 
    hover=True,
    responsive=True, # if True, table can be scrolled horizontally?
    striped=True, # applies zebra striping to the rows
    size='sm'
    )


########################
# Define layout
layout = html.Div(
    children=[
        html.H1(children="Metadata"),
        html.Div(
            #children=""" This is the Metadata page content."""
            dbc.Container(table, className="p-5")
        ),
    ]
)
