# Dash tutorial: interactive app with simple callbacks -- Multiple inputs
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
app = Dash(__name__)

# define layout
# pdb.set_trace()
app.layout = html.Div(
    [  # Header
        html.Div(
            [  # Dropdown + Radio buttons for x-axis
                html.Div(
                    [
                        dcc.Dropdown(
                            options=[
                                {"label": el, "value": el}
                                for el in df["Indicator Name"].unique()
                            ],  # options
                            value="Fertility rate, total (births per woman)",  # default
                            id="xaxis-column",
                        ),
                        dcc.RadioItems(
                            options=[
                                {"label": el, "value": el}
                                for el in ["Linear", "Log"]
                            ],
                            value="Linear",
                            id="xaxis-type",
                        ),
                    ],
                    style={"width": "48%", "display": "inline-block"},
                ),
                # Dropdown + Radio buttons for y-axis
                html.Div(
                    [
                        dcc.Dropdown(
                            options=[
                                {"label": el, "value": el}
                                for el in df["Indicator Name"].unique()
                            ],  # options
                            value="Life expectancy at birth, total (years)",
                            id="yaxis-column",
                        ),
                        dcc.RadioItems(
                            options=[
                                {"label": el, "value": el}
                                for el in ["Linear", "Log"]
                            ],
                            value="Linear",
                            id="yaxis-type",
                        ),
                    ],
                    style={
                        "width": "48%",
                        "float": "right",
                        "display": "inline-block",
                    },
                ),
            ]
        ),
        # Graph
        dcc.Graph(id="indicator-graphic"),

        # Slider: select year to show indicator in
        dcc.Slider(
            min=df["Year"].min(),
            max=df["Year"].max(),
            step=None,
            id="year--slider",
            value=df["Year"].max(),
            marks={str(year): str(year) for year in df["Year"].unique()},
        ),
    ]
)

####################
## Callback with multiple input/triggers
# - the multiple inputs are just listed after the output (defined by ID and property)
# - the callback executes whenever the value property of any of the Input components changes
# - the input arguments of the callback function are ***each of the input properties 
#   IN THE ORDER THEY ARE SPECIFIED IN THE DECORATOR***
# ---------------------------------------------------------------------
# ATT! Callbacks should never modify variables outside of their scope!
# ---------------------------------------------------------------------
# - otherwise if a callback modifies a global state, a user's session might affect the next user's session!
# - also when the app is deployed on multiple threads, modifs would not be shared!
# here we make a copy of the dataframe by filtering using pandas
# - even tho only a single input changes at a time (the user cannot change several inputs simultaneously),
#   Dash collects the full state of the input properties and passes them into the callback fn

@app.callback(
    Output(
        component_id="indicator-graphic", 
        component_property='figure'),
    Input(component_id="xaxis-column", component_property='value'),
    Input(component_id="yaxis-column", component_property='value'),
    Input(component_id="xaxis-type", component_property='value'),
    Input(component_id="yaxis-type", component_property='value'),
    Input(component_id="year--slider", component_property='value'),
)
def update_graph(
    xaxis_column_name, # from dropdown
    yaxis_column_name, # from dropdown
    xaxis_type, # from radio
    yaxis_type, # from radio
    year_value # from slider---these match the order in the inputs decorator
):

    # Filter dataframe to year in slider
    dff = df[df["Year"] == year_value]

    # Plot Scatter plot
    fig = px.scatter(
        x=dff[dff["Indicator Name"] == xaxis_column_name]['Value'],
        y=dff[dff['Indicator Name'] == yaxis_column_name]['Value'],
        hover_name=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'])

    # figure layout?
    fig.update_layout(
        margin={'l':40, 'b':40, 't':10, 'r':0},
        hovermode='closest')

    fig.update_xaxes(
        title=xaxis_column_name,
        type=xaxis_type.lower()
        )
    fig.update_yaxes(
        title=yaxis_column_name,
        type=yaxis_type.lower()
        )

    # return updated figure!!!
    return fig #---this matches the output in the decorator

## Driver
if __name__ == "__main__":
    app.run_server(debug=True)
