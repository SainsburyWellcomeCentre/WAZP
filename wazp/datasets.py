"""Module for fetching and loading datasets.

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

# A pooch download manager that keeps track of available datasets.
# The path to each file is "base_url + registry_key"
sample_datasets = pooch.create(
    path=LOCAL_DATA_DIR,
    base_url=f"{DATA_URL}/",
    registry={
        "jewel-wasp/short-clips_raw.zip": "7fab80e68af5b90a4633e886b06bebefd7d400c5d8acc23e1693ecfd8d344f0d",  # noqa: E501
        "jewel-wasp/short-clips_compressed.zip": "2b4a6a4b00c6a41eae71d10e74dff61d5a2bb7d2b627db6edb59abae0e18aaee",  # noqa: E501
        "jewel-wasp/entire-video_raw.zip": "f587c8e60b9df3b4664a6587a624abdcf401263b86ba0268c0b5a0f8e89f5167",  # noqa: E501
        "jewel-wasp/entire-video_compressed.zip": "d2c5d4e4febc9eca1d523cb113b004fe6368a3d63bde5206cef04ef576c6a042",  # noqa: E501
    },
)


def find_sample_datasets(registry: pooch.Pooch = sample_datasets) -> dict:
    """Find all available datasets in the remote data repository.

    Parameters
    ----------
    registry : pooch.Pooch
        A pooch download manager object that keeps track of available datasets.
        Default: wazp.datasets.sample_datasets

    Returns
    -------
    dict
        A dictionary with species names as keys and a list of available datasets
        as values.
    """
    datasets_per_species = {}
    for key in registry.registry.keys():
        species, kind = key.split("/")
        kind = kind.split(".")[0]
        if species not in datasets_per_species:
            datasets_per_species[species] = [kind]
        else:
            if kind not in datasets_per_species[species]:
                datasets_per_species[species].append(kind)

    return datasets_per_species


def get_sample_dataset(
    species_name: str = "jewel-wasp",
    dataset_kind: str = "short-clips_compressed",
    progressbar: bool = True,
) -> Path:
    """Return the local path to a sample dataset.

    The dataset is downloaded from the remote data repository on GIN, unzipped
    and cached under ~/.WAZP/sample_data. If the dataset has already been
    downloaded, the cached version is used. The paths in the WAZP project config
    file are updated to point to the downloaded dataset.

    Parameters
    ----------
    species_name : str
        Name of the species to download. Currently only "jewel-wasp" is available.
        Default: "jewel-wasp".
    dataset_kind : str
        Which kind of dataset to download. You can find the available datasets
        per species by calling `wazp.datasets.find_sample_datasets()`.
        Default: "short-clips_compressed".
    progressbar : bool
        Whether to show a progress bar while downloading the data. Default: True.

    Returns
    -------
    pathlib.Path
        Path to the downloaded dataset (unzipped folder)
    """

    datasets_per_species = find_sample_datasets(sample_datasets)
    if species_name not in datasets_per_species.keys():
        raise ValueError(
            f"Species {species_name} not found. "
            f"Available species: {datasets_per_species.keys()}"
        )
    if dataset_kind not in datasets_per_species[species_name]:
        raise ValueError(
            f"Dataset kind {dataset_kind} not found for species {species_name}. "
            f"Available dataset kinds: {datasets_per_species[species_name]}"
        )

    full_dataset_name = f"{species_name}/{dataset_kind}.zip"
    sample_datasets.fetch(
        full_dataset_name,
        progressbar=progressbar,
        processor=pooch.Unzip(extract_dir=LOCAL_DATA_DIR / species_name),
    )

    dataset_path = LOCAL_DATA_DIR / species_name / dataset_kind
    _update_paths_in_project_config(dataset_path)
    return dataset_path


def _update_paths_in_project_config(
    sample_dataset_path: Path,
):
    """Update the paths in the WAZP project config file to point to the downloaded
    dataset on the local machine.

    Parameters
    ----------
    sample_dataset_path : pathlib Path
        Path to the downloaded dataset (unzipped folder) on the local machine.
    """
    config_file = sample_dataset_path / "WAZP_config.yaml"

    with open(config_file, "r") as f:
        yaml_dict = yaml.safe_load(f)

    yaml_dict["videos_dir_path"] = (
        (sample_dataset_path / "videos").absolute().as_posix()
    )
    yaml_dict["pose_estimation_results_path"] = (
        (sample_dataset_path / "pose_estimation_results").absolute().as_posix()
    )
    yaml_dict["metadata_fields_file_path"] = (
        (sample_dataset_path / "metadata_fields.yaml").absolute().as_posix()
    )
    yaml_dict["dashboard_export_data_path"] = (
        (sample_dataset_path / "wazp_output").absolute().as_posix()
    )

    with open(config_file, "w") as f:
        yaml.dump(yaml_dict, f, sort_keys=False)
