from contextvars import copy_context

import pytest
from dash._callback_context import context_value
from dash._utils import AttributeDict

from wazp.callbacks.metadata import generate_yaml_files_from_csv

expected_yaml_fields = [
    "File",
    "Species_name",
    "Common_name",
    "Subject",
    "Treatment",
    "Treatment_description",
    "Date_start",
    "Time_start",
    "Date_end",
    "Time_end",
    "Time_recorded",
    "Video_length",
    "Hardware_description",
    "Software_description",
    "Further_description",
    "Events",
    "ROIs",
]


def test_generate_yaml_files_from_csv_callback() -> None:
    def run_callback():
        context_value.set(
            AttributeDict(
                **{
                    "triggered_inputs": [
                        {"prop_id": "upload-csv-ctx-example.contents"}
                    ]
                }
            )
        )
        return generate_yaml_files_from_csv(
            "",
            "sample_project/test_from_spreadsheet.xlsx",
            False,
            {
                "metadata_fields": {key: "" for key in expected_yaml_fields},
                "config": {
                    "videos_dir_path": "",
                    "metadata_key_field_str": "",
                },
            },
        )

    ctx = copy_context()
    _, message_text, _ = ctx.run(run_callback)
    assert (
        message_text
        == f"3 YAML files generated in video directory: . Please refresh the page to update the metadata table."
    )
