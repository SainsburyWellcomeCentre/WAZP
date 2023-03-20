import math
import pathlib as pl
from datetime import datetime, timedelta
from typing import Callable

import cv2
import pandas as pd
import plotly.express as px
import yaml


def df_from_metadata_yaml_files(
    parent_dir: str, metadata_fields_dict: dict
) -> pd.DataFrame:
    """Build a dataframe from all the metadata.yaml files in the input parent
    directory.

    If there are no metadata.yaml files in the parent directory, make a
    dataframe with the columns as defined in the metadata fields
    description and empty (string) fields


    Parameters
    ----------
    parent_dir : str
        path to directory with video metadata.yaml files
    metadata_fields_dict : dict
        dictionary with metadata fields descriptions

    Returns
    -------
    pd.DataFrame
        a pandas dataframe in which each row holds the metadata for one video
    """

    # List of metadata files in parent directory
    list_metadata_files = [
        str(f)
        for f in pl.Path(parent_dir).iterdir()
        if str(f).endswith(".metadata.yaml")
    ]

    # If there are no metadata (yaml) files:
    #  build dataframe from metadata_fields_dict
    if not list_metadata_files:
        return pd.DataFrame.from_dict(
            {c: [""] for c in metadata_fields_dict.keys()},
            orient="columns",
        )
    # If there are metadata (yaml) files:
    # build dataframe from yaml files
    else:
        list_df_metadata = []
        for yl in list_metadata_files:
            with open(yl) as ylf:
                list_df_metadata.append(
                    pd.DataFrame.from_dict(
                        {
                            k: [v if not isinstance(v, dict) else str(v)]
                            # in the df we pass to the dash table component,
                            # values need to be either str, number or bool
                            for k, v in yaml.safe_load(ylf).items()
                        },
                        orient="columns",
                    )
                )

        return pd.concat(list_df_metadata, ignore_index=True, join="inner")


def set_edited_row_checkbox_to_true(
    data_previous: list[dict], data: list[dict], list_selected_rows: list[int]
) -> list[int]:
    """Set a row's checkbox to True when its data is edited.

    Parameters
    ----------
    data_previous : list[dict]
        a list of dictionaries holding the previous state of the table
        (read-only)
    data : list[dict]
        a list of dictionaries holding the table data
    list_selected_rows : list[int]
        a list of indices for the currently selected rows

    Returns
    -------
    list_selected_rows : list[int]
        a list of indices for the currently selected rows
    """

    # Compute difference between current and previous table
    # TODO: faster if I compare dicts rather than dfs?
    # (that would be: find the dict in the 'data' list with
    # same key but different value)
    df = pd.DataFrame(data=data)
    df_previous = pd.DataFrame(data_previous)

    # ignore static type checking here,
    # see https://github.com/pandas-dev/pandas-stubs/issues/256
    df_diff = df.merge(df_previous, how="outer", indicator=True).loc[
        lambda x: x["_merge"] == "left_only"  # type: ignore
    ]

    # Update the set of selected rows
    list_selected_rows += [
        i for i in df_diff.index.tolist() if i not in list_selected_rows
    ]

    return list_selected_rows


def export_selected_rows_as_yaml(
    data: list[dict], list_selected_rows: list[int], app_storage: dict
) -> None:
    """Export selected rows as yaml files.

    Parameters
    ----------
    data : list[dict]
        a list of dictionaries holding the table data
    list_selected_rows : list[int]
        a list of indices for the currently selected rows
    app_storage : dict
        _description_
    """

    # Export selected rows
    for row in [data[i] for i in list_selected_rows]:
        # extract key per row
        key = row[app_storage["metadata_key_field_str"]].split(".")[
            0
        ]  # remove video extension

        # write each row to yaml
        yaml_filename = key + ".metadata.yaml"
        with open(
            pl.Path(app_storage["videos_dir_path"]) / yaml_filename, "w"
        ) as yamlf:
            yaml.dump(row, yamlf, sort_keys=False)

    return


