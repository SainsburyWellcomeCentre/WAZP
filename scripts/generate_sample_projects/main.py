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
"entire-video_raw" holds an entire input video (use for critical tests only).
"entire-video_compressed" contains a compressed version of the entire input video.

Each of the above 4 sample projects has the following structure:
PROJECT
    └── videos
        ├── list of video files *.avi or *.mp4
        └── list of video metadata files *.metadata.yaml
    └── pose_estimation_results
        └── list of *.h5 files
    ├── WAZP_config.yaml
    └── metadata_fields.yaml

The latter two files are created based on template files present in this directory.
"""

import shutil
from pathlib import Path

from file_utils import check_file_io_safety, update_wazp_config_file
from pose_utils import extract_clip_from_poses
from video_utils import compress_video, copy_entire_video, extract_clip_from_video

###############################################################################
# Modify these variables according to your system and needs
###############################################################################

# Path to the local data repository
# This should be a clone of https://gin.g-node.org/SainsburyWellcomeCentre/WAZP
DATA_REPO_LOCAL = Path.home() / "WAZP_sample_data"
# Shorthand for the species/experiment
SPECIES = "jewel-wasp"

# Local path to the source experiment on /ceph/zoo
ZOO_DIR = Path(
    "/media/ceph-zoo/processed/LondonZoo/"
    "jewel-wasp_Ampulex-compressa/DLC_femaleandmale/"
    "jwasp_femaleandmale-Sanna-2022-09-12/videos"
)

# Whether to overwrite existing files
# When false, file copying/extraction steps are skipped if the output file exists
OVERWRITE = False

# List of input video filenames for short clips
input_videos_for_short_clips = [
    "jwaspI_nectar-open-close_control.avi",
    "jwaspI_nectar-open-close_nectar1.avi",
    "jwaspK_nectar-open-close_nectar2.avi",
    "jwaspK_nectar-open-close_wateronly_s.avi",
]
# Entire video to be copied
input_video_entire = ["jwaspE_nectar-open-close_control.avi"]

# Model name used for pose estimation
model_name = "DLC_resnet50_jwasp_femaleandmaleSep12shuffle1_1000000"

# Parameters for short clips
# unit: frames
clip_duration = 400
start_frame = 6000  # to skip the first minutes of each video
end_frame = start_frame + clip_duration


###############################################################################
# The code below should work (mostly) without modification
###############################################################################

# Get the parent directory of the current script
current_dir = Path(__file__).parent
# Path to the WAZP config file to use as a template
wazp_config_template = Path(current_dir / "WAZP_config_template.yaml")
# Path to the metadata fields file to use as a template
metadata_fields_template = Path(current_dir / "metadata_fields_template.yaml")

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
    videos_dir = (project_dir / "videos").absolute()
    videos_dir.mkdir(exist_ok=True)
    poses_dir = (project_dir / "pose_estimation_results").absolute()
    poses_dir.mkdir(exist_ok=True)
    for template in [wazp_config_template, metadata_fields_template]:
        target = project_dir / f"{template.name.split('_template')[0]}.yaml"
        if check_file_io_safety(template, target, overwrite=OVERWRITE):
            shutil.copy(template, target)
        if target == project_dir / "WAZP_config.yaml":
            update_wazp_config_file(
                target,
                model_str=model_name,
                videos_dir_path=videos_dir,
                pose_estimation_results_path=poses_dir,
            )

# Extract short clips from the supplied input videos
for input_video_name in input_videos_for_short_clips:
    input_video_path = ZOO_DIR / input_video_name
    input_poses_path = ZOO_DIR / f"{input_video_path.stem}{model_name}.h5"
    clip_suffix = f"_clip-{start_frame}-{end_frame}"

    raw_clip_name = f"{input_video_path.stem}{clip_suffix}{input_video_path.suffix}"
    raw_clip_path = out_dir / "short-clips_raw" / "videos" / raw_clip_name
    compr_clip_name = raw_clip_name.replace(input_video_path.suffix, ".mp4")
    compr_clip_path = out_dir / "short-clips_compressed" / "videos" / compr_clip_name

    poses_clip_filename = f"{input_video_path.stem}{clip_suffix}{model_name}.h5"
    raw_poses_path = (
        out_dir / "short-clips_raw" / "pose_estimation_results" / poses_clip_filename
    )
    compr_poses_path = (
        out_dir
        / "short-clips_compressed"
        / "pose_estimation_results"
        / poses_clip_filename
    )

    # Extract raw video clip
    extract_clip_from_video(
        input_video=input_video_path,
        output_clip=raw_clip_path,
        start_frame=start_frame,
        clip_duration=clip_duration,
        overwrite=OVERWRITE,
        copy_metadata=True,
    )
    # Extract the corresponding pose estimation results
    extract_clip_from_poses(
        input_poses=input_poses_path,
        output_poses=raw_poses_path,
        start_frame=start_frame,
        clip_duration=clip_duration,
        overwrite=OVERWRITE,
    )

    # Compress extracted clip
    compress_video(
        input_video=raw_clip_path,
        output_video=compr_clip_path,
        codec="libx264",
        crf=23,
        overwrite=OVERWRITE,
        copy_metadata=True,
    )
    # Copy the pose estimation results clip
    if check_file_io_safety(raw_poses_path, compr_poses_path, overwrite=OVERWRITE):
        shutil.copy(raw_poses_path, compr_poses_path)

# Copy entire video
for input_video_name in input_video_entire:
    input_video_path = ZOO_DIR / input_video_name
    input_poses_name = f"{input_video_path.stem}{model_name}.h5"
    input_poses_path = ZOO_DIR / input_poses_name

    raw_video_path = out_dir / "entire-video_raw" / "videos" / input_video_name
    compr_video_name = input_video_name.replace(input_video_path.suffix, ".mp4")
    compr_video_path = out_dir / "entire-video_compressed" / "videos" / compr_video_name

    raw_poses_path = (
        out_dir / "entire-video_raw" / "pose_estimation_results" / input_poses_name
    )
    compr_poses_path = (
        out_dir
        / "entire-video_compressed"
        / "pose_estimation_results"
        / input_poses_name
    )

    # Copy the raw entire video
    copy_entire_video(
        input_video=input_video_path,
        output_video=raw_video_path,
        overwrite=OVERWRITE,
        copy_metadata=True,
    )
    # Copy the corresponding pose estimation results
    if check_file_io_safety(input_poses_path, raw_poses_path, overwrite=OVERWRITE):
        shutil.copy(input_poses_path, raw_poses_path)
        print(f"Copied {input_poses_path} to {raw_poses_path}")

    # Compress the entire video
    compress_video(
        input_video=raw_video_path,
        output_video=compr_video_path,
        codec="libx264",
        crf=23,
        overwrite=OVERWRITE,
        copy_metadata=True,
    )
    # Copy the pose estimation results
    if check_file_io_safety(raw_poses_path, compr_poses_path, overwrite=OVERWRITE):
        shutil.copy(raw_poses_path, compr_poses_path)
        print(f"Copied {raw_poses_path} to {compr_poses_path}")
