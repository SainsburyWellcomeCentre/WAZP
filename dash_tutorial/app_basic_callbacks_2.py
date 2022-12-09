# Dash tutorial: interactive app with simple callbacks -- Filtered data
# https://dash.plotly.com/basic-callbacks 
# On decorators:
# - https://stackoverflow.com/questions/739654/how-do-i-make-function-decorators-and-chain-them-together/1594484#1594484 

from dash import Dash, dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import pdb

# Data as a dataframe
# OJO! Note the dataframe is in the global state of the app and can be read **inside** the callback fns
# (what is the benefit of this tho? less args to pass? a common input for all?)
# ---> Loading data into memory can be expensive, so by doing it at the start of the app we ensure it is done only once (when the app starts)
#      When the user interacts with the app the data is already in memory. 
#      If possible downloading or querying data (is filtering querying?) should be done in the global scope, rather than the callback
#
# ATT! Callbacks should never modify variables outside of their scope!
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv')


## Define app
# initialise app
app = Dash(__name__)

# define layout
# pdb.set_trace()
app.layout = html.Div([
    dcc.Graph(
        id='graph-with-slider'
        ),
    dcc.Slider(
        id='year-slider',
        min=df['year'].min(),
        max=df['year'].max(), 
        step=None,
        value=df['year'].min(),
        marks={str(year): str(year) for year in df['year'].unique()},
        )
])

## Callback
# plot only filtered data ---useful for heatmaps and barplots too!
# ---------------------------------------------------------------------
# ATT! Callbacks should never modify variables outside of their scope!
# ---------------------------------------------------------------------
# - otherwise if a callback modifies a global state, a user's session might affect the next user's session!
# - also when the app is deployed on multiple threads, modifs would not be shared!
# here we make a copy of the dataframe by filtering using pandas
@app.callback(
    Output(component_id='graph-with-slider',component_property='figure'),
    Input(component_id='year-slider',component_property='value'))
def update_figure(selected_year):
    df_filt = df[df.year==selected_year]

    fig = px.scatter(
        df_filt,
        x='gdpPercap',
        y='lifeExp',
        size='pop',
        color='continent',
        hover_name='country',
        log_x=True,
        size_max=55)

    fig.update_layout(transition_duration=500) # transitions allow the chart to update smoothly

    return fig # OJO return figure

if __name__=='__main__':
    app.run_server(debug=True)