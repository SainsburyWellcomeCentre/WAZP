import shutil
import sys
from pathlib import Path
from typing import Optional

import cv2
import ffmpeg
import yaml
from file_utils import check_file_io_safety


def ensure_clip_fits_in_video(
    start_frame: int,
    end_frame: int,
    n_frames: int,
):
    """Raise appropriate error if clip does not fit in video.

    Parameters
    ----------
    start_frame : int
        Starting frame of clip.
    end_frame : int
        Ending frame of clip.
    n_frames : int
        Number of frames in video.
    """

    if start_frame < 0:
        raise ValueError("Start frame must be >= 0.")
    elif start_frame >= n_frames:
        raise ValueError(f"Start frame must be < number of frames ({n_frames}).")
    elif end_frame > n_frames:
        raise ValueError(f"End frame exceeds number of frames ({n_frames}).")


def copy_video_metadata_file(
    input_video: Path,
    output_video: Path,
    overwrite: bool = True,
    clear_rois: bool = True,
    clear_events: bool = True,
):
    """Copy YAML metadata file from one video to another.

    The metadata file is assumed to be named as {video_name}.metadata.yaml
    and to be in the same directory as the video file.
    This function additionally updates the copied metadata file, if necessary:
    - The "File" field is updated to the match the output video file name.
    - The "ROIs" and "Events" fields are cleared if requested.

    Parameters
    ----------
    input_video : pathlib Path
        Path to input video file.
    output_video : pathlib Path
        Path to output video file.
    overwrite : bool, optional
        Whether to overwrite the output metadata file if it already exists,
        by default True
    clear_rois : bool, optional
        Whether to clear the "ROIs" field in the metadata file, by default True
    clear_events : bool, optional
        Whether to clear the "Events" field in the metadata file, by default True
    """

    input_metadata = input_video.parent / f"{input_video.stem}.metadata.yaml"
    output_metadata = output_video.parent / f"{output_video.stem}.metadata.yaml"
    if check_file_io_safety(input_metadata, output_metadata, overwrite=overwrite):
        shutil.copy(input_metadata, output_metadata)
        print(f"Copied metadata file from {input_metadata} to {output_metadata}")

        # Update the "File" field in the metadata file if necessary
        # Also start with clean "ROIs" and "Events" fields
        if output_video.name != input_video.name:
            with open(output_metadata, "r") as f:
                metadata = yaml.safe_load(f)
            metadata["File"] = output_video.name
            if clear_rois:
                metadata["ROIs"] = ""
            if clear_events:
                metadata["Events"] = ""
            with open(output_metadata, "w") as f:
                yaml.dump(metadata, f, sort_keys=False)
            print(f"Updated output metadata file: {output_metadata}")


def compress_video(
    input_video: Path,
    output_video: Optional[Path] = None,
    overwrite: bool = False,
    codec: str = "libx264",
    crf: int = 23,
    copy_metadata: bool = True,
):
    """Compress a video file using ffmpeg.

    Parameters
    ----------
    input_video : pathlib Path
        Path to input video file.
    output_video : pathlib Path, optional
        Path to output video file.
        If not specified, it will be the same as the input file,
        but the suffix will be changed to '.mp4'.
    overwrite : bool, optional
        Whether to overwrite the output video file if it already exists,
        by default False
    codec : str, optional
        ffmpeg video codec to use, by default 'libx264'
        Should be one of the codecs supported by ffmpeg.
    crf : int, optional
        Constant Rate Factor for compression, by default 23.
        Higher values mean more compression, lower values mean better quality.
    copy_metadata
        Whether to copy the metadata from the input video file to the output
        video file, by default True.
    """

    if output_video is None:
        output_video = input_video.with_suffix(".mp4")

    if check_file_io_safety(input_video, output_video, overwrite=overwrite):
        print(f"Compressing video: {input_video}")

        # Get ffmpeg command
        process = ffmpeg.input(input_video.as_posix(), y=None).output(
            output_video.as_posix(), vcodec=codec, crf=crf, y=None
        )
        try:
            process.run()
        except ffmpeg.Error as e:
            print(e.stderr.decode(), file=sys.stderr)
            raise RuntimeError("Error running ffmpeg.") from e

        print(f"Compressed video saved to: {output_video}")

        if copy_metadata:
            copy_video_metadata_file(input_video, output_video, overwrite=overwrite)


def extract_clip_from_video(
    input_video: Path,
    output_clip: Path,
    start_frame: int = 0,
    clip_duration: int = 30,
    overwrite: bool = False,
    copy_metadata: bool = True,
):
    """Extract a clip from a video file.

    Clips are zero-indexed, i.e. the first frame is frame 0.
    So if you want to extract frames 0-29, aka the first 30 frames,
    you would set start_frame=0 and clip_duration=30.

    Parameters
    ----------
    input_video : pathlib Path
        Path to the input video file.
    output_clip : pathlib Path
        Path to the output clip file.
    start_frame : int, optional
        Starting frame, by default 0
    clip_duration : int, optional
        Clip duration in frames, by default 30
    overwrite : bool, optional
        Whether to overwrite the output clip file if it already exists,
    copy_metadata : bool, optional
        Whether to copy the metadata from the input video file to the output
        video file, by default True.
    """

    if check_file_io_safety(input_video, output_clip, overwrite=overwrite):
        print(f"Extracting clip from {input_video}...")
        end_frame = start_frame + clip_duration

        # initialise capture and videowriter
        cap = cv2.VideoCapture(str(input_video))
        fourcc = cv2.VideoWriter_fourcc("m", "p", "4", "v")
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        print(f"Frame width: {frame_width} pixels")
        print(f"Frame height: {frame_height} pixels")
        print(f"Frame rate: {fps} fps")
        videowriter = cv2.VideoWriter(
            output_clip.as_posix(),
            fourcc,
            fps,
            (frame_width, frame_height),
        )

        # Ensure that clip fits in video
        n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        ensure_clip_fits_in_video(start_frame, end_frame, n_frames)

        # Set capture to start frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        # Extract clip
        count = 0
        while count < end_frame:
            # read frame
            success_frame, frame = cap.read()
            # if not successfully read, exit
            if not success_frame:
                print("Can't receive frame. Exiting ...")
                break
                # write frame to video
            # if frame within clip bounds: write to video
            if (count >= start_frame) and (count < end_frame):
                videowriter.write(frame)
            count += 1

        # Release everything if job is finished
        cap.release()
        videowriter.release()
        cv2.destroyAllWindows()

        print(f"Saved clip to: {output_clip}")
        print(f"Clip duration: {clip_duration} frames = {clip_duration / fps:.3f} sec")

        if copy_metadata:
            copy_video_metadata_file(input_video, output_clip, overwrite=overwrite)


def copy_entire_video(
    input_video: Path,
    output_video: Path,
    overwrite: bool = False,
    copy_metadata: bool = True,
):
    """Copy an entire video file.

    Parameters
    ----------
    input_video : pathlib Path
        Path to input video file.
    output_video : pathlib Path
        Path to output video file.
    overwrite : bool, optional
        Whether to overwrite the output video file if it already exists,
        by default False.
    copy_metadata : bool, optional
        Whether to copy the metadata from the input video file to the output
        video file, by default True.
    """

    if check_file_io_safety(input_video, output_video, overwrite=overwrite):
        shutil.copy(input_video, output_video)
        msg = f"Copied {input_video} to: {output_video}"
        if copy_metadata:
            copy_video_metadata_file(input_video, output_video, overwrite=overwrite)
            msg += ", including the metadata file."
        print(msg)
