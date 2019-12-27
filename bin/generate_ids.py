#!/usr/bin/env python

""" Generates unique identifiers for repositories

    Usage:
    python generate_ids.py
"""

import csv
import shortuuid

from os import rename
from os.path import join, dirname, abspath

source_path = join(abspath(dirname(__file__)), '..', 'data.csv')
out_path = join(abspath(dirname(__file__)), '..', 'data_ids.csv')

shortuuid.set_alphabet("23456789abcdefghijkmnopqrstuvwxyz")

def generate_ids():
    with open(source_path, 'r') as source_file, open(out_path, 'w') as out_file:
        csvreader = csv.DictReader(source_file)
        fieldnames = ['ID'] + csvreader.fieldnames if "ID" not in csvreader.fieldnames else csvreader.fieldnames
        csvwriter = csv.DictWriter(out_file, fieldnames, extrasaction='ignore')
        csvwriter.writeheader()
        for node, row in enumerate(csvreader, 1):
            identifier = row.get("ID") if row.get("ID") else shortuuid.uuid()
            csvwriter.writerow(dict(row, ID=identifier))
        source_file.close()
        out_file.close()

        rename(out_path, source_path)

if __name__ == "__main__":
    generate_ids()
