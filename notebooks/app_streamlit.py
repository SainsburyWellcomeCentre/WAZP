'''
Checking sample dashboard

'''
# %%%%%%%%%%%%%%%%
# imports
import streamlit as st



# %%%%%%%%%%%%%%
#  Params
video_path = '/Users/sofia/Documents_local/Zoo_SWC project/Example_videos/jwaspE_nectar-open-close.m4v'#avi'--avi not valid 


# %%%%%%%%%%%%%%%%%%%%%%%%%%
# Add video widget
# ideally: frame by frame or play; extract number of frames
video_file = open(video_path, 'rb')
video_bytes = video_file.read() # can I get number of frames here?

st.video(video_bytes) #format


# %%%%%%%%%%%%%%%%%%%
#  Add video slider for range of recorded frames
# ideally: in slider show tagged events (from metadata,/json?)




# %%%%%%%%%%%%%%%%%
#  Plot data related to selected frames