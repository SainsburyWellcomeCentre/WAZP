# Define the page's content within a variable called layout or 
# a function called layout that returns the content.

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd


###############
# Register this page
dash.register_page(__name__)


###############
# Define table component from pandas dataframe
df = pd.read_csv(
    "https://gist.githubusercontent.com/chriddyp/c78bf172206ce24f77d6363a2d754b59/raw/c353e8ef842413cae56ae3920b8fd78468aa4cb2/usa-agricultural-exports-2011.csv"
)

table = dbc.Table.from_dataframe(
    df,
    bordered=True, #dark=True, #deprecated µ~~~~ñ~~~ññ
    hover=True,
    responsive=True, # if True, table can be scrolled horizontally?
    striped=True # applies zebra striping to the rows
    )


########################
# Define layout
layout = html.Div(
    children=[
        html.H1(children="Metadata"),
        html.Div(
            #children=""" This is the Metadata page content."""
            dbc.Container(table, className="p-5")
        ),
    ]
)
