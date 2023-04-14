import pathlib as pl
from datetime import datetime, timedelta
from typing import Callable

import cv2
import pandas as pd
import plotly.express as px
import shapely
import yaml
from shapely.geometry import Polygon


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
    """Set a metadata table row's checkbox to True
    when its data is edited.

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

    df_diff = df.merge(df_previous, how="outer", indicator=True).loc[
        lambda x: x["_merge"] == "left_only"
    ]

    # Update the set of selected rows
    list_selected_rows += [
        i for i in df_diff.index.tolist() if i not in list_selected_rows
    ]

    return list_selected_rows


def export_selected_rows_as_yaml(
    data: list[dict], list_selected_rows: list[int], app_storage: dict
) -> None:
    """Export selected metadata rows as yaml files.

    Parameters
    ----------
    data : list[dict]
        a list of dictionaries holding the table data
    list_selected_rows : list[int]
        a list of indices for the currently selected rows
    app_storage : dict
        data held in temporary memory storage,
        accessible to all tabs in the app
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


def read_and_restructure_DLC_dataframe(
    h5_file: str,
) -> pd.DataFrame:
    """Read and reorganise columns in DLC dataframe
    The columns in the DLC dataframe as read from the h5 file are
    reorganised to more closely match a long format.

    The original columns in the DLC dataframe are multi-level, with
    the following levels:
    - scorer: if using the output from a model, this would be the model_str
      (e.g. 'DLC_resnet50_jwasp_femaleandmaleSep12shuffle1_1000000').
    - bodyparts: the keypoints tracked in the animal (e.g., head, thorax)
    - coords: x, y, likelihood

    We reshape the dataframe to have a single level along the columns,
    and the following columns:
    - model_str: string that characterises the model used
      (e.g. 'DLC_resnet50_jwasp_femaleandmaleSep12shuffle1_1000000')
    - frame: the (zero-indexed) frame number the data was tracked at.
      This is inherited from the index of the DLC dataframe.
    - bodypart: the keypoints tracked in the animal (e.g., head, thorax).
      Note we use the singular, rather than the plural as in DLC.
    - x: x-coordinate of the bodypart tracked.
    - y: y-coordinate of the bodypart tracked.
    - likelihood: likelihood of the estimation provided by the model
    The data is sorted by bodypart, and then by frame.

    Parameters
    ----------
    h5_file : str
        path to the input h5 file
    Returns
    -------
    pd.DataFrame
        a dataframe with the h5 file data, and the columns as specified above
    """
    # TODO: can this be less hardcoded?
    # TODO: check with multianimal dataset!

    # read h5 file as a dataframe
    df = pd.read_hdf(h5_file)

    # determine if model is multianimal
    is_multianimal = "individuals" in df.columns.names

    # assuming the DLC index corresponds to frame number!!!
    # TODO: can I check this?
    # frames are zero-indexed
    df.index.name = "frame"

    # stack scorer and bodyparts levels from columns to index
    # if multianimal, also column 'individuals'
    columns_to_stack = ["scorer", "bodyparts"]
    if is_multianimal:
        columns_to_stack.append("individual")
    df = df.stack(level=columns_to_stack)  # type: ignore
    # Not sure why mypy complains, list of labels is allowed
    # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.stack.html
    # ignoring for now

    # reset index to remove 'frame','scorer' and 'bodyparts'
    # if multianimal, also remove 'individuals'
    df = df.reset_index()  # removes all levels in index by default

    # reset name of set of columns and indices
    # (to remove columns name = 'coords')
    df.columns.name = ""
    df.index.name = ""

    # rename columns
    # TODO: if multianimal, also 'individuals'
    columns_to_rename = {
        "scorer": "model_str",
        "bodyparts": "bodypart",
    }
    if is_multianimal:
        columns_to_rename["individuals"] = "individual"
    df.rename(
        columns=columns_to_rename,
        inplace=True,
    )

    # reorder columns
    list_columns_in_order = [
        "model_str",
        "frame",
        "bodypart",
        "x",
        "y",
        "likelihood",
    ]
    if is_multianimal:
        # insert 'individual' in second position
        list_columns_in_order.insert(1, "individual")
    df = df[list_columns_in_order]

    # sort rows by bodypart and frame
    # if multianimal: sort by individual first
    list_columns_to_sort_by = ["bodypart", "frame"]
    if is_multianimal:
        list_columns_to_sort_by.insert(0, "individual")
    df.sort_values(by=list_columns_to_sort_by, inplace=True)  # type: ignore

    # reset dataframe index
    df = df.reset_index(drop=True)

    return df  # type: ignore


