#!/usr/bin/env python

import csv
from datetime import datetime
import json

def convert():
    repos = []
    for row in csv.DictReader(open('data.csv')):
        repos.append(filter_row(row))
    json.dump(repos, open('data.json', 'w'), indent=2)

def filter_row(row):
    """Filters row data.

    Converts empty strings to none.
    """
    filtered_row = {k: None if not v else coerce_type(v, k) for k, v in row.items()}
    return filtered_row

def coerce_type(value, key):
    """Converts fields to their appropriate data type."""
    if key in ["st_zip_code_5_numbers", "st_zip_code_4_following_numbers"]:
        return int(value)
    elif key in ["latitude", "longitude", "geocode_confidence"]:
        return float(value)
    elif key == "date_entry_recorded":
        parsed = datetime.fromisoformat(value)
        return parsed.isoformat()
    else:
        return value

if __name__ == "__main__":
    convert()
