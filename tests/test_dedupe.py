from pathlib import Path

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

    assert isnan(mediator.df.loc["222vbsyz44jadgb2rcqyu5ibu3"].latitude)
    assert isnan(mediator.df.loc["222vbsyz44jadgb2rcqyu5ibu3"].longitude)

    mediator.copy(
        "latitude", "22ygfe9fkgvzd2m6qxrs4r7rj5", "222vbsyz44jadgb2rcqyu5ibu3"
    )
    mediator.copy(
        "longitude", "22ygfe9fkgvzd2m6qxrs4r7rj5", "222vbsyz44jadgb2rcqyu5ibu3"
    )

    assert mediator.df.loc["222vbsyz44jadgb2rcqyu5ibu3"].latitude == 41.6090744738
    assert mediator.df.loc["222vbsyz44jadgb2rcqyu5ibu3"].longitude == -88.2036374157

    mediator.undo()
    assert isnan(mediator.df.loc["222vbsyz44jadgb2rcqyu5ibu3"].longitude)

    mediator.undo()
    assert isnan(mediator.df.loc["222vbsyz44jadgb2rcqyu5ibu3"].latitude)
