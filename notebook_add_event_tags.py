# %%%%%%%%%%%%%%%%%%
import pathlib as pl
import pickle

# import cv2
import pandas as pd
import yaml

# %%%%%%%%%%%%%%%%%%%%%%%
project_config_path = "./sample_project/input_config.yaml"

# %%%%%%%%%%%%%%%%%%%%%
# read project config from yaml
with open(project_config_path) as f:
    config = yaml.safe_load(f)


# list of videos in parent dir
list_video_files = list(pl.Path(config["videos_dir_path"]).glob("*.avi"))
# list of yaml in parent dir
list_yaml_files = list(pl.Path(config["videos_dir_path"]).glob("*.yaml"))


# %%%%%%%%%%%%%%%%%%%%%%%%%%%
# get number of frames from associated h5 files
list_h5_file_paths = [
    pl.Path(config["pose_estimation_results_path"])
    / pl.Path(pl.Path(vd).stem + config["pose_estimation_model_str"] + ".h5")
    for vd in list_video_files
]

nframes_per_video = {
    vid.name: len(pd.read_hdf(f))
    for vid, f in zip(list_video_files, list_h5_file_paths)
}

# save as pickle
with open("nframes_per_video.pickle", "wb") as handle:
    pickle.dump(nframes_per_video, handle, protocol=pickle.HIGHEST_PROTOCOL)

# # %%
# with open('nframes_per_video.pickle', 'rb') as handle:
#     b = pickle.load(handle)


# %%%%%%%%%%%%%%%%%%%%%%%%
# add info to metadata file
for yf in list_yaml_files:
    nframes = nframes_per_video[pl.Path(yf.stem).stem + ".avi"]
    tags_locations = [int(x * nframes) for x in [0, 1 / 3, 2 / 3, 1]]
    tags_locations[-1] -= 1

    with open(yf, "r") as yaml_file:
        # read metadata file
        metadata = yaml.safe_load(yaml_file)
        # add event tags
        metadata["Events"] = {
            tg: val for tg, val in zip(config["event_tags"], tags_locations)
        }

    # write to metadata file
    with open(yf, "w") as yaml_file:
        yaml.safe_dump(metadata, yaml_file, sort_keys=False)


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# get number of frames for each video
# list_frames_per_video = [
#     int(
#         cv2.VideoCapture(str(vid)).get(
#             cv2.CAP_PROP_FRAME_COUNT
#         )
#     )
#     for vid in list_video_files
# ]
