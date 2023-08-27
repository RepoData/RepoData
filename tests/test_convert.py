import pandas

from pathlib import Path
from convert import create_json, create_geojson

example_csv = Path(__file__).parent / "data" / "example.csv"
temp_dir = Path('tests/data/temp')

def test_json_convert():
    temp_file = temp_dir / 'data.json'
    create_json(temp_file)
    assert Path(temp_file).is_file(), 'json file exists'
    curr_data = pandas.read_json('data.json', orient='records')
    new_data = pandas.read_json(temp_file, orient='records')
    assert curr_data.equals(new_data), 'json is up to date'

def test_geojson_convert():
    temp_file = temp_dir / 'data.geojson'
    create_geojson(temp_file)
    assert Path(temp_file).is_file(), 'geojson file exists'
    curr_data = pandas.read_json('data.geojson', orient='records')
    new_data = pandas.read_json(temp_file, orient='records')
    assert curr_data.equals(new_data), 'geojson is up to date'
