import dash
import dash_bootstrap_components as dbc
import plotly.express as px
from dash import dash_table, dcc, html
from PIL import Image

from wazp.utils import time_passed

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
init_roi_color = px.colors.qualitative.Dark2[0]
# Initialize the number of frames in the video
init_num_frames: dict = {v: 1 for v in init_videos}
# Columns for ROI table
init_roi_table_columns = ["ROI", "path"]
# Initialize the ROI storage dictionary
init_roi_storage: dict = {v: {"shapes": []} for v in init_videos}
# Also add a start_time to the ROI storage
init_roi_storage["start_time"] = time_passed()

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

# Frame selection input box
frame_input = dbc.Input(
    id="frame-input",
    type="number",
    placeholder="Frame number",
    min=0,
    max=init_num_frames[init_videos[0]],
    step=1,
    value=0,
    debounce=True,
)

# frame status alert
frame_status_alert = dbc.Alert(
    "",
    id="frame-status-alert",
    color="light",
    is_open=False,
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

# Buttons for saving/loading ROIs
roi_save_button = dbc.Button(
    "Save ROIs",
    id="save-rois-button",
    download="rois.yaml",
    n_clicks=0,
    outline=True,
    color="dark",
)
roi_load_button = dbc.Button(
    "Load ROIs",
    id="load-rois-button",
    n_clicks=0,
    outline=True,
    color="dark",
)
infer_rois_button = dbc.Button(
    "Infer ROIs",
    id="infer-rois-button",
    n_clicks=0,
    outline=True,
    color="dark",
)
# Tooltips for ROI buttons
save_rois_tooltip = dbc.Tooltip(
    "Save the ROIs to the video's " ".metadata.yaml file",
    target="save-rois-button",
)
load_rois_tooltip = dbc.Tooltip(
    "Load ROIs from the video's " ".metadata.yaml file",
    target="load-rois-button",
)
infer_rois_tooltip = dbc.Tooltip(
    "Infer ROI positions" "based on defined ROIs",
    target="infer-rois-button",
)

# ROI status alert
roi_status_alert = dbc.Alert(
    "No ROIs to save.",
    id="rois-status-alert",
    color="light",
    is_open=True,
)

###############################
# Put elements into cards     #
###############################

# Video frame card
frame_card = dbc.Card(
    id="frame-card",
    children=[
        dbc.CardHeader(
            [
                dbc.Row(
                    [
                        dbc.Col(dcc.Markdown("Select video"), width=4),
                        dbc.Col(video_dropdown, width=8),
                        dcc.Store(
                            id="num-frames-storage",
                            data=init_num_frames,
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(dcc.Markdown("Frame shown"), width=4),
                        dbc.Col(frame_input, width=8),
                    ]
                ),
            ]
        ),
        dbc.CardBody(frame_graph),
        dbc.CardFooter(frame_status_alert),
    ],
)

# ROI table card
table_card = dbc.Card(
    [
        dbc.CardHeader(
            dbc.Row(
                [
                    dbc.Col(roi_save_button, width=4),
                    dbc.Col(roi_load_button, width=4),
                    dbc.Col(infer_rois_button, width=4),
                    save_rois_tooltip,
                    load_rois_tooltip,
                    infer_rois_tooltip,
                ],
            ),
        ),
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
                dcc.Store(id="roi-storage", data=init_roi_storage),
            ]
        ),
        dbc.CardFooter(roi_status_alert),
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
