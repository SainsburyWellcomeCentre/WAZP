import glob
import tempfile
from pathlib import Path

import pytest
import yaml

from wazp.datasets import get_sample_dataset
from wazp.utils import df_from_metadata_yaml_files


# Pytest fixture for getting a sample dataset
@pytest.fixture(scope="session")
def sample_project() -> Path:
    """Get the sample project for testing."""
    return get_sample_dataset("jewel-wasp", "short-clips_compressed", progressbar=True)


@pytest.fixture
def metadata_fields(sample_project) -> dict:
    """Get the metadata dictionary from the sample project for testing."""
    fields_file = sample_project / "metadata_fields.yaml"
    with open(fields_file) as fi:
        metadata_fields = yaml.safe_load(fi)
    return metadata_fields


def test_columns_names_and_nrows_in_df_from_metadata(
    sample_project, metadata_fields
) -> None:
    """Normal operation: test we can read the sample project metadata."""
    df_output = df_from_metadata_yaml_files(sample_project / "videos", metadata_fields)

    fields_from_yaml = set(metadata_fields)
    df_columns = set(df_output.columns)
    diff = fields_from_yaml.symmetric_difference(df_columns)
    # Ignore the "ROIs" column, which is absent from the metadata_fields.yaml
    if diff == {"ROIs"}:
        diff = set()
    assert (
        not diff
    ), f"Metadata fields and df columns differ in the following fields: {diff}"

    glob_pattern = (sample_project / "videos" / "*.yaml").as_posix()
    nfiles = len(glob.glob(glob_pattern))
    nrows, _ = df_output.shape
    assert nrows == nfiles, "Number of rows in df != number of yaml files."


def test_df_from_metadata_yaml_no_metadata(metadata_fields) -> None:
    """
    Test with no metadata files (expect just to create an empty dataframe with
    metadata_fields column headers).
    """
    with tempfile.TemporaryDirectory() as empty_existing_directory:
        df_output = df_from_metadata_yaml_files(
            empty_existing_directory, metadata_fields
        )

    assert df_output.shape == (1, len(metadata_fields))


def test_df_from_metadata_garbage() -> None:
    """Check we don't get metadata for things that don't exist."""
    with pytest.raises(FileNotFoundError):
        df_from_metadata_yaml_files("DIRECTORY_DOESNT_EXIST", dict())

    with tempfile.TemporaryDirectory() as empty_existing_directory:
        df_output = df_from_metadata_yaml_files(empty_existing_directory, dict())
    assert df_output.empty, "There shouldn't be any data in the df."
