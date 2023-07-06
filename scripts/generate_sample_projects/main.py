"""Generate sample projects based on the Zoo data on /ceph/zoo.

This script can generate 4 sample projects for a given species/experiment.
The generated projects will be saved in a local data repository - DATA_REPO_LOCAL,
which should be a clone of https://gin.g-node.org/SainsburyWellcomeCentre/WAZP.

DATA_REPO_LOCAL
└── SPECIES
    ├── short-clips_raw
    ├── short-clips_compressed
    ├── entire-video_raw
    └── entire-video_compressed

"short-clips_raw" contains ~10s clips extracted from the input videos.
"short-clips_compressed" contains compressed versions of the clips in short-clips_raw.
"entire_video_raw" holds an entire input video (use for critical tests only).
"entire_video_compressed" contains a compressed version of the entire input video.

Each of the above 4 sample projects has the following structure:
PROJECT
    └── videos
        ├── list of video files *.avi or *.mp4
        └── list of video metadata files *.metadata.yaml
    └── pose_estimation_results
        └── list of *.h5 files
    ├── WAZP_config.yaml
    └── metadata_fields.yaml

The latter two files are copies of the respective template files in this directory.
"""

import pathlib as pl
import shutil

from video_utils import compress_video, extract_clip_from_video

###############################################################################
# Modify these variables according to your system and needs
###############################################################################

# Path to the local data repository
# This should be a clone of https://gin.g-node.org/SainsburyWellcomeCentre/WAZP
DATA_REPO_LOCAL = pl.Path("/home/nsirmpilatze/Code/Data/WAZP/")
# Shorthand for the species/experiment
SPECIES = "jewel-wasp"

# Local path to the source experiment on /ceph/zoo
ZOO_DIR = pl.Path(
    "/media/ceph-zoo/processed/LondonZoo/"
    "jewel-wasp_Ampulex-compressa/DLC_femaleandmale/"
    "jwasp_femaleandmale-Sanna-2022-09-12/videos"
)

# List of input video filenames for short clips
input_videos_for_short_clips = [
    "jwaspI_nectar-open-close_control.avi",
    "jwaspI_nectar-open-close_nectar1.avi",
    "jwaspK_nectar-open-close_nectar2.avi",
    "jwaspK_nectar-open-close_wateronly_s.avi",
]
# Entire video to be copied
input_video_entire = ["jwaspE_nectar-open-close_control.avi"]

# Parameters for short clips
# unit: frames
clip_duration = 400
start_frame = 6000  # to skip the first minutes of each video


###############################################################################
# The code below should work (mostly) without modification
###############################################################################

# Get the parent directory of the current script
current_dir = pl.Path(__file__).parent
# Path to the WAZP config file to use as a template
wazp_config_template = pl.Path(current_dir / "WAZP_config_template.yaml")
# Path to the metadata fields file to use as a template
metadata_fields_template = pl.Path(current_dir / "metadata_fields_template.yaml")

# Create the output directory structure
out_dir = DATA_REPO_LOCAL / SPECIES
out_dir.mkdir(exist_ok=True, parents=True)

project_dirs = [
    out_dir / "short-clips_raw",
    out_dir / "short-clips_compressed",
    out_dir / "entire-video_raw",
    out_dir / "entire-video_compressed",
]

for project_dir in project_dirs:
    project_dir.mkdir(exist_ok=True)
    (project_dir / "videos").mkdir(exist_ok=True)
    (project_dir / "pose_estimation_results").mkdir(exist_ok=True)
    shutil.copy(wazp_config_template, project_dir / "WAZP_config.yaml")
    shutil.copy(metadata_fields_template, project_dir / "metadata_fields.yaml")

# Extract short clips from the supplied input videos
for input_video_name in input_videos_for_short_clips:
    input_video_path = ZOO_DIR / input_video_name
    raw_clip_name = input_video_path.name
    compr_clip_name = input_video_path.stem + ".mp4"

    # Extract raw video clip
    extract_clip_from_video(
        input_video_path,
        start_frame=start_frame,
        clip_duration=clip_duration,
        output_dir=out_dir / "short-clips_raw" / "videos",
        output_filename=raw_clip_name,
        copy_metadata=True,
    )

    # Compress extracted clip
    compress_video(
        input_video=out_dir / "short-clips_raw" / "videos" / raw_clip_name,
        output_video=out_dir / "short-clips_compressed" / "videos" / compr_clip_name,
        codec="libx264",
        crf=23,
        copy_metadata=True,
    )


# Copy entire video
for input_video_name in input_video_entire:
    input_entire_video_path = ZOO_DIR / input_video_name
    raw_video_name = input_entire_video_path.name
    compr_video_name = input_entire_video_path.stem + ".mp4"

    # Copy raw video
    shutil.copy(
        input_entire_video_path,
        out_dir / "entire-video_raw" / "videos" / raw_video_name,
    )

    # Compress raw video
    compress_video(
        input_video=out_dir / "entire-video_raw" / "videos" / raw_video_name,
        output_video=out_dir / "entire-video_compressed" / "videos" / compr_video_name,
        codec="libx264",
        crf=23,
        copy_metadata=True,
    )
