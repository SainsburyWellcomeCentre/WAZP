from pathlib import Path
from typing import Optional

import pandas as pd
from file_utils import check_file_io_safety


def load_poses_from_dlc(file_path: Path) -> Optional[pd.DataFrame]:
    """Load pose estimation results from a DeepLabCut (DLC) files.
    Files must be in .h5 format

    Parameters
    ----------
    file_path : pathlib Path
        Path to the file containing the DLC poses.

    Returns
    -------
    pandas DataFrame
        DataFrame containing the DLC poses
    """

    try:
        df = pd.read_hdf(file_path, "df_with_missing")
        # above line does not necessarily return a DataFrame
        df = pd.DataFrame(df)
    except (OSError, TypeError, ValueError) as e:
        error_msg = (
            f"Could not load poses from {file_path}. "
            "Please check that the file is valid and readable."
        )
        raise OSError(error_msg) from e
    return df


def save_poses_to_dlc(df: pd.DataFrame | pd.Series, file_path: Path):
    """Save pose estimation results to a DeepLabCut (DLC) .h5 file.
    Also saves the poses to a .csv file with the same name.

    Parameters
    ----------
    df : pandas DataFrame
        DataFrame containing the DLC poses
    file_path : pathlib Path
        Path to the .h5 file to save the DLC poses to.
    """

    if file_path.suffix != ".h5":
        raise ValueError(
            f"`file_path` must be a .h5 file, but got {file_path.suffix} instead."
        )

    try:
        df.to_hdf(file_path, key="df_with_missing", mode="w")
        df.to_csv(file_path.with_suffix(".csv"))
    except (OSError, TypeError, ValueError) as e:
        error_msg = (
            f"Could not save poses to {file_path}. "
            "Please check that the file is valid and writable."
        )
        raise OSError(error_msg) from e


def extract_clip_from_poses(
    input_poses: Path,
    output_poses: Path,
    start_frame: int = 0,
    clip_duration: int = 30,
    overwrite: bool = True,
):
    """Extract a clip from a pose tracks DLC .h5 file and save it to a new .h5 file.
    Also saves the extracted poses to a .csv file with the same name.

    Clips are zero-indexed, i.e. the first frame is frame 0.
    So if you want to extract frames 0-29, aka the first 30 frames,
    you would set start_frame=0 and clip_duration=30.

    Parameters
    ----------
    input_poses : pathlib Path
        Path to DLC .h5 file containing the pose tracks (pose estimation results).
    output_poses : pathlib Path
        Path to the .h5 file to save the extracted pose tracks to.
    start_frame : int, optional
        Starting frame, by default 0
    clip_duration : int, optional
        Clip duration in frames, by default 30
    overwrite : bool, optional
        Whether overwriting output file is allowed, by default True
    """

    if check_file_io_safety(input_poses, output_poses, overwrite=overwrite):
        print(f"Extracting clip from pose tracks {input_poses}...")
        df = load_poses_from_dlc(input_poses)
        if type(df) is pd.DataFrame:
            end_frame = start_frame + clip_duration
            clip = df.iloc[start_frame:end_frame]
            save_poses_to_dlc(clip, output_poses)
            print(f"Extracted poses for frames {start_frame}-{end_frame}.")
            print(f"Saved to {output_poses}.")
        else:
            raise TypeError(
                f"Expected DataFrame, but got {type(df)} instead. "
                "Please check that the file is valid and readable."
            )
