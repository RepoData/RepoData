from pathlib import Path
from datetime import datetime

from numpy import isnan

from dedupe import DupeAnalyzer, DupeMediator

example_csv = Path(__file__).parent / "data" / "example.csv"


def test_dupes():
    analyzer = DupeAnalyzer(example_csv)
    results = analyzer.get_dupes()
    assert len(results) == 2, "found two sets of duplicates"
    assert results[0] == [
        "222vbsyz44jadgb2rcqyu5ibu3",
        "93lksjiwjflkdjeidjkej39slk",
        "hsj4od7s9zbkjf3diiuxxjp375",
    ]
    assert results[1] == ["232vyh8ebnagc3u9qa6rgqe2k2", "lslknbiwoflaoei293jf9wk39f"]


def test_no_pobox():
    analyzer = DupeAnalyzer(example_csv, no_pobox=True)
    results = analyzer.get_dupes()
    assert len(results) == 2, "found two sets of duplicates"
    assert results[0] == [
        "232vyh8ebnagc3u9qa6rgqe2k2",
        "lslknbiwoflaoei293jf9wk39f",
    ], "pobox wasn't included"
    assert results[1] == ["93lksjiwjflkdjeidjkej39slk", "hsj4od7s9zbkjf3diiuxxjp375"]


def test_recorded_by():
    analyzer = DupeAnalyzer(example_csv, entry_recorded_by="Eira Tansey")
    results = analyzer.get_dupes()
    assert len(results) == 1, "only included duplicates involving Eira"
    assert results[0] == [
        "222vbsyz44jadgb2rcqyu5ibu3",
        "93lksjiwjflkdjeidjkej39slk",
        "hsj4od7s9zbkjf3diiuxxjp375",
    ]


def test_delete():
    """Test deleting records from the dataset, and then undoing it."""
    mediator = DupeMediator(example_csv, DupeAnalyzer(example_csv).get_dupes())
    assert len(mediator.df) == 8

    mediator.delete("222vbsyz44jadgb2rcqyu5ibu3")
    assert len(mediator.df) == 7

    mediator.undo()
    assert len(mediator.df) == 8


def test_copy():
    """Test copying some properties from one record to another then undoing it."""
    mediator = DupeMediator(example_csv, DupeAnalyzer(example_csv).get_dupes())

    # currently latitude and longitude are not set for this record
    assert isnan(mediator.df.loc["222vbsyz44jadgb2rcqyu5ibu3"].latitude)
    assert isnan(mediator.df.loc["222vbsyz44jadgb2rcqyu5ibu3"].longitude)

    # copy them from a record where they are defined
    mediator.copy(
        "latitude", "22ygfe9fkgvzd2m6qxrs4r7rj5", "222vbsyz44jadgb2rcqyu5ibu3"
    )
    mediator.copy(
        "longitude", "22ygfe9fkgvzd2m6qxrs4r7rj5", "222vbsyz44jadgb2rcqyu5ibu3"
    )

    # make sure they are there
    assert mediator.df.loc["222vbsyz44jadgb2rcqyu5ibu3"].latitude == 41.6090744738
    assert mediator.df.loc["222vbsyz44jadgb2rcqyu5ibu3"].longitude == -88.2036374157

    # undo them and make sure they go back to their prervious value
    mediator.undo()
    assert isnan(mediator.df.loc["222vbsyz44jadgb2rcqyu5ibu3"].longitude)
    mediator.undo()
    assert isnan(mediator.df.loc["222vbsyz44jadgb2rcqyu5ibu3"].latitude)

def test_updated():
    """Editing a record should cause it to get a new date_entry_updated."""
    now = datetime.now()
    mediator = DupeMediator(example_csv, DupeAnalyzer(example_csv).get_dupes())
    mediator.copy(
        "latitude", "22ygfe9fkgvzd2m6qxrs4r7rj5", "222vbsyz44jadgb2rcqyu5ibu3"
    )
    mediator.next()
    assert mediator.df.loc['222vbsyz44jadgb2rcqyu5ibu3'].date_entry_updated > now

def test_save():
    """Saving the data with no edits should result in exact copy of the original."""
    mediator = DupeMediator(example_csv, [])
    copy_csv = example_csv.parent / "temp" / "copy.csv"
    mediator.save(copy_csv)
    assert copy_csv.open().read() == example_csv.open().read()
