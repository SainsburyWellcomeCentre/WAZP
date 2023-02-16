import dash
import dash_bootstrap_components as dbc
import plotly.express as px
from dash import dcc, html
from PIL import Image

###############################
# Add page to registry        #
###############################
dash.register_page(__name__)

###############################
# Initialize variables        #
###############################

# Get initial video
init_videos = ["No videos found yet"]
# Get initial set of ROIs to initialize dropdown
init_roi_names = ["No ROIs defined yet"]
# Default color for ROI drawing
init_roi_color = px.colors.qualitative.Dark24[0]


###############################
# Graph showing a video frame #
###############################

# Default white frame to show
default_frame = Image.new("RGB", (1456, 1088), (255, 255, 255))

# Create figure
fig = px.imshow(default_frame)
fig.update_layout(
    dragmode="drawclosedpath",
    newshape_line_color=init_roi_color,
    margin=dict(l=0, r=0, t=0, b=0),
    yaxis={"visible": False, "showticklabels": False},
    xaxis={"visible": False, "showticklabels": False},
)

# figure configuration
fig_config = {
    "scrollZoom": True,  # enable zooming with scroll wheel
    "displayModeBar": True,  # mode bar always visible
    "showAxisDragHandles": True,  # show axis drag handles
    "modeBarButtonsToAdd": [
        "drawclosedpath",
        "eraseshape",
    ],
    "displaylogo": False,  # hide plotly logo
}

# Put frame figure in a graph
frame_graph = dcc.Graph(
    figure=fig,
    config=fig_config,
    id="frame-graph",
)

###############################
# Put elements into cards     #
###############################

# Cards
frame_card = dbc.Card(
    id="frame-card",
    children=[
        dbc.CardBody(frame_graph),
    ],
)

###############################
# Define page layout          #
###############################

layout = dbc.Container(
    [
        html.H1(children="ROI definition"),
        dbc.Row(frame_card),
    ],
    fluid=True,
)
