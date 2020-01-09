#!/usr/bin/env python

import csv
import json

def convert():
    repos = []
    for row in csv.DictReader(open('data.csv')):
        repos.append(row)
    json.dump(repos, open('data.json', 'w'), indent=2)

if __name__ == "__main__":
    convert()


