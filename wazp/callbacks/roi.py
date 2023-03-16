import pathlib as pl

# import pdb
import re
from typing import Optional

import dash
import plotly.express as px
import plotly.graph_objects as go
import yaml
from dash import Input, Output, State
from PIL import Image

from wazp import utils

# TODO: other video extensions? have this in project config file instead?
VIDEO_TYPES = [".avi", ".mp4"]
# TODO: make colomap this a project config parameter?
ROI_CMAP = px.colors.qualitative.Dark24


#########################
# Callbacks
###########################
def get_callbacks(app: dash.Dash) -> None:
    """
    Return all callback functions for the ROI tab.
    Parameters
    ----------
    app : dash.Dash
        Dash app object for which these callbacks are defined
    """

    @app.callback(
        [
            Output("video-select", "options"),
            Output("video-select", "value"),
        ],
        Input("session-storage", "data"),
    )
    def update_video_select_options(
        app_storage: dict,
    ) -> Optional[tuple[list, str]]:
        """Update the options of the video select dropdown.
        Parameters
        ----------
        app_storage : dict
            data held in temporary memory storage,
            accessible to all tabs in the app
        Returns
        -------
        list
            list of dictionaries with keys 'label' and 'value'
        str
            value of the first video in the list
        """
        if "config" in app_storage.keys():
            # Get videos directory from stored config
            config = app_storage["config"]
            videos_dir = config["videos_dir_path"]
            # get all videos in the videos directory
            video_paths = []
            for video_type in VIDEO_TYPES:
                video_paths += [
                    p for p in pl.Path(videos_dir).glob(f"*{video_type}")
                ]
            video_paths.sort()
            video_names = [p.name for p in video_paths]
            video_paths_str = [p.absolute().as_posix() for p in video_paths]
            # Video names become the labels and video paths the values
            # of the video select dropdown
            options = [
                {"label": v, "value": p}
                for v, p in zip(video_names, video_paths_str)
            ]
            value = video_paths_str[0]
            return options, value
        else:
            return dash.no_update, dash.no_update

    @app.callback(
        [
            Output("roi-select", "options"),
            Output("roi-select", "value"),
            Output("roi-colors-storage", "data"),
        ],
        Input("session-storage", "data"),
    )
    def update_roi_select_options(
        app_storage: dict,
    ) -> Optional[tuple[list[dict], str, dict]]:
        """Update the options of the ROI select dropdown.
        Parameters
        ----------
        app_storage : dict
            data held in temporary memory storage,
            accessible to all tabs in the app
        Returns
        -------
        list[dict]
            list of dictionaries with keys 'label' and 'value'
        str
            value of the first ROI in the list
        dict
            dictionary with the following keys:
                - roi2color: dict mapping ROI names to colors
                - color2roi: dict mapping colors to ROI names
        """
        if "config" in app_storage.keys():
            # Get ROI names from stored config
            config = app_storage["config"]
            roi_names = config["roi_names"]
            options = [{"label": r, "value": r} for r in roi_names]
            value = roi_names[0]

            # Get ROI-to-color mapping
            roi_color_mapping = utils.assign_roi_colors(
                roi_names, cmap=ROI_CMAP
            )

            return options, value, roi_color_mapping
        else:
            return dash.no_update, dash.no_update, dash.no_update

    @app.callback(
        [
            Output("frame-slider", "max"),
            Output("frame-slider", "step"),
            Output("frame-slider", "value"),
            Output("frame-slider-storage", "data"),
        ],
        Input("video-select", "value"),
        State("frame-slider-storage", "data"),
    )
    def update_frame_slider(
        video_path: str, frame_slider_storage: dict
    ) -> tuple[int, int, int, dict]:
        """
        Update the frame slider parameters when a new video
        is selected. Read the parameters from storage if available,
        otherwise extract them from the video file (slower),
        and update the storage for future use.
        Parameters
        ----------
        video_path : str
            Path to the video file.
        frame_slider_storage : dict
            Dictionary storing frame slider parameters for each video.
            It has the following structure:
            {  "video_name_1": {
                    "max": 1000,
                    "step": 100,
                    "value": 500 }
                "video_name_2": {   ... }
            }
        Returns
        -------
        int
            Maximum frame input value.
        int
            Frame step size.
        int
            Frame value at the middle slider step (default).
        dict
            Updated dictionary storing frame slider parameters for each video.
        """
        video_name = pl.Path(video_path).name
        if video_name in frame_slider_storage.keys():
            stored_video_params = frame_slider_storage[video_name]
            num_frames = stored_video_params["max"]
            frame_step = stored_video_params["step"]
            middle_frame = stored_video_params["value"]
            return num_frames - 1, frame_step, middle_frame, dash.no_update
        else:
            num_frames = int(utils.get_num_frames(video_path))
            # Round the frame step to the nearest 1000
            frame_step = round(int(num_frames / 4), -3)
            # Default to the middle step
            middle_frame = frame_step * 2
            frame_slider_storage[video_name] = {
                "max": num_frames - 1,
                "step": frame_step,
                "value": middle_frame,
            }
            return (
                num_frames - 1,
                frame_step,
                middle_frame,
                frame_slider_storage,
            )

    @app.callback(
        Output("roi-table", "data"),
        [
            Input("video-select", "value"),
            Input("roi-storage", "data"),
        ],
    )
    def update_roi_table(
        video_path: str, roi_storage: dict
    ) -> Optional[list[dict]]:
        """
        Update the ROI table with the ROI names and
        their corresponding colors.
        Parameters
        ----------
        video_path : str
            Path to the video file.
        roi_storage : dict
            Dictionary storing ROI data for each video.
        Returns
        -------
        list[dict]
            List of dictionaries with ROI table data.
        """
        if video_path is not None:
            video_name = pl.Path(video_path).name
            if video_name not in roi_storage.keys():
                roi_storage[video_name] = {"shapes": []}
            roi_table = [
                utils.stored_shape_to_table_row(shape)
                for shape in roi_storage[video_name]["shapes"]
            ]
            return roi_table
        else:
            return dash.no_update

    @app.callback(
        Output("roi-table", "style_data_conditional"),
        Input("roi-table", "data"),
        State("roi-colors-storage", "data"),
    )
    def set_roi_color_in_table(
        roi_table: list, roi_color_mapping: dict
    ) -> list:
        """
        Set the color of the ROI names in the ROI table
        based on the color assigned to that ROI shape.
        Parameters
        ----------
        roi_table : list
            List of dictionaries with ROI table data.
        roi_color_mapping : dict
            Dictionary with the following keys:
                - roi2color: dict mapping ROI names to colors
                - color2roi: dict mapping colors to ROI names
        Returns
        -------
        list[dict]
            List of dictionaries with conditional formatting
            rules for the ROI table.
        """
        if len(roi_table) == 0:
            return dash.no_update
        else:
            cond_format = []
            roi2color = roi_color_mapping["roi2color"]
            for roi in roi2color.keys():
                cond_format.append(
                    {
                        "if": {
                            "column_id": "name",
                            "filter_query": f"{{name}} = {roi}",
                        },
                        "color": roi2color[roi],
                    }
                )
            return cond_format

    @app.callback(
        Output("roi-storage", "data"),
        [
            Input("frame-graph", "relayoutData"),
            Input("load-rois-button", "n_clicks"),
        ],
        [
            State("video-select", "value"),
            State("frame-slider", "value"),
            State("roi-storage", "data"),
            State("roi-colors-storage", "data"),
        ],
    )
    def update_roi_storage(
        graph_relayout: dict,
        load_clicks: int,
        video_path: str,
        frame_num: int,
        roi_storage: dict,
        roi_color_mapping: dict,
    ) -> dict:
        """
        Update the ROI storage with the latest ROI shapes
        drawn on the frame graph or with the ROI shapes
        loaded from the video's .metadata.yaml file.
        Parameters
        ----------
        graph_relayout : dict
            Dictionary with information about the latest
            changes to the frame graph.
        load_clicks : int
            Number of times the load ROIs button has been clicked.
        video_path : str
            Path to the video file.
        frame_num : int
            Frame number.
        roi_storage : dict
            Dictionary storing ROI data for each video.
        roi_color_mapping : dict
            Dictionary with the following keys:
                - roi2color: dict mapping ROI names to colors
                - color2roi: dict mapping colors to ROI names
        Returns
        -------
        dict
            Updated dictionary storing ROI data for each video.
        """

        trigger = dash.callback_context.triggered[0]["prop_id"]
        video_path_pl = pl.Path(video_path)
        video_name = video_path_pl.name
        # Create a storage entry for the video if it doesn't exist
        if video_name not in roi_storage.keys():
            roi_storage[video_name] = {"shapes": []}

        # Stuff to do when a shape is drawn/deleted/modified on the graph
        if trigger == "frame-graph.relayoutData":
            if "shapes" in graph_relayout.keys():
                # this means that whole shapes have been created or deleted

                # Get the shapes from the graph
                graph_shapes = graph_relayout["shapes"]
                # Get the stored shapes for the video
                stored_shapes = roi_storage[video_name]["shapes"]

                # Figure out which stored shapes are no longer in the graph
                # (i.e. have been deleted)
                deleted_shapes_i = [
                    i
                    for i, shape in enumerate(stored_shapes)
                    if not utils.shape_in_list(graph_shapes)(shape)
                ]
                # remove the deleted shapes from the storage
                for i in sorted(deleted_shapes_i, reverse=True):
                    del roi_storage[video_name]["shapes"][i]

                # Figure out which graph shapes are new (not in storage)
                new_shapes_i = [
                    i
                    for i, shape in enumerate(graph_shapes)
                    if not utils.shape_in_list(stored_shapes)(shape)
                ]
                new_graph_shapes = [graph_shapes[i] for i in new_shapes_i]
                # Add the frame number and the ROI name to the new shapes
                for shape in new_graph_shapes:
                    shape["drawn_on_frame"] = frame_num
                    shape["roi_name"] = roi_color_mapping["color2roi"][
                        shape["line"]["color"]
                    ]
                # Pass the new shapes to the storage
                roi_storage[video_name]["shapes"] += new_graph_shapes

            elif re.match("shapes\[[0-9]+\].", list(graph_relayout.keys())[0]):
                # this means that a single shape has been edited
                # So update only that shape in storage
                for key in graph_relayout.keys():
                    shape_i = int(re.findall(r"\d+", key)[0])
                    shape_attr = key.split(".")[-1]
                    roi_storage[video_name]["shapes"][shape_i][
                        shape_attr
                    ] = graph_relayout[key]
                    roi_storage[video_name]["shapes"][shape_i][
                        "drawn_on_frame"
                    ] = frame_num

            else:
                # this means that the graph was zoomed/panned
                return dash.no_update

        # If triggered by the load ROIs button click
        # Load the ROIs from the metadata file
        # CAUTION! This will overwrite any ROIs is the roi-storage
        elif trigger == "load-rois-button.n_clicks":
            if load_clicks > 0:
                metadata_path = video_path_pl.with_suffix(".metadata.yaml")
                roi_storage[video_name]["shapes"] = utils.load_rois_from_yaml(
                    yaml_path=metadata_path
                )

        return roi_storage

    @app.callback(
        [
            Output("frame-graph", "figure"),
            Output("frame-status-alert", "children"),
            Output("frame-status-alert", "color"),
            Output("frame-status-alert", "is_open"),
        ],
        [
            Input("video-select", "value"),
            Input("frame-slider", "value"),
            Input("roi-select", "value"),
            Input("roi-storage", "data"),
        ],
        [
            State("frame-graph", "figure"),
            State("roi-colors-storage", "data"),
        ],
    )
    def update_frame_graph(
        video_path: str,
        frame_num: int,
        roi_name: str,
        roi_storage: dict,
        current_fig: go.Figure,
        roi_color_mapping: dict,
    ) -> tuple[go.Figure, str, str, bool]:
        """
        Update the frame graph
        Parameters
        ----------
        video_path : str
            Path to the video file.
        frame_num : int
            Frame number (which video frame to display).
        roi_name : str
            Name of the next ROI to be drawn.
        roi_storage : dict
            Dictionary storing already drawn ROI shapes.
        current_fig : plotly.graph_objects.Figure
            Current frame graph figure.
        roi_color_mapping : dict
            Dictionary with the following keys:
                - roi2color: dict mapping ROI names to colors
                - color2roi: dict mapping colors to ROI names
        Returns
        -------
        plotly.graph_objects.Figure.Figure
            Updated frame graph figure
        str
            Message to display in the frame status alert.
        str
            Color of the frame status alert.
        bool
            Whether to open the frame status alert.
        """

        # Get the video path and file name
        video_path_pl = pl.Path(video_path)
        video_name = video_path_pl.name

        # Load the stored shapes for this video (if any)
        graph_shapes = []
        if video_name in roi_storage.keys():
            stored_shapes = roi_storage[video_name]["shapes"]
            # Get rid of the custom keys that we added
            graph_shapes = [
                utils.shape_drop_custom_keys(shape) for shape in stored_shapes
            ]
        # Get the color for the next ROI
        next_shape_color = roi_color_mapping["roi2color"][roi_name]

        trigger = dash.callback_context.triggered[0]["prop_id"]
        # If triggered by an update of the roi-storage
        # maintain the current figure and only update the shapes
        if trigger == "roi-storage.data":
            current_fig["layout"]["shapes"] = graph_shapes
            return current_fig, dash.no_update, dash.no_update, dash.no_update

        # If triggered by a change in the ROI dropdown
        # maintain the current figure and only update the new shape color
        elif trigger == "roi-select.value":
            current_fig["layout"]["newshape"]["line"][
                "color"
            ] = next_shape_color
            return current_fig, dash.no_update, dash.no_update, dash.no_update

        # If triggered by a change in the video or frame
        # Load the frame into a new figure
        else:
            try:
                frame_filepath = utils.cache_frame(video_path_pl, frame_num)
                new_frame = Image.open(frame_filepath)
                # Put the frame in a figure
                new_fig = px.imshow(new_frame)
                # Add the stored shapes and set the next ROI color
                new_fig.update_layout(
                    shapes=graph_shapes,
                    newshape_line_color=next_shape_color,
                    dragmode="drawclosedpath",
                    margin=dict(l=0, r=0, t=0, b=0),
                    yaxis={"visible": False, "showticklabels": False},
                    xaxis={"visible": False, "showticklabels": False},
                )
                alert_msg = f"Showing frame {frame_num} from {video_name}."
                alert_color = "success"
                alert_open = True
                return new_fig, alert_msg, alert_color, alert_open
            except Exception as e:
                print(e)
                alert_msg = (
                    f"Could not extract frames from {video_name}. "
                    f"Make sure that it is a valid video file."
                )
                alert_color = "danger"
                alert_open = True
                return dash.no_update, alert_msg, alert_color, alert_open

    @app.callback(
        [
            Output("save-rois-button", "download"),
            Output("rois-status-alert", "children"),
            Output("rois-status-alert", "color"),
            Output("rois-status-alert", "is_open"),
        ],
        [
            Input("save-rois-button", "n_clicks"),
            Input("roi-storage", "data"),
            Input("video-select", "value"),
        ],
    )
    def save_rois_and_update_status_alert(
        save_clicks: int,
        roi_storage: dict,
        video_path: str,
    ) -> tuple[str, str, str, bool]:
        """
        Save the ROI shapes to a metadata YAML file
        and update the ROI status alert accordingly.
        Parameters
        ----------
        save_clicks : int
            Number of times the save ROIs button has been clicked.
        roi_storage : dict
            Dictionary storing already drawn ROI shapes.
        video_path : str
            Path to the video file.
        Returns
        -------
        str
            Download path to the metadata YAML file.
        str
            Message to display in the ROI status alert.
        str
            Color of the ROI status alert.
        bool
            Whether to open the ROI status alert.
        """
        # Get what triggered the callback
        trigger = dash.callback_context.triggered[0]["prop_id"]
        # Get the paths to the video and metadata files
        video_path_pl = pl.Path(video_path)
        video_name = video_path_pl.name
        metadata_filepath = video_path_pl.with_suffix(".metadata.yaml")

        # Check if the metadata file exists
        # and load any previously saved ROIs
        if metadata_filepath.exists():
            with open(metadata_filepath, "r") as yaml_file:
                metadata = yaml.safe_load(yaml_file)
                if "ROIs" in metadata.keys():
                    saved_rois = metadata["ROIs"]
                else:
                    saved_rois = []
        else:
            alert_msg = f"Could not find {metadata_filepath.name}"
            alert_color = "danger"
            return dash.no_update, alert_msg, alert_color, True

        # Get the stored ROI shapes for this video
        if video_name in roi_storage.keys():
            roi_shapes = roi_storage[video_name]["shapes"]
            rois_to_save = [
                utils.stored_shape_to_yaml_entry(shape) for shape in roi_shapes
            ]
        else:
            rois_to_save = []

        if rois_to_save:
            if trigger == "roi-storage.data" and rois_to_save == saved_rois:
                # This means that the ROIs have just been loaded
                alert_msg = f"Loaded ROIs from {metadata_filepath.name}"
                alert_color = "success"
                return dash.no_update, alert_msg, alert_color, True
            elif trigger == "roi-storage.data" and rois_to_save != saved_rois:
                # This means that the ROIs have been modified
                # in respect to the metadata file
                alert_msg = "Detected unsaved changes to ROIs."
                alert_color = "warning"
                return dash.no_update, alert_msg, alert_color, True
            else:
                if save_clicks > 0:
                    # This means that the user wants to save the ROIs
                    # This overwrites any previously saved ROIs
                    with open(metadata_filepath, "w") as yaml_file:
                        metadata["ROIs"] = rois_to_save
                        yaml.safe_dump(metadata, yaml_file)
                    alert_msg = f"Saved ROIs to {metadata_filepath.name}"
                    alert_color = "success"
                    return (
                        metadata_filepath.as_posix(),
                        alert_msg,
                        alert_color,
                        True,
                    )
                else:
                    return dash.no_update, dash.no_update, dash.no_update, True

        else:
            alert_msg = "No ROIs to save."
            alert_color = "light"
            return dash.no_update, alert_msg, alert_color, True