def get_dataframes_to_combine(
    list_selected_videos: list,
    slider_start_end_labels: list,
    app_storage: dict,
) -> list:
    """Create list of dataframes to export as one

    Parameters
    ----------
    list_selected_videos : list
        list of videos selected in the table
    slider_start_end_labels : list
        labels for the slider start and end positions
    app_storage : dict
        data held in temporary memory storage,
        accessible to all tabs in the app

    Returns
    -------
    list_df_to_export : list
        list of dataframes to concatenate
        before exporting
    """
    # TODO: allow model_str to be a list?
    # (i.e., consider the option of different models being used)

    # List of h5 files corresponding to
    # the selected videos
    list_h5_file_paths = [
        pl.Path(app_storage["config"]["pose_estimation_results_path"])
        / (pl.Path(vd).stem + app_storage["config"]["model_str"] + ".h5")
        for vd in list_selected_videos
    ]

    # Read the dataframe for each video and h5 file
    list_df_to_export = []
    for h5, video in zip(list_h5_file_paths, list_selected_videos):

        # Get the metadata file for this video
        # (built from video filename)
        yaml_filename = pl.Path(app_storage["config"]["videos_dir_path"]) / (
            pl.Path(video).stem + ".metadata.yaml"
        )
        with open(yaml_filename, "r") as yf:
            metadata = yaml.safe_load(yf)

        # Extract frame start/end using info from slider
        frame_start_end = [
            metadata["Events"][x] for x in slider_start_end_labels
        ]

        # -----------------------------

        # Read h5 file and reorganise columns
        # TODO: I assume index in DLC dataframe represents frame number
        # (0-indexed) -- check this with download from ceph and ffmpeg
        df = read_and_restructure_DLC_dataframe(h5)

        # Extract subset of rows based on events slider
        # (frame numbers from slider, both inclusive)
        df = df.loc[
            (df["frame"] >= frame_start_end[0])
            & (df["frame"] <= frame_start_end[1]),
            :,
        ]

        # -----------------------------
        # Add video file column
        # (insert after model_str)
        df.insert(1, "video_file", video)

        # Add ROI per frame and bodypart,
        # if ROIs defined for this video
        # To set hierarchy of ROIs:
        # - Start assigning from the smallest,
        # - only set ROI if not previously defined
        # TODO: Is there a better approach?
        df["ROI_tag"] = ""  # initialize ROI column with empty strings
        if "ROIs" in metadata:
            # Extract ROI paths for this video if defined
            # TODO: should I do case insensitive?
            # if "rois" in [ky.lower() for ky in metadata.keys()]:
            ROIs_as_polygons = {
                el["name"]: svg_path_to_polygon(el["path"])
                for el in metadata["ROIs"]
            }
            df = add_ROIs_to_video_dataframe(df, ROIs_as_polygons, app_storage)

        # Add Event tags if defined
        # - if no event is defined for that frame: empty str
        # - if an event is defined for that frame: event_tag
        df["event_tag"] = ""
        if "Events" in metadata:
            for event_str in metadata["Events"].keys():
                event_frame = metadata["Events"][event_str]
                df.loc[df["frame"] == event_frame, "event_tag"] = event_str

        # Append to list
        list_df_to_export.append(df)

    return list_df_to_export


def svg_path_to_polygon(svg_path: str) -> Polygon:
    """Converts an SVG Path that describes a closed
    polygon into a Shapely polygon.

    The svg_path string starts with 'M' (initial point),
    indicates end of intermediate line segments with 'L'
    and marks the end of the string with 'Z' (end of path)
    (see [1]).

    Based on original function by @niksirbi

    References
    ----------
    [1] "SVG Path",
        https://developer.mozilla.org/en-US/docs/Web/SVG/Tutorial/Paths
    """

    # strip svg_path of initial and end marks
    svg_path_no_ends = svg_path.lstrip("M").rstrip("Z")

    # extract points as x,y tuples
    list_points = [
        tuple(float(s) for s in tuple_str.split(","))
        for tuple_str in svg_path_no_ends.split("L")
    ]

    return Polygon(list_points)


