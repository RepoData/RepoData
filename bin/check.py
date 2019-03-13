#!/usr/bin/env python

""" Ensures all column headers in XSLX files match

    Usage:
    python check.py
"""

import csv
import openpyxl

from os import listdir
from os.path import join, dirname, abspath

excel_dir = join(abspath(dirname(__file__)), '..', 'excel')

def check_column_headers():
    expected = None

    for excel_file in listdir(excel_dir):
        path = join(excel_dir, excel_file)
        sheet = openpyxl.load_workbook(path).active

        found = set([c.value for c in next(sheet.iter_rows())])

        # assumes first file (AK.xlsx) is canonical
        if expected is None:
            expected = found

        diff = expected.symmetric_difference(found)
        if diff:
            print(excel_file, diff)

if __name__ == "__main__":
    check_column_headers()
