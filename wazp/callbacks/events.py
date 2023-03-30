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
    ) -> tuple[list, str]:
        """Update the video selection dropdown with the videos defined in
        the project configuration file.

        Parameters
        ----------
        app_storage : dict
            data held in temporary memory storage,
            accessible to all tabs in the app

        Returns
        -------
        options : list
            list of dictionaries with the following keys and values:
            - 'label': video name
            - 'value': video name
        value : str
            Currently selected video name
        """

        if "video_paths" in app_storage:
            options = [
                {"label": v, "value": v} for v in app_storage["video_paths"]
            ]
            value = options[0]["value"]
            return options, value
        else:
            return dash.no_update, dash.no_update

    @app.callback(
        [
            Output("event-select", "options"),
            Output("event-select", "value"),
        ],
        Input("session-storage", "data"),
    )
    def update_event_select_options(
        app_storage: dict,
    ) -> tuple[list, str]:
        """Update the options of the event select dropdown with
        the event tags defined in the project configuration file.

        Parameters
        ----------
        app_storage : dict
            data held in temporary memory storage,
            accessible to all tabs in the app

        Returns
        -------
        options : list
            list of dictionaries with the following keys and values:
            - 'label': event tag
            - 'value': event tag
        value : str
            Currently selected event tag
        """
        if "config" in app_storage.keys():
            # Get ROI names from stored config
            config = app_storage["config"]
            event_tags = config["event_tags"]
            options = [{"label": t, "value": t} for t in event_tags]
            value = event_tags[0]
            return options, value
        else:
            return dash.no_update, dash.no_update
