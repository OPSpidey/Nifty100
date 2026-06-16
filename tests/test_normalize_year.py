from src.etl.normalizer import normalize_year


def test_dec_2012():
    assert normalize_year("Dec 2012") == 2012


def test_mar_2015():
    assert normalize_year("Mar 2015") == 2015


def test_plain_year():
    assert normalize_year("2018") == 2018


def test_spaces():
    assert normalize_year(" 2020 ") == 2020


def test_none():
    assert normalize_year(None) is None


import pytest
from src.etl.normalizer import normalize_year

@pytest.mark.parametrize(
    "value,expected",
    [
        ("Dec 2012", 2012),
        ("Mar 2013", 2013),
        ("Mar 2014", 2014),
        ("Mar 2015", 2015),
        ("Mar 2016", 2016),
        ("Mar 2017", 2017),
        ("Mar 2018", 2018),
        ("Mar 2019", 2019),
        ("Mar 2020", 2020),
        ("Mar 2021", 2021),
        ("Mar 2022", 2022),
        ("Mar 2023", 2023),
        ("2010", 2010),
        ("2011", 2011),
        (" 2012 ", 2012),
        ("FY2013", 2013),
        ("Year 2014", 2014),
        ("Q1 2015", 2015),
        ("Q2 2016", 2016),
        (None, None),
    ]
)
def test_normalize_year_cases(value, expected):
    assert normalize_year(value) == expected