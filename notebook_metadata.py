"""
Draft pipeline

"""
# %%
import sys

sys.path.append("../")

#%%
###############
import os
import yaml
import pandas as pd

import wazp.metadata.utils as mu

from dash import Dash, dash_table


# %%%%%%%%%%%%%%%%%%%%%%%%
# Input params (eventually CLI args?)
input_config_path = "./sample_project_cfg/input_config.yaml"

# %%%%%%%%%%%%%%%%%%%%%%%%
#  Read input config
# Should include:|
# - path to videos directory
# - path to pose estim model weights + any other params required to run inference (DLC for now)
# Probably we would set here any other defaults?
with open(input_config_path, "r") as f:
    input_config = yaml.safe_load(f)


# %%%%%%%%%%%%%%%%%%%%%%%%
# Add metadata per video
# - check videos in videos_dir which do not have a metadata file
# - request metadata for them
# - launch a Dash/Plotly browser-based viz to see metadat as table?
mu.csv_to_yaml_per_video(
    "sample_metadata/master-list-sample.csv", "File", "sample_metadata"
)


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Visualize current metada in dashboard
# - Read all yaml as a datafame
# - Visualize dataframe in dash

# Read all YAML in dir as dataframe
list_json_files = [
    el
    for el in os.listdir(input_config["videos_dir_path"])
    if el.endswith(".yaml")
]

# %%
# read_fn = lambda x: pd.json_normalize(
#     os.path.join(input_config["videos_dir_path"], x), orient="index"
# )
# df = pd.concat(map(read_fn, list_json_files), ignore_index=True, axis=1)
# df.head()  # TODO fix key
# df.shape
list_df = []
for el in list_json_files:
    with open(os.path.join(input_config["videos_dir_path"], el), "r") as f:
        yaml_df = pd.json_normalize(yaml.safe_load(f))
        list_df.append(yaml_df)

df = pd.concat(list_df) #, ignore_index=True, axis=1)

df.head()
print(df.shape)

# %%%%%%%%%%%%%%%
# Show in Dashboard
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/solar.csv')
app = Dash(__name__)

app.layout = dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns])


app.run_server(debug=True)

# %%
# https://dash-bootstrap-components.opensource.faculty.ai/docs/quickstart/
# import dash_bootstrap_components as dbc

# %%%%%%%%%%%%%%%%%%
# Define ROIs per video
# - add coord syst and ROI per video to metadata
