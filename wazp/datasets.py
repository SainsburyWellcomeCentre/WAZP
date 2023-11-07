"""Module for fetching and loading sample datasets.

This module provides functions for fetching and loading data used in tests,
examples, and tutorials. The data are stored in a remote repository on GIN
and are downloaded to the user's local machine the first time they are used.
"""

from pathlib import Path

import pooch
import yaml

# URL to GIN data repository where the experimental data are hosted
DATA_URL = "https://gin.g-node.org/SainsburyWellcomeCentre/WAZP/raw/master"

# Data to be downloaded and cached in ~/.WAZP/sample_data
LOCAL_DATA_DIR = Path("~", ".WAZP", "sample_data").expanduser()
LOCAL_DATA_DIR.mkdir(parents=True, exist_ok=True)

# A pooch download manager that keeps track of available sample projects.
# The path to each file is "base_url + registry_key"
sample_projects = pooch.create(
    path=LOCAL_DATA_DIR,
    base_url=f"{DATA_URL}/",
    registry={
        "jewel-wasp/short-clips_raw.zip": "7fab80e68af5b90a4633e886b06bebefd7d400c5d8acc23e1693ecfd8d344f0d",  # noqa: E501
        "jewel-wasp/short-clips_compressed.zip": "2b4a6a4b00c6a41eae71d10e74dff61d5a2bb7d2b627db6edb59abae0e18aaee",  # noqa: E501
        "jewel-wasp/entire-video_raw.zip": "f587c8e60b9df3b4664a6587a624abdcf401263b86ba0268c0b5a0f8e89f5167",  # noqa: E501
        "jewel-wasp/entire-video_compressed.zip": "d2c5d4e4febc9eca1d523cb113b004fe6368a3d63bde5206cef04ef576c6a042",  # noqa: E501
    },
)


def find_sample_projects(registry: pooch.Pooch = sample_projects) -> dict:
    """Find all available projects in the remote data repository.

    Parameters
    ----------
    registry : pooch.Pooch
        A pooch download manager object that keeps track of available projects.
        Default: wazp.datasets.sample_projects

    Returns
    -------
    dict
        A dictionary with species names as keys and a list of available projects
        as values.
    """
    projects_per_species = {}
    for key in registry.registry.keys():
        species, kind = key.split("/")
        kind = kind.split(".")[0]
        if species not in projects_per_species:
            projects_per_species[species] = [kind]
        else:
            if kind not in projects_per_species[species]:
                projects_per_species[species].append(kind)

    return projects_per_species


def get_sample_project(
    species_name: str = "jewel-wasp",
    project_name: str = "short-clips_compressed",
    progressbar: bool = True,
) -> Path:
    """Return the local path to a sample project.

    The project is downloaded from the remote data repository on GIN, unzipped
    and cached under ~/.WAZP/sample_data. If the project has already been
    downloaded, the cached version is used. The paths in the WAZP project config
    file are updated to point to the downloaded project.

    Parameters
    ----------
    species_name : str
        Name of the species to download. Currently only "jewel-wasp" is available.
        Default: "jewel-wasp".
    project_name : str
        Name of the project to download. You can find the available projects
        per species by calling `wazp.datasets.find_sample_projects()`.
        Default: "short-clips_compressed".
    progressbar : bool
        Whether to show a progress bar while downloading the data. Default: True.

    Returns
    -------
    pathlib.Path
        Path to the downloaded project (unzipped folder)
    """

    projects_per_species = find_sample_projects(sample_projects)
    if species_name not in projects_per_species.keys():
        raise ValueError(
            f"Species {species_name} not found. "
            f"Available species: {projects_per_species.keys()}"
        )
    if project_name not in projects_per_species[species_name]:
        raise ValueError(
            f"Project name {project_name} not found for species {species_name}. "
            f"Available project names: {projects_per_species[species_name]}"
        )

    species_project_name = f"{species_name}/{project_name}.zip"
    sample_projects.fetch(
        species_project_name,
        progressbar=progressbar,
        processor=pooch.Unzip(extract_dir=LOCAL_DATA_DIR / species_name),
    )

    project_path = LOCAL_DATA_DIR / species_name / project_name
    _update_paths_in_project_config(project_path)
    return project_path


def _update_paths_in_project_config(
    sample_project_path: Path,
):
    """Update the paths in the WAZP project config file to point to the downloaded
    project on the local machine.

    Parameters
    ----------
    sample_project_path : pathlib Path
        Path to the downloaded project (unzipped folder) on the local machine.
    """
    config_file = sample_project_path / "WAZP_config.yaml"

    with open(config_file, "r") as f:
        yaml_dict = yaml.safe_load(f)

    yaml_dict["videos_dir_path"] = (
        (sample_project_path / "videos").absolute().as_posix()
    )
    yaml_dict["pose_estimation_results_path"] = (
        (sample_project_path / "pose_estimation_results").absolute().as_posix()
    )
    yaml_dict["metadata_fields_file_path"] = (
        (sample_project_path / "metadata_fields.yaml").absolute().as_posix()
    )
    yaml_dict["dashboard_export_data_path"] = (
        (sample_project_path / "wazp_output").absolute().as_posix()
    )

    with open(config_file, "w") as f:
        yaml.dump(yaml_dict, f, sort_keys=False)
