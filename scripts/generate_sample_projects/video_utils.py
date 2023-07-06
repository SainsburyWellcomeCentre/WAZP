import pathlib as pl
import shutil
import sys
from typing import Optional

import cv2
import ffmpeg
import yaml


def ensure_file_exists(path: pl.Path):
    """Raise FileNotFoundError if file does not exist."""
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")


def ensure_file_does_not_exist(path: pl.Path):
    """Raise FileExistsError if file already exists."""
    if path.is_file():
        raise FileExistsError(f"File already exists: {path}")


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
    input_video: pl.Path,
    output_video: pl.Path,
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
    input_video : pl.Path
        Path to input video file.
    output_video : pl.Path
        Path to output video file.
    clear_rois : bool, optional
        Whether to clear the "ROIs" field in the metadata file, by default True
    clear_events : bool, optional
        Whether to clear the "Events" field in the metadata file, by default True
    """

    # Check if metadata file exists
    input_metadata = input_video.parent / f"{input_video.stem}.metadata.yaml"
    ensure_file_exists(input_metadata)

    # Copy metadata file
    output_metadata = output_video.parent / f"{output_video.stem}.metadata.yaml"
    ensure_file_does_not_exist(output_metadata)
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
            yaml.dump(metadata, f)
        print(f"Updated output metadata file: {output_metadata}")


def compress_video(
    input_video: pl.Path,
    output_video: Optional[pl.Path] = None,
    codec: str = "libx264",
    crf: int = 23,
    copy_metadata: bool = True,
):
    """Compress a video file using ffmpeg.

    Parameters
    ----------
    input_video : pl.Path
        Path to input video file.
    output_video : pl.Path, optional
        Path to output video file.
        If not specified, it will be the same as the input file,
        but the suffix will be changed to '.mp4'.
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

    ensure_file_exists(input_video)
    if output_video is None:
        output_video = input_video.with_suffix(".mp4")
    ensure_file_does_not_exist(output_video)

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
        copy_video_metadata_file(input_video, output_video)


def extract_clip_from_video(
    video_file: pl.Path,
    start_frame: int = 0,
    clip_duration: int = 30,
    output_dir: Optional[pl.Path] = None,
    output_filename: Optional[str] = None,
    copy_metadata: bool = True,
):
    """Extract a clip from a video file.

    Clips are zero-indexed, i.e. the first frame is frame 0.
    So if you want to extract frames 0-29, aka the first 30 frames,
    you would set start_frame=0 and clip_duration=30.

    Parameters
    ----------
    video_file : pl.Path
        Path to video file.
    start_frame : int, optional
        Starting frame, by default 0
    clip_duration : int, optional
        Clip duration in frames, by default 30
    output_dir : pl.Path, optional
        output directory, by default the same directory as the video file.
        If non-existent, it will be created.
    output_filename : str, optional
        output file name, by default the same as the input file name,
        suffixed with the start and end frame numbers.
    copy_metadata : bool, optional
        Whether to copy the metadata from the input video file to the output
        video file, by default True.
    """

    ensure_file_exists(video_file)

    print("-" * 80)
    print(f"Extracting clip from {video_file}...")
    print(f"Start frame: {start_frame}")
    print(f"Clip duration: {clip_duration} frames")
    end_frame = start_frame + clip_duration
    print(f"End frame: {end_frame}")

    # Get output file directory, name, and path
    if output_dir is None:
        output_dir = video_file.parent
    output_dir.mkdir(exist_ok=True, parents=True)

    if output_filename is None:
        clip_suffix = f"_clip-{start_frame}-{end_frame}"
        output_filename = video_file.stem + clip_suffix + video_file.suffix

    output_file = output_dir / output_filename

    # initialise capture and videowriter
    cap = cv2.VideoCapture(str(video_file))
    fourcc = cv2.VideoWriter_fourcc("m", "p", "4", "v")
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"Frame width: {frame_width} pixels")
    print(f"Frame height: {frame_height} pixels")
    print(f"Frame rate: {fps} fps")
    videowriter = cv2.VideoWriter(
        output_file.as_posix(),
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

    print(f"Saved clip to: {output_file}")
    print(f"Clip duration: {clip_duration} frames = {clip_duration / fps:.3f} seconds")

    if copy_metadata:
        copy_video_metadata_file(video_file, output_file)
