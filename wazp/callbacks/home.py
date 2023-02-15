import base64
from typing import Any

import dash
import yaml
from dash import Input, Output, State


def get_callbacks(app: dash.Dash) -> None:
    """Return all callback functions for the home tab.

    Parameters
    ----------
    app : dash.Dash
        Dash app object for which these callbacks are defined
    """

    @app.callback(
        Output("session-storage", "data"),
        Output("upload-message", "is_open"),
        Output("upload-message", "children"),
        Output("upload-message", "color"),
        Input("upload-data", "contents"),
        State("upload-data", "filename"),
        State("upload-message", "is_open"),
    )
    def save_input_config_to_storage(
        up_content: str, up_filename: str, up_message_state: bool
    ) -> tuple[dict[Any, Any], bool, str, str]:
        """Save project configuration file to temporary memory storage for the current session.

        See https://community.plotly.com/t/dash-plotly-share-callback-input-in-another-page-with-dcc-store/44190/2

        Parameters
        ----------
        up_content : str
            data from the project config file upload
        up_filename : str
            name of the uploaded file (project config file)
        up_message_state : bool
            visibility of the upload message

        Returns
        -------
        data_to_store : dict
            dictionary with the following keys and values:
            - 'config': a dict with the project configuration parameters
            - 'metadata_fields': a dict with a set of attributes (description, type...)
            for each metadata field
        up_message_state : bool
            visibility of the upload message
        output_message : str
            content of the upload message
        output_color : str
            color of the upload message
        """  # noqa

        data_to_store = dict()

        # default parameters for confirmation message
        output_message = ""
        output_color = "light"
        if up_content is not None:
            _, content_str = up_content.split(",")
            try:
                if "yaml" in up_filename:
                    # get config
                    config = yaml.safe_load(base64.b64decode(content_str))

                    # get metadata fields dict
                    with open(config["metadata_fields_file_path"]) as mdf:
                        metadata_fields_dict = yaml.safe_load(mdf)

                    # bundle data
                    data_to_store = {
                        "config": config,
                        "metadata_fields": metadata_fields_dict,
                    }

                    # output message
                    if not up_message_state:
                        up_message_state = not up_message_state
                    output_message = (
                        f"Input config for:"
                        f"{config['videos_dir_path']} processed successfully."
                    )
                    output_color = "success"
                    # TODO: print path to config file instead?

            except Exception as e:
                print(e)  # TODO: check this, it prints something odd
                if not up_message_state:
                    up_message_state = not up_message_state
                output_message = (
                    "There was an error processing the config file."
                )
                output_color = "danger"

        return (data_to_store, up_message_state, output_message, output_color)
