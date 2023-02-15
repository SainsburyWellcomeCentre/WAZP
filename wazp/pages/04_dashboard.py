import dash

# import plotly.express as px
from dash import html

######################
# Add page to registry
#########################
dash.register_page(__name__)


# ##########################
# # Read dataframe for one h5 file
# # TODO: this will be part of the figs' callbacks
# h5_file_path = (
#     "sample_project/pose_estimation_results/"
#     "jwaspE_nectar-open-close_controlDLC_"
#     "resnet50_jwasp_femaleandmaleSep12shuffle1_1000000.h5"
# )
# df_trajectories = pd.read_hdf(h5_file_path.replace("\n", ""))
# df_trajectories.columns = df_trajectories.columns.droplevel()


#######################
# Slider component
####################
# TODO put this in a callback and get labels from project config


######################
# Layout
####################

layout = html.Div(
    className="row",
    children=[
        html.H1("Dashboard"),
        html.Br(),
        html.H5(
            "Input data", style={"margin-top": "20px", "margin-bottom": "20px"}
        ),
        html.Div(children=[], id="videos-table-container"),
        # html.Hr(
        #     style={"margin-top": "30px", "margin-bottom": "15px"}
        # ),
        # html.H5(
        #     "Time range",
        #     style={"margin-top": "20px", "margin-bottom": "25px"}
        # ),
        html.Div(
            children=[],
            id="slider-container",
            style={"margin-top": "30px", "margin-bottom": "25px"},
        ),
        # html.Hr(
        #     style={"margin-top": "60px", "margin-bottom": "15px"}
        # ),
        # html.H5(
        #     "Export", style={"margin-top": "60px", "margin-bottom": "25px"}
        # ),
        html.Div(
            children=[],
            id="export-container",
            style={"margin-top": "30px", "margin-bottom": "25px"},
        ),
        # html.H5(
        #     "Plots", style={"margin-top": "60px", "margin-bottom": "25px"}
        # ),
        html.Div(children=[], id="custom-plot-container"),
        html.Div(
            [
                # html.Hr(),
                html.Div(children=[]),
                html.Div(children=[]),
            ]
        ),
    ],
)
