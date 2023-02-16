import dash
import dash_bootstrap_components as dbc
import plotly.express as px
from dash import dash_table, dcc, html
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
init_roi_color = "#fff"
# Columns for ROI table
init_roi_table_columns = ["ROI", "path"]


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

# video selection dropdown
video_dropdown = dcc.Dropdown(
    id="video-select",
    placeholder="Select video",
    options=[{"label": v, "value": v} for v in init_videos],
    value=init_videos[0],
    clearable=False,
)

###############################
# Table of ROIs               #
###############################

roi_table = dash_table.DataTable(
    id="roi-table",
    columns=[dict(name=c, id=c) for c in init_roi_table_columns],
    data=[],
    editable=False,
    style_data={"height": 40},
    style_cell={
        "overflow": "hidden",
        "textOverflow": "ellipsis",
        "maxWidth": 0,
        "textAlign": "left",
    },
    style_data_conditional=[],
    fill_width=True,
)

# Dropdown for ROI selection
roi_dropdown = dcc.Dropdown(
    id="roi-select",
    placeholder="Select ROI",
    options=[{"label": roi, "value": roi} for roi in init_roi_names],
    value=init_roi_names[0],
    clearable=False,
)

###############################
# Put elements into cards     #
###############################

# Video frame card
frame_card = dbc.Card(
    id="frame-card",
    children=[
        dbc.CardHeader(video_dropdown),
        dbc.CardBody(frame_graph),
    ],
)

# ROI table card
table_card = dbc.Card(
    [
        dbc.CardBody(
            [
                dbc.Row(dbc.Col(html.H4("Defined ROIs"))),
                dbc.Row(dbc.Col(roi_table)),
                dbc.Row(
                    dbc.Col(
                        [
                            html.Br(),
                            html.H4("Create new ROI for"),
                            roi_dropdown,
                        ],
                        align="center",
                    )
                ),
                dcc.Store(data={}, id="roi-colors-storage"),
            ]
        ),
    ]
)

###############################
# Define page layout          #
###############################

layout = dbc.Container(
    [
        html.H1(children="ROI definition"),
        dbc.Row(
            [
                dbc.Col(frame_card, width=7),
                dbc.Col(table_card, width=5),
            ],
        ),
    ],
    fluid=True,
)
