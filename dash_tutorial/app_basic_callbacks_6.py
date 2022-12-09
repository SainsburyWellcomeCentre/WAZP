# Dash tutorial: Callbacks -- State
# To pass along extra input values without firing the callbacks
# --> some (input) components are 'state' and a button component is 'Input'
# https://dash.plotly.com/basic-callbacks

from dash import Dash, dcc, html, Input, Output, State
import pandas as pd
import plotly.express as px

# import pdb


#############################
## Define app
# initialise app
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = Dash(__name__, external_stylesheets=external_stylesheets)

# define layout
app.layout = html.Div(
    [
        dcc.Input(id='text-input-1', type='text', value='patata'),
        dcc.Input(id='text-input-2', type='text', value='tomate'),
        html.Button(id='submit-button', n_clicks=0, children='Submit vegetable'),
        html.Div(id='output-state')
    ]
)


#############################
## Callback
# - Bc text boxes are marked as 'State', changing their input won't trigger anything but clicking the button will
# - The 'state' values are passed to the callback even if they dont trigger the fn
# - OJO! The trigger is the number of clicks on the button! when that changes the callback is triggered
#   (it is available in every Dash HTML component)
@app.callback(
    Output('output-state', 'children'),
    State('text-input-1', 'value'), # STATE!
    State('text-input-2', 'value'), # STATE! ---order between inputs and state doesnt matter, as long as it matches wrapped fn?
    Input('submit-button', 'n_clicks'), 
)
def update_output_text(
    text_str_1,
    text_str_2,
    n_clicks,
):
    return f'Input 1 is {text_str_1}, input 2 is {text_str_2} and the button has been clicked {n_clicks} times'

###################
## Driver
if __name__ == "__main__":
    app.run_server(debug=True)
