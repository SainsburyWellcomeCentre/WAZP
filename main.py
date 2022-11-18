'''
Draft pipeline

'''
###############
import json
import os
import metadata_utils
  
# %%%%%%%%%%%%%%%%%%%%%%%%
# Input params (eventually CLI args?)
input_config_path = '/Users/sofia/Documents_local/Zoo_SWC project/WAZP/input_config.json'

# %%%%%%%%%%%%%%%%%%%%%%%%
#  Read input config 
# Should include:
# - path to videos directory
# - path to pose estim model weights + any other params required to run inference (DLC for now)
# Probably we would set here any other defaults?
with open(input_config_path, 'r') as f:
    input_config = json.load(f)
  

# %%%%%%%%%%%%%%%%%%%%%%%%
# Add metadata per video
# - check videos in videos_dir which do not have a metadata file
# - request metadata for them
# - launch a Dash/Plotly browser-based viz to see metadat as table?
metadata_utils.csv_to_json_per_video('sample_metadata/master-list-sample.csv','File','sample_metadata')

# %%%%%%%%%%%%%%%%%%
# Define ROIs per video
# - add coord syst and ROI per video to metadata