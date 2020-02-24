#!/usr/bin/env python

""" Adds latitude, longitude and geocoding confidence data.

    Usage:
    python geocode.py [geodata_path]
"""

import argparse
import csv
import openpyxl

from os import rename
from os.path import join, dirname, abspath

source_path = join(abspath(dirname(__file__)), '..', 'data.csv')
out_path = join(abspath(dirname(__file__)), '..', 'data_geocode.csv')

LAT_IDX = 50
LONG_IDX = 51
CONF_IDX = 3
ID_IDX = 69


def from_geodata(geodata_dict, identifier):
    try:
        row = geodata_dict[identifier]
        return row["latitude"], row["longitude"], row["confidence"]
    except KeyError:
        return None, None, None


def create_geodata_dict(geodata_path):
    dict = {}
    geodata = openpyxl.load_workbook(geodata_path).active
    for row in geodata.iter_rows():
        dict.update(
            {row[ID_IDX].value: {
                "latitude": row[LAT_IDX].value,
                "longitude": row[LONG_IDX].value,
                "confidence": row[CONF_IDX].value}})
    return dict


def generate_ids(geodata_path):
    geodata_dict = create_geodata_dict(geodata_path)
    with open(source_path, 'r') as source_file, open(out_path, 'w') as out_file:
        csvreader = csv.DictReader(source_file)
        fieldnames = csvreader.fieldnames + ["geocode_confidence"] \
            if "geocode_confidence" not in csvreader.fieldnames \
            else csvreader.fieldnames
        csvwriter = csv.DictWriter(out_file, fieldnames, extrasaction='ignore')
        csvwriter.writeheader()
        for node, row in enumerate(csvreader, 1):
            latitude, longitude, confidence = from_geodata(geodata_dict, row["id"])
            csvwriter.writerow(dict(
                row,
                latitude=latitude,
                longitude=longitude,
                geocode_confidence=confidence
            ))
        source_file.close()
        out_file.close()

        rename(out_path, source_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Adds latitude, longitude and geocoding confidence data."
    )
    parser.add_argument("geodata_path", help="Path to geodata in Excel format")
    args = parser.parse_args()
    generate_ids(args.geodata_path)
