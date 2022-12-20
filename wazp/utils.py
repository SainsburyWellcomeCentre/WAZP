

import pathlib as pl 


import dash_bootstrap_components as dbc
import pandas as pd
import yaml



def df_from_metadata_yaml_files(parent_dir):
    '''
    Build a dataframe from all the metadata.yaml files in the input parent directory.

    '''
    # TODO: refactor, I think it could be more compact (see below)

    list_metadata_files = [
        str(yl) for yl in pl.Path(parent_dir).iterdir() 
        if str(yl).endswith('metadata.yaml')
        ]

    list_df_metadata = []
    for yl in list_metadata_files:
        with open(pl.Path(parent_dir) / yl) as f: # with open(os.path.join(parent_dir, yl)) as f:
            list_df_metadata.append(
                pd.DataFrame.from_dict(yaml.safe_load(f), orient="index")
            )

    return pd.concat(
        list_df_metadata, ignore_index=True, axis=1
    ).T  # TODO review why transpose required


# TODO: this was the previous approach with json, can I do it as compact?
# read_fn = lambda x: pd.read_json(os.path.join(parent_dir, x), orient="index")
# df = pd.concat(map(read_fn, list_metadata_files), ignore_index=True, axis=1)


def generate_tbl_component_from_df(df):
    '''
    Build a table component for the Dash/Plotly app populated with input dataframe
    '''
    # ##########################
    # Using html dash components
    # dataframe = df_from_metadata_yaml_files(parent_dir)
    # table = html.Table(
    #     children =
    #     [ # define table head?
    #        html.Thead(html.Tr([html.Th(col, style={'width':'15%'})
    #                               for col in dataframe.columns])),
    #        # define table body
    #        html.Tbody(
    #            [
    #               html.Tr(
    #                 [
    #                   html.Td(dataframe.iloc[i][col], style={'width':'15%'})
    #                   for col in dataframe.columns
    #                  ]
    #                 )
    #                 #range(min(len(dataframe), max_rows))
    #                 for i in range(len(dataframe))
    #             ]
    #         ),
    #     ],
    #     style={'width':'100%',}
    # )
    #########

    # Using bootstrap components
    table = dbc.Table.from_dataframe(
        df, #df_from_metadata_yaml_files(parent_dir),
        bordered=True,
        hover=False,  # True
        responsive=True,  # if True, table can be scrolled horizontally?
        striped=True,  # applies zebra striping to the rows
        size="sm",
        style={
            "width": "100%",
        }, # TODO: check table style options (see Table class)
    )

    return dbc.Container(table, className="p-5")