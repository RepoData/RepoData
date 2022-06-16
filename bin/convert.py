#!/usr/bin/env python

import csv
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
    filtered_row = {k: None if not v else v for k, v in row.items()}
    return filtered_row

if __name__ == "__main__":
    convert()
