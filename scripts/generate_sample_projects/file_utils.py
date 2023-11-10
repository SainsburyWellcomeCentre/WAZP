from pathlib import Path

import yaml


def update_wazp_config_file(
    config_file: Path,
    model_str: str,
    videos_dir_path: Path,
    pose_estimation_results_path: Path,
):
    """Update the WAZP project config file.

    Parameters
    ----------
    config_file : pathlib Path
        Path to WAZP project config file.
    model_str : str
        Name of model DLC model used for pose estimation.
    videos_dir_path : pathlib Path
        Path to directory containing videos.
    pose_estimation_results_path : pathlib Path
        Path to directory containing pose estimation results.
    """

    if not config_file.is_file():
        raise FileNotFoundError(f"File not found: {config_file}")

    with open(config_file.as_posix(), "r") as f:
        yaml_dict = yaml.safe_load(f)

    yaml_dict["model_str"] = model_str
    yaml_dict["videos_dir_path"] = videos_dir_path.as_posix()
    yaml_dict["pose_estimation_results_path"] = pose_estimation_results_path.as_posix()

    # We assume that the metadata fields file and dashboard export data path
    # are in the same directory as the config file
    metadata_fields_file_path = (config_file.parent / "metadata_fields.yaml").as_posix()
    yaml_dict["metadata_fields_file_path"] = metadata_fields_file_path
    dashboard_export_data_path = (config_file.parent / "wazp_output").as_posix()
    yaml_dict["dashboard_export_data_path"] = dashboard_export_data_path

    with open(config_file.as_posix(), "w") as f:
        yaml.dump(yaml_dict, f, sort_keys=False)


def check_file_io_safety(input_file: Path, output_file: Path, overwrite: bool = False):
    """Check if input and output files are safe to use.

    This function raises an error if:
    - The input file does not exist.
    - The input and output files are the same.
    - The output file exists and overwrite is False.

    If the output file exists and overwrite is True, the output file is deleted to
    prep for writing.

    Parameters
    ----------
    input_file : pathlib Path
        Path to input file.
    output_file : pathlib Path
        Path to output file.
    overwrite : bool, optional
        Whether overwriting output file is allowed, by default False

    Returns
    -------
    bool
        Whether it is safe to proceed with file IO.
    """

    proceed = False
    if not input_file.is_file():
        raise FileNotFoundError(f"File not found: {input_file}")
    elif output_file == input_file:
        raise ValueError("Input and output files are the same.")
    elif output_file.is_file() and not overwrite:
        print(f"Output file already exists: {output_file}")
    elif output_file.is_file() and overwrite:
        output_file.unlink()
        print(f"Deleted existing output file: {output_file}")
        proceed = True
    else:
        proceed = True

    return proceed
