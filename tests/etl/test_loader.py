from pathlib import Path

import pandas as pd
import pytest

from src.etl.loader import (
    FILES,
    load_excel,
    load_source_file,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

def test_files_dictionary_exists():
    assert isinstance(FILES, dict)
    assert len(FILES) == 12


@pytest.mark.parametrize(
    "filename",
    list(FILES.keys()),
)
def test_file_registered(filename):
    assert filename in FILES


@pytest.mark.parametrize(
    "filename",
    list(FILES.keys()),
)
def test_file_path_exists(filename):
    path, _ = FILES[filename]
    assert (PROJECT_ROOT / path).exists()


@pytest.mark.parametrize(
    "filename",
    list(FILES.keys()),
)
def test_load_source_returns_dataframe(filename):

    path, header = FILES[filename]

    df = load_source_file(
        PROJECT_ROOT / path,
        header,
    )

    assert isinstance(df, pd.DataFrame)


@pytest.mark.parametrize(
    "filename",
    list(FILES.keys()),
)
def test_dataframe_not_empty(filename):

    path, header = FILES[filename]

    df = load_source_file(
        PROJECT_ROOT / path,
        header,
    )

    assert len(df) > 0


@pytest.mark.parametrize(
    "filename",
    list(FILES.keys()),
)
def test_column_names_lowercase(filename):

    path, header = FILES[filename]

    df = load_source_file(
        PROJECT_ROOT / path,
        header,
    )

    assert all(
        c == c.lower()
        for c in df.columns
    )


@pytest.mark.parametrize(
    "filename",
    list(FILES.keys()),
)
def test_column_names_trimmed(filename):

    path, header = FILES[filename]

    df = load_source_file(
        PROJECT_ROOT / path,
        header,
    )

    assert all(
        c == c.strip()
        for c in df.columns
    )


def test_load_excel_returns_dataframe():

    df = load_excel(
        PROJECT_ROOT / "data/raw/analysis.xlsx"
    )

    assert isinstance(df, pd.DataFrame)


def test_load_excel_not_empty():

    df = load_excel(
        PROJECT_ROOT / "data/raw/analysis.xlsx"
    )

    assert len(df) > 0


def test_load_excel_columns_normalized():

    df = load_excel(
        PROJECT_ROOT / "data/raw/analysis.xlsx"
    )

    for col in df.columns:
        assert col == col.lower()
        assert " " not in col