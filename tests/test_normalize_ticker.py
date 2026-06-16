from src.etl.normalizer import normalize_ticker


def test_upper():
    assert normalize_ticker("ABB") == "ABB"


def test_lower():
    assert normalize_ticker("abb") == "ABB"


def test_spaces():
    assert normalize_ticker(" abb ") == "ABB"


def test_special_chars():
    assert normalize_ticker("ABB-LTD") == "ABBLTD"


def test_none():
    assert normalize_ticker(None) is None


import pytest
from src.etl.normalizer import normalize_ticker

@pytest.mark.parametrize(
    "value,expected",
    [
        ("ABB", "ABB"),
        ("abb", "ABB"),
        (" abb ", "ABB"),
        ("ABB-LTD", "ABBLTD"),
        ("ABB LTD", "ABBLTD"),
        ("TCS", "TCS"),
        ("tcs", "TCS"),
        ("INFY", "INFY"),
        ("infy", "INFY"),
        ("RELIANCE", "RELIANCE"),
        ("RELIANCE ", "RELIANCE"),
        (" HDFC ", "HDFC"),
        ("LT", "LT"),
        ("M&M", "MM"),
        (None, None),
    ]
)
def test_normalize_ticker_cases(value, expected):
    assert normalize_ticker(value) == expected