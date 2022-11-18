import csv
import json
import os


def csv_to_json(csv_file_path: str, field_str_key: str, json_file_path: str):
    """
    Convert input csv to json file, taking the value at the 'field_str_key' column as key for each entry

    Args:
        csv_file_path: path to input csv
        field_str_key: key for each entry in final json file
        json_file_path: path to output json

    Usage:
        metadata_utils.csv_to_json('./sample_metadata/master-list-sample.csv','File','./sample_metadata/master-list-sample.json')
    """
    rows_dict = {}
    with open(csv_file_path, "r", encoding="utf-8-sig") as csvf:
        csv_reader = csv.DictReader(csvf)

        for row in csv_reader:
            key = row[field_str_key]
            rows_dict[key] = row

    # write to json
    # TODO check if extension is included in json path?
    # if not json_file_path.endswith('.json')...
    with open(json_file_path, "w") as jsonf:
        json.dump(rows_dict, jsonf)


def csv_to_json_per_video(
    csv_file_path: str,
    field_str_key: str,  # name of the field with the 'key'; the key will also be filename
    json_parent_dir: str,
):
    """
    Convert input csv to a set of json files, one for each row entry.
    For each row, the value at the 'field_str_key' column is taken as the json filename

    Args:
        csv_file_path: path to input csv
        field_str_key: the value at the 'field_str_key' column is taken as the json filename
        json_parent_dir: path to parent directory for all json files

    Usage:
        metadata_utils.csv_to_json_per_video('./sample_metadata/master-list-sample.csv','File','./sample_metadata/')


    """
    rows_dict = {}
    with open(csv_file_path, "r", encoding="utf-8-sig") as csvf:
        csv_reader = csv.DictReader(csvf)

        for row in csv_reader:
            # extract key
            key = row[field_str_key]

            # write each row to json
            json_filename = os.path.splitext(key)[0] + ".json"
            with open(os.path.join(json_parent_dir, json_filename), "w") as jsonf:
                json.dump(row, jsonf)


##################
# Json files to csv
# - single
# - json files per video


###############
# Check files with missing metadata


############
# Add metadata entry?


######
# Visualise metadata
