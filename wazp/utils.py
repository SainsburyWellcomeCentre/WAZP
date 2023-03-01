import math
import pathlib as pl

import pandas as pd
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
                        {k: [v] for k, v in yaml.safe_load(ylf).items()},
                        orient="columns",
                    )
                )

        return pd.concat(list_df_metadata, ignore_index=True)


def metadata_table_component_from_df(df: pd.DataFrame) -> dash_table.DataTable:
    """Build a Dash table component populated with the input dataframe.

    Parameters
    ----------
    df : pd.DataFrame
        input dataframe

    Returns
    -------
    dash_table.DataTable
        dash table component built from input dataframe
    """

    # Change format of columns with string 'date' in their name from string to
    # datetime
    # (this is to allow sorting in the Dash table)
    # TODO: review this, is there a more failsafe way?
    list_date_columns = [
        col for col in df.columns.tolist() if "date" in col.lower()
    ]
    for col in list_date_columns:
        df[col] = pd.to_datetime(df[col]).dt.strftime("%Y-%m-%d")

    # dash table component
    table = dash_table.DataTable(
        id="metadata-table",
        data=df.to_dict("records"),
        data_previous=None,
        selected_rows=[],
        columns=[
            {
                "id": c,
                "name": c,
                "hideable": (True if c != "File" else False),
                "editable": True,
                "presentation": "input",
            }
            for c in df.columns
        ],
        css=[
            {
                "selector": ".dash-spreadsheet td div",
                "rule": """
                    max-height: 20px; min-height: 20px; height: 20px;
                    line-height: 15px;
                    display: block;
                    overflow-y: hidden;
                    """,
            }
        ],  # to fix issue of different cell heights if row is empty;
        # see https://dash.plotly.com/datatable/width#wrapping-onto-multiple-lines-while-constraining-the-height-of-cells # noqa
        row_selectable="multi",
        page_size=25,
        page_action="native",
        fixed_rows={"headers": True},
        # fix header when scrolling vertically
        fixed_columns={"headers": True, "data": 1},
        # fix first column when scrolling laterally
        sort_action="native",
        sort_mode="single",
        tooltip_header={i: {"value": i} for i in df.columns},
        tooltip_data=[
            {
                row_key: {"value": str(row_val), "type": "markdown"}
                for row_key, row_val in row_dict.items()
            }
            for row_dict in df.to_dict("records")
        ],
        style_header={
            "backgroundColor": "rgb(210, 210, 210)",
            "color": "black",
            "fontWeight": "bold",
            "textAlign": "left",
            "fontFamily": "Helvetica",
        },
        style_table={
            "height": "720px",
            "maxHeight": "720px",
            # css overwrites the table height when fixed_rows is enabled;
            # setting height and maxHeight to the same value seems a quick
            # hack to fix it
            # (see https://community.plotly.com/t/setting-datatable-max-height-when-using-fixed-headers/26417/10) # noqa
            "width": "100%",
            "maxWidth": "100%",
            "overflowY": "scroll",
            "overflowX": "scroll",
        },
        style_cell={  # refers to all cells (the whole table)
            "textAlign": "left",
            "padding": 7,
            "minWidth": 70,
            "width": 175,
            "maxWidth": 450,
            "fontFamily": "Helvetica",
        },
        style_data={  # refers to data cells (all except header and filter)
            "color": "black",
            "backgroundColor": "white",
            "overflow": "hidden",
            "textOverflow": "ellipsis",
        },
        style_header_conditional=[
            {
                "if": {"column_id": "File"},
                # TODO: consider getting file from app_storage
                "backgroundColor": "rgb(200, 200, 400)",
            }
        ],
        style_data_conditional=[
            {
                "if": {"column_id": "File", "row_index": "odd"},
                "backgroundColor": "rgb(220, 220, 420)",  # darker blue
            },
            {
                "if": {"column_id": "File", "row_index": "even"},
                "backgroundColor": "rgb(235, 235, 255)",  # lighter blue
            },
            {
                "if": {
                    "column_id": [c for c in df.columns if c != "File"],
                    "row_index": "odd",
                },
                "backgroundColor": "rgb(240, 240, 240)",  # gray
            },
        ],
    )

    return table


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
    # TODO: alternative to h5: pickle? csv?
    # TODO: try to make it generic to any pose estim library?
    # (right now DLC)
    list_h5_file_paths = [
        pl.Path(app_storage["config"]["pose_estimation_results_path"])
        / pl.Path(
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
        yaml_filename = pl.Path(
            app_storage["config"]["videos_dir_path"]
        ) / pl.Path(pl.Path(video).stem + ".metadata.yaml")

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

        # read h5 as dataframe and add 'File' row
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
