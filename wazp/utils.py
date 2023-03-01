import pathlib as pl

import pandas as pd
import yaml
from dash import dash_table


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
        if str(f).endswith("metadata.yaml")
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
                "hideable": True,
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
            "maxWidth": 300,
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
