#!/usr/bin/env python

""" Converts XLSX files to CSV

    Usage:
    python convert.py -o [output format]
"""

import argparse
import csv
import json
import openpyxl
import os
import sys

root_dir = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
source_dir = os.path.join(root_dir, 'excel')

parser = argparse.ArgumentParser(description='Convert XLSX files to CSV')
parser.add_argument('-o', '--output', default='all', choices=['csv', 'json'],
                    help='output format', )
args = parser.parse_args()


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
        if cell.value:
            return cell.value.replace("*", "")
        return ''

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
        try:
            destination = self.get_filepath('.csv')
            with open(destination, 'w') as f:
                csv_writer = csv.writer(f)
                for f in os.listdir(source_dir):
                    print('converting', f)
                    source = SourceFile(os.path.join(source_dir, f))
                    self.data = source.load_data()
                    for r in self.data.iter_rows(min_row=2):
                        new_row = []
                        for cell in r:
                            new_row.append(self.get_value(cell) if cell.value else '')
                        if not all('' == s or s.isspace() for s in new_row):
                            csv_writer.writerow(new_row)
            print("CSV saved")
        except Exception as e:
            print("Error creating CSV file: {}".format(e))

    def write_json(self):
        print("Creating JSON")
        try:
            destination = self.get_filepath('.json')
            array = []
            for f in os.listdir(source_dir):
                print('converting', f)
                source = SourceFile(os.path.join(source_dir, f))
                self.data = source.load_data()
                rows = list(self.data)
                for x in range(1, len(rows)):
                    part = {}
                    for n in range(0, 23):
                        val = self.get_value(rows[x][n])
                        key = self.get_key(rows[0][n])
                        part[key] = val
                    array.append(part)
            with open(destination, 'w') as f:
                f.write(json.dumps(array, sort_keys=True, indent=4,
                        separators=(',', ': ')))
            print("JSON saved")
        except Exception as e:
            print("Error creating JSON file: {}".format(e))

    def write_all(self):
        self.write_csv()
        self.write_json()

for f in ['data.csv', 'data.json']:
    if os.path.isfile(os.path.join(root_dir, f)):
        os.remove(os.path.join(root_dir, f))
destination = DestinationFile()
getattr(destination, 'write_{}'.format(args.output))()
