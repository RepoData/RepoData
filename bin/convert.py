#!/usr/bin/env python3

import csv
import json

from datetime import datetime
from os.path import join, dirname, abspath

source_path = join(abspath(dirname(__file__)), '..', 'data.csv')
json_path = join(abspath(dirname(__file__)), '..', 'data.json')
geojson_path = join(abspath(dirname(__file__)), '..', 'data.geojson')

def convert():
    create_json()
    create_geojson()

def create_json(json_path=json_path):
    """Dumps JSON representation of each row of `data.csv` to `data.json`."""
    repos = []
    for row in csv.DictReader(open(source_path)):
        repos.append(filter_row(row))
    json.dump(repos, open(json_path, 'w'), indent=2)

def create_geojson(geojson_path=geojson_path):
    """Creates a GeoJSON FeatureCollection for all repositories in `data.csv`."""
    geojson = {
        "type": "FeatureCollection",
        "features": []
    }
    for repo in csv.DictReader(open(source_path)):
        repo = filter_row(repo)
        if repo['latitude'] and repo['longitude']:
            geojson['features'].append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [repo["longitude"], repo["latitude"]]
                },
                "properties": repo
            })
    json.dump(geojson, open(geojson_path, 'w'), indent=2)


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