def add_ROIs_to_video_dataframe(
    df: pd.DataFrame, ROIs_as_polygons: dict, app_storage: dict
) -> pd.DataFrame:
    """Assign an ROI to every row in the dataframe
    of the current video. Every row corresponds to a keypoint at a
    specific frame.

    If no ROIs are defined for this video, an empty string
    is assigned to all rows.

    To solve for the cases in which a point falls in two or more ROIs
    (e.g. because one ROI contains or intersects another), we also define
    a hierarchy of ROIs.

    By default the hierarchy of ROIs is based on their area (a smaller ROI
    prevails over a larger one). However, if in the project config the
    parameter 'use_ROIs_order_as_hierarchy' is defined and set as True, the
    order of the ROIs in the project config file will be interpreted as their
    hierarchy, with top ROIs prevailing over ROIs placed below.

    Parameters
    ----------
    df : pd.Dataframe
        pandas dataframe with the pose estimation results
        for one video. It is a single-level dataframe, restructured
        from the DeepLabCut output.
    ROIs_as_polygons : dict
        dictionary for the current video with ROI tags as keys,
        and their corresponding shapely polygons as values.
    app_storage : dict
        data held in temporary memory storage,
        accessible to all tabs in the app

    Returns
    -------
    df : pd.Dataframe
        pandas dataframe with the pose estimation results
        for one video, and the ROI per bodypart per frame
        assigned.
    """

    # Define hierarchy of ROIs
    flag_use_ROI_custom_order = app_storage["config"].get(
        "use_ROIs_order_as_hierarchy", False  # reads a bool
    )

    # Use order of ROIs in the project config file
    # as hierarchy if required
    if flag_use_ROI_custom_order:

        # sort pairs of ROI tags and polygons
        # in the same order as the ROI tags appear in
        # the config file
        list_sorted_ROI_pairs = [
            x
            for x, _ in sorted(
                zip(
                    ROIs_as_polygons.items(),
                    enumerate(app_storage["config"]["ROI_tags"]),
                ),
                key=lambda pair: pair[1][0],  # sort by index from enumerate
            )
        ]

    # else: sort pairs of ROI tags and polygons
    # based on the polygons' areas
    else:
        list_sorted_ROI_pairs = sorted(
            ROIs_as_polygons.items(),
            key=lambda pair: pair[1].area,  # sort by increasing area
        )

    # -------------------
    # Assign ROIs
    for ROI_str, ROI_poly in list_sorted_ROI_pairs:
        # for optimized performance
        # (applies transform in place)
        shapely.prepare(ROI_poly)

        # Consider buffer around boundaries if required
        # TODO: remove this buffer option? inspired by this SO answer
        # https://stackoverflow.com/a/59033011
        if "buffer_around_ROIs_boundaries" in app_storage["config"]:
            ROI_poly = ROI_poly.buffer(
                float(app_storage["config"]["buffer_around_ROIs_boundaries"])
            )

        # select rows with x,y coordinates inside ROI (including boundary)
        select_rows_in_ROI = shapely.intersects_xy(
            ROI_poly, [(x, y) for (x, y) in zip(df["x"], df["y"])]
        )

        # select rows with no ROI assigned
        select_rows_w_empty_str = df["ROI_tag"] == ""

        # assign ROI
        df.loc[
            select_rows_in_ROI & select_rows_w_empty_str, "ROI_tag"
        ] = ROI_str

    return df


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


def get_num_frames(video_path) -> int:
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
    vidcap = cv2.VideoCapture(video_path, apiPreference=cv2.CAP_FFMPEG)
    num_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    if num_frames < 1:
        raise RuntimeError(
            f"Could not read from '{video_path}'. "
            "Is this a valid video file?"
        )
    return num_frames


def extract_frame(video_path: str, frame_idx: int, output_path: str) -> None:
    """
    Extract a single frame from a video and save it.

    Parameters
    ----------
    video_path : str
        Path to the video file
    frame_idx : int
        Index of the frame to extract
    output_path : str
        Path to the output image file
    """
    print(f"Extracting frame {frame_idx} from video {video_path}")

    vidcap = cv2.VideoCapture(video_path, apiPreference=cv2.CAP_FFMPEG)
    vidcap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
    success, image = vidcap.read()
    if success:
        cv2.imwrite(output_path, image)
        print(f"Saved frame {frame_idx} to {output_path}")
    else:
        raise RuntimeError(
            f"Could not extract frame {frame_idx} from {video_path}."
        )


def cache_frame(
    video_path: pl.Path,
    frame_idx: int,
    cache_dir: pl.Path = pl.Path.home() / ".WAZP" / "roi_frames",
    frame_suffix: str = "png",
) -> pl.Path:
    """Cache a frame in a .WAZP folder in the home directory.
    This is to avoid extracting the same frame multiple times.

    Parameters
    ----------
    video_path : pl.Path
        Path to the video file
    frame_idx : int
        Index of the frame to extract
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
        cache_dir / f"{video_path.stem}_frame-{frame_idx}.{frame_suffix}"
    )
    # Extract frame if it is not already cached
    if not frame_filepath.exists():
        extract_frame(
            video_path.as_posix(), frame_idx, frame_filepath.as_posix()
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
            if "ROIs" in metadata:
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
