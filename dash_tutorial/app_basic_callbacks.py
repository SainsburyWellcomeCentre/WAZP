# Dash tutorial: interactive app with simple callbacks
# https://dash.plotly.com/basic-callbacks 
# On decorators:
# - https://stackoverflow.com/questions/739654/how-do-i-make-function-decorators-and-chain-them-together/1594484#1594484 

from dash import Dash, dcc, html, Input, Output


# initialise app
app = Dash(__name__)

# define layout
app.layout = html.Div([
    html.H6("Change the value in the text box to see callbacks in action"),
    html.Div([
        html.Label('Input: '),
        dcc.Input(id='my-input', type='text', value='sample text'),
    ]),
    html.Br(),
    html.Div(id='my-output') # any children we define here for the output would get overwritten because the Dash app automatically calls all of the calbacks with the initial input values when it starts
])

# define callback
# - update fn
# - decorator, which takes the outputs and inputs of the application (these are properties of certain components)
#   ---> call the fn this decorator acts on whenever the input value changes, in order to update the children of the output component
#   ----> you must use the same id used in the layout def
# here the input is the 'value' property of the component with ID 'my-input'
# Don't confuse the dash.dependencies.Input object (only used in callback definitions) and the dcc.Input object (an actual component).
@app.callback(
    Output(component_id='my-output', component_property='children'), # component_property: property of the output to update?
    Input(component_id='my-input', component_property='value') # component_property: property of the input to observe?
)
# The arguments are positional by default: first the Input items and then any State items are given in the same order as in the decorator
def update_output_div(input_value): 
    return f'Output: {input_value.upper()}'


if __name__=='__main__':
    app.run_server(debug=True)