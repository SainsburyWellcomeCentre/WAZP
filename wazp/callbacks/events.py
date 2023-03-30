from typing import Optional

import dash
from dash import Input, Output


def get_callbacks(app: dash.Dash) -> None:
    """
    Return all callback functions for the events tab.

    Parameters
    ----------
    app : dash.Dash
        Dash app object for which these callbacks are defined
    """

    @app.callback(
        [
            Output("events-video-select", "options"),
            Output("events-video-select", "value"),
        ],
        Input("session-storage", "data"),
    )
    def update_events_video_select(
        app_storage: dict,
    ) -> tuple[list, Optional[str]]:
        """Update the video selection dropdown with the videos defined in
        the project configuration file.

        Parameters
        ----------
        app_storage : dict
            dictionary with the following keys and values:
            - 'config': a dict with the project configuration parameters
            - 'metadata_fields': a dict with a set of attributes
            - 'video_paths': a dict storing paths to the video files

        Returns
        -------
        options : list
            list of dictionaries with the following keys and values:
            - 'label': video name
            - 'value': video name
        value : str
            Currently selected video name
        """

        options = []
        if "video_paths" in app_storage:
            options = [
                {"label": v, "value": v} for v in app_storage["video_paths"]
            ]
        value = options[0]["value"] if options else None
        return options, value
