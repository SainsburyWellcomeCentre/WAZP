import dash
import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html

######################
# Add page to registry
#########################
dash.register_page(__name__)

###############################
# Initialize variables        #
###############################

# Get initial video
init_videos = ["No videos found yet"]
# Get initial set of event tags to initialize table
init_event_tags = ["start", "end"]

# Columns for events table
init_events_table_columns = ["tag", "frame index", "seconds"]
# Initialize the events storage dictionary
init_events_storage: dict = {v: {} for v in init_videos}
# Initialize the events status alert
init_events_status: dict = {"message": "No events defined", "color": "light"}

###############################
# Table of events             #
###############################

events_table = dash_table.DataTable(
    id="events-table",
    columns=[dict(name=c, id=c) for c in init_events_table_columns],
    data=[],
    editable=True,
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

# video selection dropdown
events_video_select = dcc.Dropdown(
    id="events-video-select",
    placeholder="Select video",
    options=[{"label": v, "value": v} for v in init_videos],
    clearable=False,
)

# events status alert
events_status_alert = dbc.Alert(
    init_events_status["message"],
    id="event-status-alert",
    color=init_events_status["color"],
    is_open=False,
    dismissable=True,
)

###############################
# Put elements into card      #
###############################

# events table card
events_table_card = dbc.Card(
    [
        dbc.CardHeader(events_video_select),
        dbc.CardBody(
            [
                dbc.Row(dbc.Col(html.H4("Defined events"))),
                dbc.Row(dbc.Col(events_table)),
                dcc.Store(
                    id="events-storage",
                    data=init_events_storage,
                    storage_type="session",
                ),
            ]
        ),
        dbc.CardFooter(events_status_alert),
    ]
)

###############################
# Define page layout          #
###############################

layout = dbc.Container(
    [
        html.H1(children="Event tagging"),
        dbc.Row(dbc.Col(events_table_card)),
    ],
    fluid=True,
)
