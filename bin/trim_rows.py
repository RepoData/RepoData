#!/usr/bin/env python

""" Trims all rows to a specified length to avoid extra cells

    Usage:
    python trim_rows.py
"""

import csv
from os import rename
from os.path import join, dirname, abspath

source_path = join(abspath(dirname(__file__)), '..', 'data.csv')
out_path = join(abspath(dirname(__file__)), '..', 'data_trim.csv')

row_length = 24


def trim_rows():
    with open(source_path, 'r') as source_file, open(out_path, 'w') as out_file:
        csvreader = csv.reader(source_file)
        csvwriter = csv.writer(out_file)
        for row in csvreader:
            csvwriter.writerow(row[:row_length])
        source_file.close()
        out_file.close()

        rename(out_path, source_path)


if __name__ == "__main__":
    trim_rows()
