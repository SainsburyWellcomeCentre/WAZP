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
init_roi_color = px.colors.qualitative.Dark2[0]
# Initialize the frame slider parameters for each video
init_frame_slider_params: dict = {"max": 1, "step": 1, "value": 0}
init_frame_slider_storage: dict = {
    v: init_frame_slider_params for v in init_videos
}
# Columns for ROI table
init_roi_table_columns = ["name", "on frame", "path"]
# Initialize the ROI storage dictionary
init_roi_storage: dict = {v: {"shapes": []} for v in init_videos}
# Initialize the ROI status alert
init_roi_status: dict = {"message": "No ROIs to save.", "color": "light"}


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

# Frame selection slider
frame_slider = dcc.Slider(
    id="frame-slider",
    min=0,
    max=init_frame_slider_params["max"],
    step=init_frame_slider_params["step"],
    value=init_frame_slider_params["value"],
)

# frame status alert
frame_status_alert = dbc.Alert(
    "",
    id="frame-status-alert",
    color="light",
    is_open=False,
    dismissable=True,
)

###############################
# Table of ROIs               #
###############################

roi_table = dash_table.DataTable(
    id="roi-table",
    columns=[dict(name=c, id=c) for c in init_roi_table_columns],
    data=[],
    selected_rows=[],
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
    row_selectable="multi",
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
disabled_button_style = {
    "n_clicks": 0,
    "outline": False,
    "color": "dark",
    "disabled": True,
    "class_name": "w-100",
}

save_rois_button = dbc.Button(
    "Save all",
    id="save-rois-button",
    download="rois.yaml",
    **disabled_button_style,
)
load_rois_button = dbc.Button(
    "Load all", id="load-rois-button", **disabled_button_style
)
delete_rois_button = dbc.Button(
    "Delete selected", id="delete-rois-button", **disabled_button_style
)
# Tooltips for ROI buttons
save_rois_tooltip = dbc.Tooltip(
    "Save all ROIs to the video's .metadata.yaml file. "
    "This will overwrite any existing ROIs in the file!",
    target="save-rois-button",
)
load_rois_tooltip = dbc.Tooltip(
    "Load all ROIs from the video's metadata.yaml file. "
    "This will overwrite any existing ROIs in the app!",
    target="load-rois-button",
)

# ROI status alert
roi_status_alert = dbc.Alert(
    init_roi_status["message"],
    id="rois-status-alert",
    color=init_roi_status["color"],
    is_open=False,
    dismissable=True,
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
                        dbc.Col(dcc.Markdown("Select video"), width=3),
                        dbc.Col(video_dropdown, width=9),
                        dcc.Store(
                            id="frame-slider-storage",
                            data=init_frame_slider_storage,
                            storage_type="session",
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(dcc.Markdown("Select frame"), width=3),
                        dbc.Col(dcc.Loading(frame_slider), width=9),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(dcc.Markdown("Draw ROI for"), width=3),
                        dbc.Col(dcc.Loading(roi_dropdown), width=9),
                    ]
                ),
            ]
        ),
        dbc.CardBody(frame_graph),
        dbc.CardFooter(dcc.Loading(frame_status_alert)),
    ],
)

# ROI table card
table_card = dbc.Card(
    [
        dbc.CardHeader(html.H3("Defined ROIs")),
        dbc.CardBody(
            [
                dbc.Row(dbc.Col(roi_table)),
                dcc.Store(data={}, id="roi-colors-storage"),
                dcc.Store(
                    id="roi-storage",
                    data=init_roi_storage,
                    storage_type="session",
                ),
            ]
        ),
        dbc.CardFooter(
            [
                dbc.Row(
                    [
                        dbc.Col(delete_rois_button, width={"size": "auto"}),
                        dbc.Col(save_rois_button, width={"size": "auto"}),
                        dbc.Col(load_rois_button, width={"size": "auto"}),
                        save_rois_tooltip,
                        load_rois_tooltip,
                    ],
                ),
                html.Br(),
                dcc.Loading(dbc.Row(roi_status_alert)),
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
