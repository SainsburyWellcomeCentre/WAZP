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


def test_columns_names_and_nrows_in_df_from_metadata() -> None:
    """Normal operation: test we can read the sample project metadata."""
    metadata_fields = get_sample_project_metadata_fields()
    df_output = df_from_metadata_yaml_files(
        "sample_project/videos", metadata_fields
    )

    fields_from_yaml = set(metadata_fields)
    df_columns = set(df_output.columns)
    diff = fields_from_yaml.symmetric_difference(df_columns)
    assert (
        fields_from_yaml == df_columns
    ), f"Metadata fields and df columns differ in the following fields: {diff}"

    nfiles = len(glob.glob("sample_project/videos/*.yaml"))
    nrows, _ = df_output.shape
    assert nrows == nfiles, "Number of rows in df != number of yaml files."


def test_df_from_metadata_yaml_no_metadata() -> None:
    """
    Test with no metadata files (expect just to create an empty dataframe with
    metadata_fields column headers).
    """
    metadata_fields = get_sample_project_metadata_fields()
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
        df_output = df_from_metadata_yaml_files(
            empty_existing_directory, dict()
        )
    assert df_output.empty, "There shouldn't be any data in the df."
