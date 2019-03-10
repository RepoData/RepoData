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
parser.add_argument('-o', '--output', default='all', choices=['csv', 'json', 'geojson'],
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
            print "Error loading data: {}".format(e)
            return False


class DestinationFile():
    def __init__(self, data):
        self.data = data

    def get_filepath(self, extension):
        return "{}{}".format(os.path.join(root_dir, 'data'), extension)

    def get_value(self, cell):
        if not cell.value:
            return None
        if cell.data_type == 'n':
            if float(cell.value).is_integer():
                return int(cell.value)
            return float(cell.value)
        else:
            return unicode(cell.value)

    def write_csv(self):
        try:
            destination = self.get_filepath('.csv')
            with open(destination, 'ab') as f:
                c = csv.writer(f)
                for r in self.data.rows:
                    new_row = []
                    for cell in r:
                        value = unicode(cell.value) if cell.value else ''
                        new_row.append(value.encode('utf-8'))
                    if not all('' == s or s.isspace() for s in new_row):
                        c.writerow(new_row)
            print "CSV saved"
        except Exception as e:
            print "Error creating CSV file: {}".format(e)

    def write_json(self):
        try:
            destination = self.get_filepath('.json')
            rows = list(self.data)
            array = []
            if os.path.isfile(destination):
                with open(destination) as json_file:
                    array = json.load(json_file)
            for x in range(1, len(rows)):
                part = {}
                for n in range(0, 23):
                    val = self.get_value(rows[x][n])
                    part[rows[0][n].value.replace("*", "")] = val
                array.append(part)
            with open(destination, 'wb') as f:
                f.write(json.dumps(array, sort_keys=True, indent=4,
                        separators=(',', ': ')))
            print "JSON saved"
        except Exception as e:
            print "Error creating JSON file: {}".format(e)

    def write_all(self):
        self.write_csv()
        self.write_json()

for f in ['data.csv', 'data.json']:
    if os.path.isfile(os.path.join(root_dir, f)):
        os.remove(os.path.join(root_dir, f))
for f in os.listdir(source_dir):
    print "Converting", f
    source = SourceFile(os.path.join(source_dir, f))
    data = source.load_data()
    destination = DestinationFile(data)
    getattr(destination, 'write_{}'.format(args.output))()
