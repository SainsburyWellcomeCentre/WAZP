# From tutorial at https://dash.plotly.com/layout
# See also: https://plotly.com/python/plotly-express/#what-about-dash 

# from dash import Dash, dcc, html
import dash
import plotly.express as px # The plotly.express module (usually imported as px) contains functions that can create entire figures at once, https://plotly.com/python/plotly-express/  
import pandas as pd


###############
# Data as a pandas dataframe
df = pd.read_csv(
    'https://gist.githubusercontent.com/chriddyp/5d1ea79569ed194d432e56108a04d188/raw/a9f9e8076b837d541398e999dcbac2b2826a81f8/gdp-life-exp-2007.csv'
    )


####################
# Define figure
# - every plotly figure can be displayed in Dash application passing it to the figure arg of the Graph component
fig = px.scatter(
    df,
    x='gdp per capita',
    y='life expectancy',
    size='population',
    color='continent',
    hover_name='country',
    log_x=True,
    size_max=60
)


###########################
# Define dash app
# initialise
app = dash.Dash(__name__)

# layout
app.layout = dash.html.Div([
    dash.dcc.Graph(id='life-exp-vs-gdp',
                   figure=fig)
])


######################
if __name__ == '__main__':
    app.run_server(debug=True)