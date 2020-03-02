#!/usr/bin/env python3

import json

repos = json.load(open('data.json'))

geojson = {
    "type": "FeatureCollection",
    "features": []
}

for repo in repos:
    if repo['latitude'] and repo['longitude']:
        geojson['features'].append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [repo["longitude"], repo["latitude"]]
            },
            "properties": repo
        })

json.dump(geojson, open('data.geojson', 'w'), indent=2)
