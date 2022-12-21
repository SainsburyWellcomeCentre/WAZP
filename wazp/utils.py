

import pathlib as pl 

from dash import html, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import yaml

import pdb

def df_from_metadata_yaml_files(parent_dir):
    '''
    Build a dataframe from all the metadata.yaml files in the input parent directory.

    '''
    # TODO: refactor, I think it could be more compact
    # TODO: this was the previous approach with json, can I do it as compact?
    # read_fn = lambda x: pd.read_json(os.path.join(parent_dir, x), orient="index")
    # df = pd.concat(map(read_fn, list_metadata_files), ignore_index=True, axis=1)

    list_metadata_files = [
        str(yl) for yl in pl.Path(parent_dir).iterdir() 
        if str(yl).endswith('.yaml') #'---
        ]

    list_df_metadata = []
    for yl in list_metadata_files:
        with open(yl) as f: 
            list_df_metadata.append(
                pd.DataFrame.from_dict(yaml.safe_load(f), orient="index")
            )

    return pd.concat(
        list_df_metadata, ignore_index=True, axis=1
    ).T  # TODO can I avoid transpose ?



def metadata_tbl_component_from_df(df):
    '''
    Build a table component for the Dash/Plotly app populated with input dataframe
    '''
    ###########################
    # Using bootstrap components
    # table = dbc.Table.from_dataframe(
    #     df, #df_from_metadata_yaml_files(parent_dir),
    #     bordered=True,
    #     hover=False,  # True
    #     responsive=True,  # if True, table can be scrolled horizontally?
    #     striped=True,  # applies zebra striping to the rows
    #     size="sm",
    #     style={
    #         "width": "100%",
    #     }, # TODO: check table style options (see Table class)
    # )

    #########################
    # Using dash table
    table = dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[{
            'id': c, 
            'name': c, 
            'hideable': True,
            'editable': False if c == 'File' else True,
            'presentation':'input'} for c in df.columns],
        page_size=25,  
        page_action='native',
        fixed_rows={'headers':True}, # fix table header when scrolling vertically
        fixed_columns={'headers':True, 'data':1}, # fix File column when scrolling horizontally
        sort_action='native',
        sort_mode='single', # if 'multi': sorting can be performed across multiple columns (e.g. sort by country, sort within each country)
        tooltip_header= { 
            i: {'value':i} for i in df.columns
            }, #{'type':'markdown', 'value':{i for i in df.columns}},
        tooltip_data= [
            {row_key: {'value': str(row_val), 'type':'markdown'} for row_key,row_val in row_dict.items()} 
            for row_dict in df.to_dict('records')
        ],   
        style_header={
            'backgroundColor': 'rgb(210, 210, 210)',
            'color': 'black',
            'fontWeight': 'bold',
            'textAlign': 'left',
            'fontFamily': "Helvetica", # "'Open Sans', verdana, arial, sans-serif",
        },
        style_table={
            'height': '720px', #'100%---with 100% seems roughly 500px, #
            'maxHeight': '720px', # css overwrites the table height when fixed_rows is enabled; setting height and maxHeight to the same value seems a quick hack to fix it (see https://community.plotly.com/t/setting-datatable-max-height-when-using-fixed-headers/26417/10)
            'width': '100%',
            'maxWidth': '100%',
            'overflowY': 'scroll',
            'overflowX': 'scroll',},
        style_cell={ # all cells
            'textAlign': 'left',
            'padding': 7,
            'minWidth': 70,
            'width': 175,
            'maxWidth': 300, #200
            'fontFamily': "Helvetica", # "'Open Sans', verdana, arial, sans-serif",
        },
        style_data={ # data cells are all cells except header and filter cells
            'color': 'black',
            'backgroundColor': 'white',
            'overflow':'hidden',
            'textOverflow': 'ellipsis',
        }, 
        style_header_conditional=[
            {
                'if': {'column_id': 'File'},
                'backgroundColor': 'rgb(200, 200, 400)', # darker blue
            }
        ],
        style_data_conditional=[
            {
                'if': {'column_id': 'File','row_index': 'odd'},
                'backgroundColor': 'rgb(220, 220, 420)', # darker blue
            },
            {
                'if': {'column_id': 'File','row_index': 'even'},
                'backgroundColor': 'rgb(235, 235, 255)', # lighter blue
            },
            {
                'if': {'column_id': [c for c in df.columns if c != 'File'], 'row_index': 'odd'},
                'backgroundColor': 'rgb(240, 240, 240)', # gray
            }
        ],

    )

    # table = dash_table.DataTable(
    #     data=df.to_dict('records'), # return df as a list of dicts, one dict for each row (index) with keys=columns, and values=cell values
    #     columns=[{
    #         'id': c, 
    #         'name': c, 
    #         'hideable': True,
    #         'editable': False if c == 'File' else True,
    #         'presentation':'markdown'} for c in df.columns],
    #     # page_size=100, # number of entries per page
    #     # page_action='native',
    #     fixed_columns={'headers':True, 'data':1}, # fix File column when scrolling horizontally
    #     fixed_rows={'headers':True, 'data':0}, # fix table header when scrolling vertically
    #     sort_action='native',
    #     sort_mode='single', # if 'multi': sorting can be performed across multiple columns (e.g. sort by country, sort within each country)
    #     tooltip_header= { 
    #         i: {'value':i} for i in df.columns
    #         }, #{'type':'markdown', 'value':{i for i in df.columns}},
    #     tooltip_data= [
    #         {row_key: {'value': str(row_val), 'type':'markdown'} for row_key,row_val in row_dict.items()} 
    #         for row_dict in df.to_dict('records')
    #     ],
    #     style_table={ # CSS styles
    #         'width':'100%', # approx 40px per row?
    #         'overflowY':'auto',
    #     },
    #     style_cell={
    #         'textAlign': 'left',
    #         'overflow':'hidden',
    #         'textOverflow': 'ellipsis',
    #         'maxWidth': 200
    #     },
    #     style_data={ # data cells are all cells except header and filter cells
    #         'color': 'black',
    #         'backgroundColor': 'white'
    #     }, 
    #     style_data_conditional=[
    #         {
    #             'if': {'row_index': 'odd'},
    #             'backgroundColor': 'rgb(220, 220, 220)',
    #         }
    #     ],
    #     style_header={
    #         'backgroundColor': 'rgb(210, 210, 210)',
    #         'color': 'black',
    #         'fontWeight': 'bold'
    #     }
    # ) 
    
    return table # dbc.Container(table, className="p-5") #