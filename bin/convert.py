#!/usr/bin/env python

""" Converts XLSX files to CSV and JSON

    Usage:
    python convert.py
"""

import csv
import json
import openpyxl
import os
import sys

root_dir = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
source_dir = os.path.join(root_dir, 'excel')
valid_cols = 23

class SourceFile():
    def __init__(self, filepath):
        self.filepath = filepath

    def load_data(self):
        try:
            wb = openpyxl.load_workbook(self.filepath)
            return wb.active
        except Exception as e:
            print("Error loading data: {}".format(e))
            return False


class DestinationFile():
    def get_filepath(self, extension):
        return "{}{}".format(os.path.join(root_dir, 'data'), extension)

    def get_key(self, cell):
        key = ''
        if cell.value:
            key = cell.value.replace("*", "")
            key = key.lower()
            key = key.replace(" ", "_")
            key = key.replace("(", "")
            key = key.replace(")", "")
        return key

    def get_value(self, cell):
        if not cell.value:
            return None
        if cell.data_type == 'n':
            if float(cell.value).is_integer():
                return int(cell.value)
            return float(cell.value)
        else:
            return str(cell.value)

    def write_csv(self):
        print("Creating CSV")

        destination = self.get_filepath('.csv')
        wrote_header = False

        with open(destination, 'w') as f:
            csv_writer = csv.writer(f)
            for f in os.listdir(source_dir):
                print('converting', f)
                source = SourceFile(os.path.join(source_dir, f))
                self.data = source.load_data()
                rows = list(self.data)

                if not wrote_header:
                    headers = [self.get_key(h) for h in rows[0]]
                    # remove empty column headers
                    headers = filter(lambda s: s != '', headers)
                    csv_writer.writerow(headers)
                    wrote_header = True

                for r in rows[1:]:
                    new_row = []
                    for cell in r[0:valid_cols]:
                        new_row.append(self.get_value(cell) if cell.value else '')
                    if not all('' == s or s.isspace() for s in new_row):
                        csv_writer.writerow(new_row)
        print("CSV saved")

    def write_json(self):
        print("Creating JSON")
        destination = self.get_filepath('.json')
        array = []
        for f in os.listdir(source_dir):
            print('converting', f)
            source = SourceFile(os.path.join(source_dir, f))
            self.data = source.load_data()
            rows = list(self.data)
            for x in range(1, len(rows)):
                part = {}
                for n in range(0, valid_cols):
                    val = self.get_value(rows[x][n])
                    key = self.get_key(rows[0][n])
                    part[key] = val
                array.append(part)
        with open(destination, 'w') as f:
            f.write(json.dumps(array, sort_keys=True, indent=4,
                    separators=(',', ': ')))
        print("JSON saved")

    def write_all(self):
        self.write_csv()
        self.write_json()

for f in ['data.csv', 'data.json']:
    if os.path.isfile(os.path.join(root_dir, f)):
        os.remove(os.path.join(root_dir, f))

destination = DestinationFile()
destination.write_all()
