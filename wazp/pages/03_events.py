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
init_videos = [""]
# Get initial set of event tags to initialize table
init_event_tags = [""]

# Columns for events table
init_events_table_columns = ["tag", "frame index", "seconds"]
# Initialize the events storage dictionary
init_events_storage: dict = {v: {} for v in init_videos}
# Initialize the events status alert
init_events_status: dict = {"message": "No events defined", "color": "light"}

disabled_button_style = {
    "n_clicks": 0,
    "outline": False,
    "color": "dark",
    "disabled": True,
    "class_name": "w-100",
}

###############################
# Table of events             #
###############################

events_table = dash_table.DataTable(
    id="events-table",
    columns=[dict(name=c, id=c) for c in init_events_table_columns],
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

# video selection dropdown
events_video_select = dcc.Dropdown(
    id="events-video-select",
    placeholder="Select video",
    options=[{"label": v, "value": v} for v in init_videos],
    clearable=False,
)

event_dropdown = dcc.Dropdown(
    id="event-select",
    placeholder="Select event",
    options=[{"label": e, "value": e} for e in init_event_tags],
    value=init_event_tags[0],
    clearable=False,
)

frame_index_input = dbc.Input(
    id="frame-index-input",
    type="number",
    placeholder="Frame index",
    min=0,
    max=1,
    step=1,
    value=0,
)

tag_event_button = dbc.Button(
    "Tag event",
    id="tag-event-button",
    **disabled_button_style,
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
    children=[
        dbc.CardHeader(
            [
                dbc.Row(
                    [
                        dbc.Col(dcc.Markdown("Select video"), width=2),
                        dbc.Col(events_video_select, width=10),
                    ],
                ),
                dbc.Row(
                    [
                        dbc.Col(dcc.Markdown("Select event"), width=2),
                        dbc.Col(event_dropdown, width=3),
                        dbc.Col(dcc.Markdown("at frame"), width=2),
                        dbc.Col(dcc.Loading(frame_index_input), width=2),
                        dbc.Col(tag_event_button, width=3),
                    ],
                ),
            ],
        ),
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
