import dash_player
from dash import dcc, html, register_page

register_page(__name__)

layout = html.Div(
    children=[
        html.H1(children="Video player"),
        html.Div(
            [
                html.Div(
                    style={"width": "48%", "padding": "0px"},
                    children=[
                        dash_player.DashPlayer(
                            id="player",
                            url="https://youtu.be/t0Q2otsqC4I",
                            controls=True,
                            width="100%",
                            height="250px",
                        ),
                        html.Div(
                            [
                                html.Div(
                                    id="current-time-div",
                                    style={"margin": "10px 0px"},
                                ),
                                html.Div(
                                    id="duration-div",
                                    style={"margin": "10px 0px"},
                                ),
                            ],
                            style={
                                "display": "flex",
                                "flex-direction": "column",
                            },
                        ),
                    ],
                ),
                html.Div(
                    style={"width": "48%", "padding": "10px"},
                    children=[
                        html.P("Playback Rate:", style={"marginTop": "25px"}),
                        dcc.Slider(
                            id="playback-rate-slider",
                            min=0,
                            max=2,
                            step=None,
                            updatemode="drag",
                            marks={
                                i: str(i) + "x" for i in [0, 0.5, 1, 1.5, 2]
                            },
                            value=1,
                        ),
                    ],
                ),
            ],
            style={
                "display": "flex",
                "flexDirection": "row",
                "justifyContent": "space-between",
            },
        ),
    ]
)
