import pathlib as pl

import pandas as pd
import yaml
from dash import dash_table


def df_from_metadata_yaml_files(parent_dir, metadata_fields_dict):
    """
    Build a dataframe from all the metadata.yaml files in the input parent
    directory. If there are no metadata.yaml files, make a dataframe with
    the columns as in metadata_fields_dict and empty (string) fields

    """
    # TODO: refactor, I think it could be more compact
    # TODO: this was the previous approach with json, can I do it as compact?
    # read_fn = lambda x: pd.read_json(os.path.join(parent_dir, x),
    #   orient="index")
    # df = pd.concat(map(read_fn, list_metadata_files),
    #   ignore_index=True, axis=1)

    # Compute list of metadata files in parentdir
    list_metadata_files = [
        str(f)
        for f in pl.Path(parent_dir).iterdir()
        if str(f).endswith("metadata.yaml")  # '---
    ]

    # If there are no metadata files: build table from metadata_fields_dict
    if not list_metadata_files:
        return pd.DataFrame.from_dict(
            [{c: "" for c in metadata_fields_dict.keys()}],
            # because we are passing only one row, wrap in a list
            orient="columns",
        )
    # If there are metadata files: build table from those yaml files
    else:
        list_df_metadata = []
        for yl in list_metadata_files:
            with open(yl) as ylf:
                list_df_metadata.append(
                    pd.DataFrame.from_dict(
                        [yaml.safe_load(ylf)], orient="columns"
                    )
                )

        return pd.concat(list_df_metadata, ignore_index=True)


def metadata_tbl_component_from_df(df):
    """
    Build a table component for the Dash/Plotly app populated
    with input dataframe
    """
    # Change format of date fields in dataframe
    list_date_columns = [col for col in df.columns if "date" in col.lower()]
    for col in list_date_columns:
        df[col] = pd.to_datetime(df[col]).dt.strftime("%Y-%m-%d")

    # Using dash table
    table = dash_table.DataTable(
        id="metadata-table",
        data=df.to_dict("records"),
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
        # see https://dash.plotly.com/datatable/width#wrapping-onto-
        # multiple-lines-while-constraining-the-height-of-cells
        row_selectable="multi",
        page_size=25,
        page_action="native",
        fixed_rows={"headers": True},  # fix header w/ vert scrolling
        fixed_columns={"headers": True, "data": 1},  # fix 'File' column
        sort_action="native",
        sort_mode="single",  # if 'multi': sorting across multiple columns
        # (e.g. sort by country, sort within each country)
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
            # "'Open Sans', verdana, arial, sans-serif",
        },
        style_table={
            "height": "720px",
            "maxHeight": "720px",
            # css overwrites the table height when fixed_rows is enabled;
            # setting height and maxHeight to the same value seems a quick
            # hack to fix it
            # (see https://community.plotly.com/t/
            # setting-datatable-max-height-when-using-fixed-headers/26417/10)
            "width": "100%",
            "maxWidth": "100%",
            "overflowY": "scroll",
            "overflowX": "scroll",
        },
        style_cell={  # all cells (the whole table)
            "textAlign": "left",
            "padding": 7,
            "minWidth": 70,
            "width": 175,
            "maxWidth": 300,  # 200
            "fontFamily": "Helvetica",
            # "'Open Sans', verdana, arial, sans-serif",
        },
        style_data={  # data cells (all cells except header and filter cells)
            "color": "black",
            "backgroundColor": "white",
            "overflow": "hidden",
            # 'lineHeight': '10px',
            "textOverflow": "ellipsis",
        },
        style_header_conditional=[
            {
                "if": {"column_id": "File"},
                "backgroundColor": "rgb(200, 200, 400)",  # darker blue
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

    return table  # dbc.Container(table, className="p-5")
