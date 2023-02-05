import glob
import tempfile

import pytest
import yaml

from wazp.utils import df_from_metadata_yaml_files


def get_sample_project_metadata_fields() -> dict:
    """Get the metadata dictionary from the sample project for testing."""
    with open("sample_project/metadata_fields.yaml") as fi:
        metadata_fields = yaml.safe_load(fi)
    return metadata_fields


def test_df_from_metadata_yaml_sample_project_metadata() -> None:
    """Normal operation: test we can read the sample project metadata."""
    fields = get_sample_project_metadata_fields()
    testme = df_from_metadata_yaml_files("sample_project/videos", fields)

    expected = set(fields)
    actual = set(testme.columns)
    diff = expected.symmetric_difference(actual)
    assert expected == actual, f"Metadata fields -> df problem with: {diff}"

    nfiles = len(glob.glob("sample_project/videos/*.yaml"))
    nrows, _ = testme.shape
    assert nrows == nfiles, "Number of rows in df != number of yaml files."


def test_df_from_metadata_yaml_no_metadata() -> None:
    """
    Test with no metadata files (expect just to create an empty dataframe with
    metadata_fields column headers).
    """
    fields = get_sample_project_metadata_fields()
    with tempfile.TemporaryDirectory() as empty_existing_directory:
        testme = df_from_metadata_yaml_files(empty_existing_directory, fields)

    assert testme.shape == (1, len(fields))


def test_df_from_metadata_garbage() -> None:
    """Check we don't get metadata for things that don't exist."""
    with pytest.raises(FileNotFoundError):
        df_from_metadata_yaml_files("DIRECTORY_DOESNT_EXIST", dict())

    with tempfile.TemporaryDirectory() as empty_existing_directory:
        testme = df_from_metadata_yaml_files(empty_existing_directory, dict())
    assert testme.empty, "There shouldn't be any data in the df."
