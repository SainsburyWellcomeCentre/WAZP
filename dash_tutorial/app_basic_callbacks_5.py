# Dash tutorial: Callbacks -- Chained callbacks
# The output of one callback fn is the input of another (e.g., one input component updates the avail options of another)
# https://dash.plotly.com/basic-callbacks

from dash import Dash, dcc, html, Input, Output
import pandas as pd
import plotly.express as px

# import pdb


#############################
## Define app
# initialise app
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = Dash(__name__, external_stylesheets=external_stylesheets)

# define layout

options_per_country = {
    "Spain": ["Madrid", "Barcelona", "Valencia"],
    "Colombia": [u"Bogotá", "Cali", "Cartagena"],
}

# pdb.set_trace()
app.layout = html.Div(
    [
        # Country selector
        dcc.RadioItems(
            options=[
                {"label": el, "value": el}
                for el in list(options_per_country.keys())
            ],
            value="Spain",
            id="radio-country",
        ),
        # Section break
        html.Hr(),  # thematic break == (semantic) horizontal rule
        # City selector --- chained
        dcc.RadioItems(id="radio-city"),
        # Section break
        html.Hr(),
        # Display output
        html.Div(id="display-selected-values"),
    ]
)


####################
## Callback with multiple outputs
# - return as many objects as outputs in the decorator
# - OJO! It's not always a good idea to combine outputs
#   - keeping them separate can prevent unnecessary updates
#   - if computations for the diff outputs are very diff, we may be able to run them in parallel if callbacks are separate
@app.callback(Output("radio-city", "options"), Input("radio-country", "value"))
def update_city_selector(country_str):
    return [
        {"label": el, "value": el} for el in options_per_country[country_str]
    ]


@app.callback(
    Output("radio-city", "value"), Input("radio-city", "options")
)  # output from previous callback is input of this one!)
def update_city_default_value(list_city_options):
    return list_city_options[0][
        "value"
    ]  # OJO options is a list of dicts with keys 'label' and 'value'


@app.callback(
    Output("display-selected-values", "children"),
    Input("radio-country", "value"),
    Input("radio-city", "value"),
)
def display_selected_values(country_str, city_str):
    return f"{city_str} is a city in {country_str}"


###################
## Driver
if __name__ == "__main__":
    app.run_server(debug=True)
