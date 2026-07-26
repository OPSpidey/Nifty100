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