def get_dataframes_to_combine(
    list_selected_videos: list,
    slider_start_end_labels: list,
    app_storage: dict,
):
    # build list of h5 files for the selected videos
    # TODO: provide an option to export as h5 or csv
    # TODO: try to make it generic to any pose estim library?
    # TODO: what is several pose_estimation_model_str are provided?
    # (right now DLC)
    list_h5_file_paths = [
        pl.Path(app_storage["config"]["pose_estimation_results_path"])
        / (
            pl.Path(vd).stem
            + app_storage["config"]["pose_estimation_model_str"]
            + ".h5"
        )
        for vd in list_selected_videos
    ]

    # loop thru videos and h5 files to read dataframe and
    # extract subset of rows
    list_df_to_export = []
    for h5, video in zip(list_h5_file_paths, list_selected_videos):

        # get the metadata file for this video
        # (built from video filename)
        yaml_filename = pl.Path(app_storage["config"]["videos_dir_path"]) / (
            pl.Path(video).stem + ".metadata.yaml"
        )

        # extract the frame numbers
        # from the slider position
        with open(yaml_filename, "r") as yf:
            metadata = yaml.safe_load(yf)
            # extract frame start/end
            frame_start_end = [
                metadata["Events"][x] for x in slider_start_end_labels
            ]
            # extract ROI paths
            # TODO
            # ...

        # read h5 as dataframe and add 'File'
        # as the outermost level of the (multi) index
        df = pd.concat(
            [pd.read_hdf(h5)],
            keys=[video],
            names=[app_storage["config"]["metadata_key_field_str"]],
            axis=1,
        )

        # add ROI and event tag per bodypart
        # TODO: is there a nicer way using pandas?
        # right now levels are hardcoded....
        # TODO: ideally event_tags are not repeated per bodypart
        # alternative; set as index? add frame from index?
        # # df = df.set_index([df.index, "event_tag"])
        metadata["Events"] = dict(
            sorted(
                metadata["Events"].items(),
                key=lambda item: item[1],
            )
        )  # ensure keys are sorted by value
        list_keys = list(metadata["Events"].keys())
        list_next_keys = list_keys[1:]
        list_next_keys.append("NAN")
        for vd in df.columns.get_level_values(0).unique().to_list():
            for scorer in df.columns.get_level_values(1).unique().to_list():
                for bdprt in df.columns.get_level_values(2).unique().to_list():
                    # assign ROI (placeholder for now)
                    # TODO: read from yaml and assign
                    df[vd, scorer, bdprt, "ROI"] = ""

                    # assign event_tag per bodypart
                    for ky, next_ky in zip(list_keys, list_next_keys):
                        df.loc[
                            (df.index >= metadata["Events"][ky])
                            & (
                                df.index
                                < metadata["Events"].get(next_ky, math.inf)
                            ),
                            (vd, scorer, bdprt, "event_tag"),
                        ] = ky

        # sort to ensure best performance
        # when accessing data
        # TODO: keep original bodyparts order?
        # rn: sorting alphabetically by bodypart
        df.sort_index(
            axis=1, level=["bodyparts"], ascending=[True], inplace=True
        )

        # select subset of rows based on
        # frame numbers from slider (both inclusive)
        # (index as frame number)
        list_df_to_export.append(
            df[
                (df.index >= frame_start_end[0])
                & (df.index <= frame_start_end[1])
            ]
        )

    return list_df_to_export


def assign_roi_colors(
    roi_names: list[str],
    cmap: list[str] = px.colors.qualitative.Dark24,
) -> dict:
    """
    Match ROI names to colors

    Parameters
    ----------
    roi_names : list of str
        List of ROI names
    cmap : list of str
        colormap for ROIs.
        Defaults to plotly.express.colors.qualitative.Dark24.
        Each color is a string in hex format, e.g. '#FD3216'

    Returns
    -------
    dict
        Dictionary with keys:
        - roi2color: dict mapping ROI names to colors
        - color2roi: dict mapping colors to ROI names
    """

    # Prepare roi-to-color mapping
    roi_color_pairs = [
        (roi, cmap[i % len(cmap)]) for i, roi in enumerate(roi_names)
    ]

    # roi-to-color and color-to-roi dicts
    roi2color = {}
    color2roi = {}
    for roi, color in roi_color_pairs:
        roi2color[roi] = color
        color2roi[color] = roi

    return {
        "roi2color": roi2color,
        "color2roi": color2roi,
    }


def get_num_frames(video_path):
    """
    Get the number of frames in a video.

    Parameters
    ----------
    video_path : str
        Path to the video file

    Returns
    -------
    int
        Number of frames in the video
    """
    vidcap = cv2.VideoCapture(video_path)
    return int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))


def extract_frame(
    video_path: str, frame_number: int, output_path: str
) -> None:
    """
    Extract a single frame from a video and save it.

    Parameters
    ----------
    video_path : str
        Path to the video file
    frame_number : int
        Number of the frame to extract
    output_path : str
        Path to the output image file
    """
    print(f"Extracting frame {frame_number} from video {video_path}")
    vidcap = cv2.VideoCapture(video_path)
    vidcap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    success, image = vidcap.read()
    if success:
        cv2.imwrite(output_path, image)
        print(f"Saved frame to {output_path}")
    else:
        print("Error extracting frame from video")


def cache_frame(
    video_path: pl.Path,
    frame_num: int,
    cache_dir: pl.Path = pl.Path.home() / ".WAZP" / "roi_frames",
    frame_suffix: str = "png",
) -> pl.Path:
    """Cache a frame in a .WAZP folder in the home directory.
    This is to avoid extracting the same frame multiple times.

    Parameters
    ----------
    video_path : pl.Path
        Path to the video file
    frame_num : int
        Number of the frame to extract
    cache_dir : pl.Path
        Path to the cache directory
    frame_suffix : str, optional
        Suffix for the frame file, by default ".png"

    Returns
    -------
    pl.Path
        Path to the cached frame .png file
    """

    cache_dir.mkdir(parents=True, exist_ok=True)
    frame_filepath = (
        cache_dir / f"{video_path.stem}_frame-{frame_num}.{frame_suffix}"
    )
    # Extract frame if it is not already cached
    if not frame_filepath.exists():
        extract_frame(
            video_path.as_posix(), frame_num, frame_filepath.as_posix()
        )
    # Remove old frames from cache
    remove_old_frames_from_cache(
        cache_dir, frame_suffix=frame_suffix, keep_last_days=1
    )

    return frame_filepath


