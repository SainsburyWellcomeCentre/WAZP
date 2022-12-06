# %% Read all json files and visualise in dash?

import csv
import json
import os

import pandas as pd
from dash import Dash, dash_table

import wazp.metadata.utils as utils


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Generate jsons from csv
csv_file_path = (
    "./sample_metadata/master-list-sample.csv"
)
utils.csv_to_json_per_video(
    csv_file_path, "File", "./sample_metadata"
)


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Read all jsons in dir as dataframe
parent_dir = "./sample_metadata"
list_json_files = [el for el in os.listdir(parent_dir) if el.endswith(".json")]

read_fn = lambda x: pd.read_json(os.path.join(parent_dir, x), orient="index")
df = pd.concat(map(read_fn, list_json_files), ignore_index=True, axis=1)
df.head()  # TODO fix key
# df.shape

# %%
# for js in list_json_files:
#     df = pd.read_json(os.path.join(parent_dir,js), orient='index')

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Visualise in Dash
# https://dash.plotly.com/datatable
app = Dash(__name__)
app.layout = dash_table.DataTable(
    df.to_dict("records"), [{"name": i, "id": i} for i in df.columns]
)

if __name__ == "__main__":
    app.run_server(debug=True)

# %%
