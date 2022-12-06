# From dash tutorial at https://dash-bootstrap-components.opensource.faculty.ai/docs/components/table/
# Available themes:
#  https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/#available-themes
#  https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/explorer/

from dash import Dash, html  # html holds wrappers for HTML components
import dash_bootstrap_components as dbc
import pandas as pd

########################
### Define table manually
#
# Table header
# a header is a table row, made from a list of header cells
table_header = [
    html.Thead(html.Tr([html.Th("First name"), html.Th("Last Name")]))
]

# Table body
# - a table row is a list of data cells
# row1 = html.Tr([html.Td('Pepe'), html.Td('Perez')]) #
# row2 = html.Tr([html.Td('Fernando'), html.Td('Fernandez')])
# row3 = html.Tr([html.Td('Zacarias'), html.Td('Zapata')])

# table_body = [html.Tbody([row1, row2, row3])]
table_body = [
    html.Tbody(
        [
            html.Tr([html.Td("Pepe"), html.Td("Perez")]),
            html.Tr([html.Td("Fernando"), html.Td("Fernandez")]),
            html.Tr([html.Td("Zacarias"), html.Td("Zapata")]),
        ]
    )
]

# Assemble table component
table0 = dbc.Table(
    children = table_header + table_body, # concatenate lists
    bordered=True,
    hover=True,
    responsive=True,
    striped=True)
##################################
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
## Define app
# initialise
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],  # link to a Bootstrap stylesheet
)

# define layout
app.layout = dbc.Container(table, className="p-5")


######################
if __name__ == "__main__":
    app.run_server(debug=True)