def remove_old_frames_from_cache(
    cache_dir: pl.Path, frame_suffix: str = "png", keep_last_days: int = 1
) -> None:
    """Remove all frames from the cache directory that are older
    than keep_last_days days.

    Parameters
    ----------
    cache_dir : pathlib Path
        Path to the cache directory
    frame_suffix : str, optional
        Suffix of the frame files, by default ".png"
    keep_last_days : int, optional
        Number of days to keep, by default 1
    """
    # Get all frame file paths in the cache directory
    cached_frame_paths = [
        cache_dir / file
        for file in cache_dir.iterdir()
        if file.suffix == frame_suffix
    ]
    # Get the time of the oldest frame to keep
    oldest_frame_time = datetime.now() - timedelta(days=keep_last_days)
    # Delete all frames older than the oldest frame to keep
    for frame_path in cached_frame_paths:
        if frame_path.stat().st_mtime < oldest_frame_time.timestamp():
            frame_path.unlink()
    return


def stored_shape_to_table_row(shape: dict) -> dict:
    """Converts a shape, as it is represented in
    roi-storage, to a Dash table row

    Parameters
    ----------
    shape : dict
        Shape dictionary for a single ROI

    Returns
    -------
    dict
        Dictionary with keys:
        - name: ROI name
        - on frame: frame number on which the ROI was last edited
        - path: SVG path for the ROI
    """
    return {
        "name": shape["roi_name"],
        "on frame": shape["drawn_on_frame"],
        "path": shape["path"],
    }


def stored_shape_to_yaml_entry(shape: dict) -> dict:
    """Converts a shape, as it is represented in
    roi-storage, to a dictionary that is meant to be
    written to a yaml file

    Parameters
    ----------
    shape : dict
        Shape dictionary for a single ROI

    Returns
    -------
    dict
        Dictionary with keys:
        - name: ROI name
        - drawn_on_frame: frame number on which the ROI was last edited
        - line_color: color of the ROI edge line
        - path: SVG path for the ROI
    """
    return {
        "name": shape["roi_name"],
        "drawn_on_frame": shape["drawn_on_frame"],
        "line_color": shape["line"]["color"],
        "path": shape["path"],
    }


def yaml_entry_to_stored_shape(roi_entry: dict) -> dict:
    """Converts a single ROI entry from a yaml file to a shape,
    as it is represented in roi-storage

    Parameters
    ----------
    roi_entry : dict
        Dictionary with keys:
        - name: ROI name
        - drawn_on_frame: frame number on which the ROI was last edited
        - line_color: color of the ROI edge line
        - path: SVG path for the ROI

    Returns
    -------
    dict
        Shape dictionary for a single ROI
    """
    return {
        "editable": True,
        "xref": "x",
        "yref": "y",
        "layer": "above",
        "opacity": 1,
        "line": {
            "color": roi_entry["line_color"],
            "width": 4,
            "dash": "solid",
        },
        "fillcolor": "rgba(0, 0, 0, 0)",
        "fillrule": "evenodd",
        "type": "path",
        "path": roi_entry["path"],
        "drawn_on_frame": roi_entry["drawn_on_frame"],
        "roi_name": roi_entry["name"],
    }


def load_rois_from_yaml(yaml_path: pl.Path) -> list:
    """
    Load ROI data from a yaml file

    Parameters
    ----------
    yaml_path : pl.Path
        Path to the yaml file

    Returns
    -------
    list
        List of ROI shape dictionaries bound for roi-storage.
        Empty if no ROIs are found in the yaml file.
    """
    shapes_to_store = []
    if yaml_path.exists():
        with open(yaml_path, "r") as yaml_file:
            metadata = yaml.safe_load(yaml_file)
            if "ROIs" in metadata.keys():
                shapes_to_store = [
                    yaml_entry_to_stored_shape(roi) for roi in metadata["ROIs"]
                ]
            else:
                raise KeyError(f"Could not find key 'ROIs' in {yaml_path}")
    else:
        raise FileNotFoundError(f"Could not find {yaml_path}")

    return shapes_to_store


def are_same_shape(shape0: dict, shape1: dict) -> bool:
    """Checks if two shapes are the same"""
    same_coords = shape0["path"] == shape1["path"]
    same_color = shape0["line"]["color"] == shape1["line"]["color"]
    return same_coords and same_color


def shape_in_list(shape_list: list) -> Callable[[dict], bool]:
    """Checks if a shape is already in a list of shapes"""
    return lambda s: any(are_same_shape(s, s_) for s_ in shape_list)


def shape_drop_custom_keys(shape: dict) -> dict:
    """
    plotly.graph_objects.Figure complains if we include custom
    keys in the shape dictionary, so we remove them here
    """
    new_shape = dict()
    for k in shape.keys() - {"drawn_on_frame", "roi_name"}:
        new_shape[k] = shape[k]
    return new_shape
