# Dash tutorial Callbacks -- Passing components into callbacks (instead of IDs)
# https://dash.plotly.com/basic-callbacks 

from dash import Dash, dcc, html, Input, Output


##################
# define app components as vars
input_component = dcc.Input(type='text', value='sample text')
output_component = html.Div() #we don't need ID anymore

# initialise app
app = Dash(__name__) 

# define app layout and pass the components as vars
app.layout = html.Div([
    html.H6("Change the value in the text box to see callbacks in action"),
    html.Div([
        html.Label('Input: '),
        input_component, # In Python > 3.8 we can use walrus operator (assign and define in one go): input_component := dcc.Input(type='text', value='sample text')
    ]),
    html.Br(),
    output_component # In Python > 3.8 we can use walrus operator: output_component := html.Div()
])


##################
# Callback
# We can pass the component directly as inputs/outputs rather than the id (Dash autogenerates the IDs for them)
# - OJO! the input/outputs component vars need to be defined outside the scope of the callback fn --otherwise auto component ID does not work
@app.callback(
    Output(output_component, component_property='children'), # component_property: property of the output to update?
    Input(input_component, component_property='value') # component_property: property of the input to observe?
)
# The arguments are positional by default: first the Input items and then any State items are given in the same order as in the decorator
def update_output_div(input_value): 
    return f'Output: {input_value.upper()}'


if __name__=='__main__':
    app.run_server(debug=True)