import dash
import pandas as pd
import plotly.express as px
from dash import dcc, html

######################
# Add page to registry
#########################
dash.register_page(__name__)


##########################
# Read dataframe for one h5 file
# TODO: this will be part of the figs' callbacks
h5_file_path = (
    "sample_project/pose_estimation_results/"
    "jwaspE_nectar-open-close_controlDLC_"
    "resnet50_jwasp_femaleandmaleSep12shuffle1_1000000.h5"
)
df_trajectories = pd.read_hdf(h5_file_path.replace("\n", ""))
df_trajectories.columns = df_trajectories.columns.droplevel()


########################
# Prepare figures --- TODO: this will be updated with callbacks
# Trajectories
fig_trajectories = px.scatter(
    df_trajectories["head"],
    x="x",
    y="y",
    labels={
        "x": "x-axis (px)",
        "y": "y-axis (px)",
        "likelihood": "likelihood",
    },
    color="likelihood",
    custom_data=df_trajectories["head"].columns,
    title="Raw trajectories",
)
fig_trajectories.update_layout(
    clickmode="event+select",
    # xaxis_range=[0,1300],
    # yaxis_range=[0,1100]
)
fig_trajectories.update_yaxes(
    scaleanchor="x",
    scaleratio=1,
)
fig_trajectories.update_traces(marker_size=5)

# Heatmap
fig_heatmap = px.density_heatmap(
    df_trajectories["head"],
    x="x",
    y="y",
    labels={
        "x": "x-axis (px)",
        "y": "y-axis (px)",
    },
    nbinsx=10,
    nbinsy=10,
    title="Heatmap",
)
fig_heatmap.update_layout(
    clickmode="event+select",
    # xaxis_range=[0,1300],
    # yaxis_range=[0,1200]
)
fig_heatmap.update_yaxes(
    scaleanchor="x",
    scaleratio=1,
)

df_occupancy = pd.DataFrame(
    {
        "ROI": [
            "ROI 1",
            "ROI 2",
            "ROI 3",
            "ROI 4",
            "ROI 1",
            "ROI 2",
            "ROI 3",
            "ROI 4",
        ],
        "occupancy": [0.4, 0.2, 0.4, 0.5, 0.3, 0.8, 0.7, 0.1],
        "sex": ["M", "M", "M", "M", "F", "F", "F", "F"],
    }
)

fig_barplot = px.bar(
    df_occupancy,
    x="ROI",
    y="occupancy",
    color="sex",
    barmode="group",
    title="Barplot occupancy",
)
fig_barplot.update_layout(clickmode="event+select")


# Entries/exits matrix
data = [[10, 25, 30, 50], [20, 60, 80, 30], [30, 60, 15, 20], [80, 50, 20, 39]]
fig_entries_exits = px.imshow(
    data,
    labels=dict(x="departure ROI", y="destination ROI", color="count"),
    x=["ROI 1", "ROI 2", "ROI 3", "ROI 4"],
    y=["ROI 1", "ROI 2", "ROI 3", "ROI 4"],
    title="Entries/exits matrix",
)

fig_entries_exits.update_layout(
    clickmode="event+select", height=500, width=500
)
fig_entries_exits.update_xaxes(side="top")


###############
# Dashboard layout


def plots_first_row_left():
    """Configure the HTML div contents for the first row left hand side"""
    trajectories_graph = dcc.Graph(
        id="graph-trajectories",
        figure=fig_trajectories,
        style={
            "width": "85%",
            "display": "inline-block",
        },
    )
    radio_button = dcc.RadioItems(
        ["likelihood", "frame", "input data"],
        "likelihood",
        style={
            "width": "15%",
            "float": "right",
            "margin-top": "110px",
        },
        labelStyle={
            "display": "block",
            "fontSize": ".8rem",
        },
    )
    return html.Div(
        children=[trajectories_graph, radio_button],
        style={"width": "49%", "display": "inline-block"},
    )


def plots_first_row_right():

    nbins_button = dcc.Input(
        id="bin-size",
        type="number",
        placeholder="nbins per axis",
        debounce=True,  # need to press enter,
        style={"float": "right"},
    )  # "value" will be in callback

    heatmap_graph = dcc.Graph(
        id="graph-heatmap",
        figure=fig_heatmap,
        style={
            "width": "85%",
            "display": "inline-block",
            "float": "right",
        },
    )
    return html.Div(
        children=[nbins_button, heatmap_graph],
        style={"width": "49%", "display": "inline-block"},
    )


def plots_second_row_left():
    return dcc.Graph(
        id="graph-barplot",
        figure=fig_barplot,
        style={"width": "42%", "display": "inline-block"},
    )


def plots_second_row_right():
    return dcc.Graph(
        id="graph-entries-exits",
        figure=fig_entries_exits,
        style={
            "width": "42%",
            "display": "inline-block",
            "float": "right",
        },
    )


layout = html.Div(
    className="row",
    children=[
        html.H1("Dashboard"),
        html.Br(),
        html.H5(
            "Input data", style={"margin-top": "20px", "margin-bottom": "10px"}
        ),
        html.Div(children=[], id="table-container"),
        html.Div(
            [
                html.Hr(),
                html.Div(
                    children=[
                        plots_first_row_left(),
                        plots_first_row_right(),
                    ]
                ),
                html.Div(
                    children=[
                        plots_second_row_left(),
                        plots_second_row_right(),
                    ]
                ),
            ]
        ),
    ],
)
