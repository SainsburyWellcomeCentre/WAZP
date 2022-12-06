# From dash tutorial at https://dash.plotly.com/layout

from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd


app = Dash(__name__)


# Define color scheme
colors = {
    "background": "#111111",
    "text": "#7FDBFF",
}


# Data: long-form dataframe
df = pd.DataFrame(
    {
        "Fruit": [
            "Apples",
            "Apples",
            "Bananas",
            "Bananas",
            "Oranges",
            "Oranges",
        ],
        "Amount": [2, 4, 2, 2, 5, 6],
        "City": [
            "Wuppertal",
            "Seville",
            "Wuppertal",
            "Seville",
            "Wuppertal",
            "Seville",
        ],
    }
)

# Figure: bar plot
fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")


# Customize colors of fig
fig.update_layout(
    plot_bgcolor=colors["background"],
    paper_bgcolor=colors["background"],
    font_color=colors["text"],
)  # update figure layout


# Define layout of the app:
# - it is a tree of components (html.H1, html.Div, dcc.Graph)
app.layout = html.Div(
    style={"backgroundColor": colors["background"]},
    children=[
        html.H1(
            children="Hello Dash",
            style={
                "textAlign": "center",
                "color": colors["text"],
            },  # add text style
        ),
        html.Div(
            children="""Dash: A web application framework for your data.""",
            style={
                "textAlign": "center",
                "color": colors["text"],
            },  # add text style
        ),
        dcc.Graph(id="example-graph", figure=fig),
    ],
)


# driver
if __name__ == "__main__":
    app.run_server(
        debug=True
    )  # what does it mean debug ON? it updates with changes in the code?---yes, hot reloading
    # To disable hot-reloading:
    # app.run_server(dev_tools_hot_reload=False)---why not debug=False? for jupyter recommended to turn off
