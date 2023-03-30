import dash
from dash import Input, Output, State


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

    @app.callback(
        Output("tag-event-button", "disabled"),
        Input("event-select", "value"),
    )
    def disable_tag_event_button(
        event_tag: str,
    ) -> bool:
        """Disable the tag event button if the event tag is empty

        Parameters
        ----------
        event_tag : str
            Currently selected event tag

        Returns
        -------
        disabled : bool
            True if the tag event button should be disabled, False otherwise
        """
        if event_tag == "" or event_tag is None:
            return True
        else:
            return False

    @app.callback(
        Output("events-storage", "data"),
        Input("tag-event-button", "n_clicks"),
        [
            State("frame-index-input", "value"),
            State("events-video-select", "value"),
            State("event-select", "value"),
            State("events-storage", "data"),
        ],
    )
    def update_events_storage(
        n_clicks: int,
        frame_index: int,
        video_name: str,
        event_tag: str,
        events_storage: dict,
    ) -> dict:
        """Update the events storage with the currently selected event tag
        and frame index, when the tag event button is clicked.

        Parameters
        ----------
        n_clicks : int
            Number of times the tag event button has been clicked
        frame_index : int
            Currently selected frame index
        video_name : str
            Currently selected video name
        event_tag : str
            Currently selected event tag
        events_storage : dict
            Dictionary storing event tags for each video.

        Returns
        -------
        events_storage : dict
            data held in temporary memory storage,
            accessible to all tabs in the app
        """
        if n_clicks > 0:
            if video_name not in events_storage.keys():
                events_storage[video_name] = dict()
            events_storage[video_name][event_tag] = frame_index
        return events_storage

    @app.callback(
        Output("events-table", "data"),
        [
            Input("events-video-select", "value"),
            Input("events-storage", "data"),
        ],
    )
    def update_events_table(
        video_name: str,
        events_storage: dict,
    ) -> list[dict]:
        """Update the events table based on the stored events.

        Parameters
        ----------
        video_name : str
            Currently selected video name
        events_storage : dict
            Dictionary storing event tags for each video.

        Returns
        -------
        data : list[dict]
            list of dictionaries with the following keys and values:
            - 'tag': event tag
            - 'frame index': frame index
            - 'seconds': frame index converted to seconds, based on the
                video FPS
        """
        fps = 40
        rows = []
        if video_name in events_storage.keys():
            for event, frame_idx in events_storage[video_name].items():
                sec = frame_idx / fps
                rows.append(
                    {"tag": event, "frame index": frame_idx, "seconds": sec}
                )
        return rows
