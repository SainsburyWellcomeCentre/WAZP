# Dash tutorial: interactive app with simple callbacks -- Multiple outputs
# https://dash.plotly.com/basic-callbacks
# On decorators:
# - https://stackoverflow.com/questions/739654/how-do-i-make-function-decorators-and-chain-them-together/1594484#1594484

from dash import Dash, dcc, html, Input, Output
import pandas as pd
import plotly.express as px

# import pdb


# Data as a dataframe
# OJO! Note the dataframe is in the global state of the app and can be read **inside** the callback fns
# (what is the benefit of this tho? less args to pass? a common input for all?)
# ---> Loading data into memory can be expensive, so by doing it at the start of the app we ensure it is done only once (when the app starts)
#      When the user interacts with the app the data is already in memory.
#      If possible downloading or querying data (is filtering querying?) should be done in the global scope, rather than the callback
#
# ATT! Callbacks should never modify variables outside of their scope!

####################
# Data
# Column names: ['Country Name', 'Indicator Name', 'Year', 'Value']
# Indicators:
# array(['Agriculture, value added (% of GDP)',
#        'CO2 emissions (metric tons per capita)',
#        'Domestic credit provided by financial sector (% of GDP)',
#        'Electric power consumption (kWh per capita)',
#        'Energy use (kg of oil equivalent per capita)',
#        'Exports of goods and services (% of GDP)',
#        'Fertility rate, total (births per woman)',
#        'GDP growth (annual %)',
#        'Imports of goods and services (% of GDP)',
#        'Industry, value added (% of GDP)',
#        'Inflation, GDP deflator (annual %)',
#        'Life expectancy at birth, total (years)',
#        'Population density (people per sq. km of land area)',
#        'Services, etc., value added (% of GDP)'], dtype=object)
df = pd.read_csv("https://plotly.github.io/datasets/country_indicators.csv")

#############################
## Define app
# initialise app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(
    __name__,
    external_stylesheets=external_stylesheets)

# define layout
# pdb.set_trace()
app.layout = html.Div(
    [
        dcc.Input(
            id='num-multi',
            type='number',
            value=2.0
        ),
        html.Table(
            [
                html.Tr([html.Td(['x', html.Sup(2)]), html.Td(id='square')]),
                html.Tr([html.Td(['x', html.Sup(3)]), html.Td(id='cube')]),
                html.Tr([html.Td([2, html.Sup('x')]), html.Td(id='twos')]),
                html.Tr([html.Td([3, html.Sup('x')]), html.Td(id='threes')]),
                html.Tr([html.Td(['x', html.Sup('x')]), html.Td(id='x^x')])

            ])
    ])





####################
## Callback with multiple outputs
# - return as many objects as outputs in the decorator
# - OJO! It's not always a good idea to combine outputs
#   - keeping them separate can prevent unnecessary updates
#   - if computations for the diff outputs are very diff, we may be able to run them in parallel if callbacks are separate
@app.callback(
    Output('square','children'),
    Output('cube','children'),
    Output('twos','children'),
    Output('threes','children'),
    Output('x^x','children'),
    Input('num-multi','value')
)
def callback_a(x):
    return x**2.0, x**3.0, 2.0**x, 3.0**x, x**x


###################
## Driver
if __name__ == "__main__":
    app.run_server(debug=True)
