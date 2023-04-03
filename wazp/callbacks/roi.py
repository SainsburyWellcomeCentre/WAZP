import pathlib as pl

# import pdb
import re
import time
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
            roi_names = config["ROI_tags"]
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
            Maximum frame index value.
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
            max_frame_idx = stored_video_params["max"]
            frame_step = stored_video_params["step"]
            middle_frame = stored_video_params["value"]
            return max_frame_idx, frame_step, middle_frame, dash.no_update
        else:
            try:
                num_frames = utils.get_num_frames(video_path)
            except RuntimeError as e:
                print(e)
                # If the number of frames cannot be extracted,
                # return a negative frame value.
                # This will trigger an alert message in the app
                return dash.no_update, dash.no_update, -1, dash.no_update

            # Divide the number of frames into 4 steps
            frame_step = int(num_frames / 4)
            # Round to the nearest 1000 if step is > 1000
            if frame_step > 1000:
                frame_step = int(frame_step / 1000) * 1000

            # Default to the middle step
            middle_frame = frame_step * 2
            max_frame_idx = num_frames - 1
            frame_slider_storage[video_name] = {
                "max": max_frame_idx,
                "step": frame_step,
                "value": middle_frame,
            }
            return (
                max_frame_idx,
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
        [
            Output("roi-storage", "data"),
            Output("roi-table", "selected_rows"),
        ],
        [
            Input("frame-graph", "relayoutData"),
            Input("load-rois-button", "n_clicks"),
            Input("delete-rois-button", "n_clicks"),
        ],
        [
            State("video-select", "value"),
            State("frame-slider", "value"),
            State("roi-storage", "data"),
            State("roi-colors-storage", "data"),
            State("roi-table", "data"),
            State("roi-table", "selected_rows"),
        ],
    )
    def update_roi_storage(
        graph_relayout: dict,
        load_clicks: int,
        delete_clicks: int,
        video_path: str,
        frame_num: int,
        roi_storage: dict,
        roi_color_mapping: dict,
        roi_table_rows: list,
        roi_table_selected_rows: list,
    ) -> tuple[dict, list]:
        """
        Update the ROI storage, when:
        - Shapes are added/removed from the frame graph
        - Shapes are edited on the frame graph
        - Shapes are loaded from file
        - Shapes are deleted from the ROI table

        Parameters
        ----------
        graph_relayout : dict
            Dictionary with information about the latest
            changes to the frame graph.
        load_clicks : int
            Number of times the load ROIs button has been clicked.
        delete_clicks : int
            Number of times the delete ROIs button has been clicked.
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
        roi_table_rows : list
            List of dictionaries with ROI table data.
        roi_table_selected_rows : list
            List of indices for the selected rows in the ROI table.

        Returns
        -------
        dict
            Updated dictionary storing ROI data for each video.
        list
            List of indices for the selected rows in the ROI table.
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

        # If triggered by the delete ROIs button click
        # Delete the selected ROIs from the roi-storage
        elif trigger == "delete-rois-button.n_clicks":
            if delete_clicks > 0 and roi_table_selected_rows:
                deleted_roi_names = [
                    roi_table_rows[idx]["name"]
                    for idx in roi_table_selected_rows
                ]
                stored_shapes = roi_storage[video_name]["shapes"]
                roi_storage[video_name]["shapes"] = [
                    sh
                    for sh in stored_shapes
                    if sh["roi_name"] not in deleted_roi_names
                ]
                # Clear the row selection
                roi_table_selected_rows = []

        return roi_storage, roi_table_selected_rows

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
            State("frame-slider", "max"),
        ],
    )
    def update_frame_graph(
        video_path: str,
        shown_frame_idx: int,
        roi_name: str,
        roi_storage: dict,
        current_fig: go.Figure,
        roi_color_mapping: dict,
        max_frame_idx: int,
    ) -> tuple[go.Figure, str, str, bool]:
        """
        Update the frame graph

        Parameters
        ----------
        video_path : str
            Path to the video file.
        shown_frame_idx : int
            Index of the frame to be shown.
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
        max_frame_idx : int
            Maximum frame index (num_frames - 1)

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
        int
            Maximum frame index (num_frames - 1)
        """

        # If a negative frame index is passed, it means that the video
        # could not be read correctly. So don't update the frame,
        # but display an alert message
        if shown_frame_idx < 0:
            alert_msg = f"Could not read from '{video_path}'. "
            alert_msg += "Is this a valid video file?"
            return dash.no_update, alert_msg, "danger", True

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
                frame_filepath = utils.cache_frame(
                    video_path_pl, shown_frame_idx
                )
            except RuntimeError as e:
                return dash.no_update, str(e), "danger", True

            new_frame = Image.open(frame_filepath)
            new_fig = px.imshow(new_frame)
            # Add the stored shapes and set the nextROI color
            new_fig.update_layout(
                shapes=graph_shapes,
                newshape_line_color=next_shape_color,
                dragmode="drawclosedpath",
                margin=dict(l=0, r=0, t=0, b=0),
                yaxis={"visible": False, "showticklabels": False},
                xaxis={"visible": False, "showticklabels": False},
            )
            alert_msg = f"Showing frame {shown_frame_idx}/{max_frame_idx}"
            return new_fig, alert_msg, "light", True

    @app.callback(
        Output("save-rois-button", "download"),
        Input("save-rois-button", "n_clicks"),
        [
            State("video-select", "value"),
            State("roi-storage", "data"),
        ],
    )
    def save_rois_to_file(
        save_clicks: int,
        video_path: str,
        roi_storage: dict,
    ) -> str:
        """
        Save the ROI shapes to a metadata YAML file.

        Parameters
        ----------
        save_clicks : int
            Number of times the save ROIs button has been clicked.
        video_path : str
            Path to the video file.
        roi_storage : dict
            Dictionary storing ROI shapes in the app.

        Returns
        -------
        str
            Download link for the metadata YAML file.
        """
        if save_clicks > 0:
            # Get the paths to the video and metadata files
            video_path_pl = pl.Path(video_path)
            video_name = video_path_pl.name
            metadata_filepath = video_path_pl.with_suffix(".metadata.yaml")

            # Get the metadata from the YAML file
            with open(metadata_filepath, "r") as yaml_file:
                metadata = yaml.safe_load(yaml_file)

            # Get the video's ROI shapes in the app
            rois_in_app = roi_storage[video_name]["shapes"]
            # Add the ROI shapes to the metadata and save
            with open(metadata_filepath, "w") as yaml_file:
                metadata["ROIs"] = [
                    utils.stored_shape_to_yaml_entry(shape)
                    for shape in rois_in_app
                ]
                yaml.safe_dump(metadata, yaml_file, sort_keys=False)

            # Return the download link
            return metadata_filepath.as_posix()
        else:
            return dash.no_update

    @app.callback(
        [
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
    def update_roi_status_alert(
        save_clicks: int,
        roi_storage: dict,
        video_path: str,
    ) -> tuple[str, str, bool]:
        """
        Update the ROI status alert to inform the user about ROIs defined
        in the app and their relation to those saved in the metadata file.

        Parameters
        ----------
        save_clicks : int
            Number of times the save ROIs button has been clicked.
        roi_storage : dict
            Dictionary storing ROI shapes in the app.
        video_path : str
            Path to the video file.

        Returns
        -------
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
        metadata_path = video_path_pl.with_suffix(".metadata.yaml")

        # If triggered by a click on the save ROIs button
        # return with a success message
        if trigger == "save-rois-button.n_clicks":
            alert_msg = f"Saved ROIs to '{metadata_path.name}'"
            alert_color = "success"
            return alert_msg, alert_color, True

        # Load saved ROIs from the metadata file, if any
        try:
            rois_in_file = utils.load_rois_from_yaml(metadata_path)
        except FileNotFoundError:
            alert_msg = f"Could not find {metadata_path.name}"
            alert_color = "danger"
            return alert_msg, alert_color, True
        except KeyError:
            rois_in_file = []

        # Get the app's ROI shapes for this video
        rois_in_app = []
        if video_name in roi_storage.keys():
            rois_in_app = roi_storage[video_name]["shapes"]

        if not rois_in_app:
            alert_color = "light"
            if rois_in_file:
                alert_msg = (
                    f"Found {len(rois_in_file)} ROIs in '{metadata_path.name}'"
                )
            else:
                alert_msg = "No ROIs defined in the metadata file."

        else:
            # Some ROIs exist in the app
            if rois_in_app == rois_in_file:
                alert_color = "success"
                if trigger == "roi-storage.data":
                    alert_msg = f"Loaded ROIs from '{metadata_path.name}'"
                else:
                    alert_msg = (
                        f"Shown ROIs match those in '{metadata_path.name}'"
                    )

            else:
                alert_color = "warning"
                alert_msg = "Detected unsaved changes to ROIs."

        return alert_msg, alert_color, True

    @app.callback(
        Output("save-rois-button", "disabled"),
        Input("roi-storage", "data"),
        Input("video-select", "value"),
    )
    def disable_save_rois_button(
        roi_storage: dict,
        video_path: str,
    ) -> bool:
        """If there are no ROIs in the app or if the metadata file
        does not exist, disable the save ROIs button.

        Parameters
        ----------
        roi_storage : dict
            Dictionary storing ROI shapes in the app.
        video_path : str
            Path to the selected video file.

        Returns
        -------
        bool
            Whether to enable the save ROIs button.
        """

        video_path_pl = pl.Path(video_path)
        video_name = video_path_pl.name
        metadata_path = video_path_pl.with_suffix(".metadata.yaml")

        rois_in_app = []
        if video_name in roi_storage.keys():
            rois_in_app = roi_storage[video_name]["shapes"]

        no_rois_to_save = len(rois_in_app) == 0
        metadata_file_does_not_exist = not metadata_path.is_file()
        return no_rois_to_save or metadata_file_does_not_exist

    @app.callback(
        Output("load-rois-button", "disabled"),
        [
            Input("save-rois-button", "n_clicks"),
            Input("video-select", "value"),
        ],
    )
    def disable_load_rois_button(
        save_clicks: int,
        video_path: str,
    ) -> bool:
        """If there are no ROIs saved in the metadata file,
        disable the 'Load all from file' button.

        Parameters
        ----------
        save_clicks : int
            Number of times the save ROIs button has been clicked.
        video_path : str
            Path to the selected video file.

        Returns
        -------
        bool
            Whether to enable the load ROIs button.
        """

        video_path_pl = pl.Path(video_path)
        metadata_path = video_path_pl.with_suffix(".metadata.yaml")

        # If triggered by a click on the save ROIs button,
        # wait a few seconds before checking for ROIs in the file
        trigger = dash.callback_context.triggered[0]["prop_id"]
        if trigger == "save-rois-button.n_clicks" and save_clicks > 1:
            time.sleep(2)

        try:
            saved_shapes = utils.load_rois_from_yaml(yaml_path=metadata_path)
            return len(saved_shapes) == 0
        except (FileNotFoundError, KeyError):
            return True

    @app.callback(
        Output("delete-rois-button", "disabled"),
        Input("roi-table", "selected_rows"),
    )
    def disable_delete_rois_button(
        selected_rows: list,
    ) -> bool:
        """If there are no ROIs selected in the ROI table,
        disable the 'Delete selected' button


        Parameters
        ----------
        selected_rows : list
            List of selected rows.

        Returns
        -------
        bool
            Whether to enable the delete ROIs button.
        """
        return len(selected_rows) == 0
