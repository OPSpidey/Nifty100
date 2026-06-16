import re
import pandas as pd


def normalize_year(value):
    """
    Converts:
    Dec 2012 -> 2012
    Mar 2015 -> 2015
    2018 -> 2018
    """

    if pd.isna(value):
        return None

    value = str(value).strip()

    match = re.search(r"(19|20)\d{2}", value)

    if match:
        return int(match.group())

    return None


def normalize_ticker(value):
    """
    ABB -> ABB
    abb -> ABB
    abb ltd -> ABBLTD
    """

    if pd.isna(value):
        return None

    value = str(value).strip().upper()

    value = re.sub(r"[^A-Z0-9]", "", value)

    return value if value else None