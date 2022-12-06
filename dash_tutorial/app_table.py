# From dash tutorial at https://dash.plotly.com/layout

from dash import Dash, html  # html holds wrappers for HTML components
import pandas as pd

############
# Fn to generate table
# HTML tags
# - Tr element defines a row of cells in a table
#   - Th element defines header cell element (in a row)
#   - Td element defines a data cell element (in a row) https://developer.mozilla.org/en-US/docs/Web/HTML/Element/tr 
def generate_table(dataframe, max_rows=10):

    return html.Table(
        [  # define table head?
            html.Thead(html.Tr([html.Th(col) for col in dataframe.columns])), 
            # define table body?--with a list of lists (each row is a list of elements, we pass a list of rows?)
            html.Tbody(
                [
                    html.Tr(
                        [
                            html.Td(dataframe.iloc[i][col])
                            for col in dataframe.columns
                        ]
                    )
                    for i in range(min(len(dataframe), max_rows))
                ]
            ),
        ]
    )


###########################
# Import data as a dataframe
df = pd.read_csv(
    "https://gist.githubusercontent.com/chriddyp/c78bf172206ce24f77d6363a2d754b59/raw/c353e8ef842413cae56ae3920b8fd78468aa4cb2/usa-agricultural-exports-2011.csv"
)

########################
## Define app
# initialise
app = Dash(__name__)

# define layout
app.layout = html.Div([
    html.H4(children="US Agriculture Exports (2011)"), 
    generate_table(df)
])


######################
if __name__=='__main__':
    app.run_server(debug=True)