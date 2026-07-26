import pandas as pd

from src.dq.rules import validate_dataframe


def check(df, rule):
    issues = validate_dataframe(df)
    assert any(i["rule_id"] == rule for i in issues)


def test_dq001():
    check(pd.DataFrame({"company_id":[None]}), "DQ001")


def test_dq002():
    check(pd.DataFrame({"year":[None]}), "DQ002")


def test_dq003():
    check(pd.DataFrame({"sales": [-1]}), "DQ003")


def test_dq004():
    check(pd.DataFrame({"net_profit":[None]}), "DQ004")


def test_dq005():
    check(pd.DataFrame({"equity":[0]}), "DQ005")


def test_dq006():
    check(pd.DataFrame({"borrowings":[-10]}), "DQ006")


def test_dq007():
    check(pd.DataFrame({"interest":[-1]}), "DQ007")


def test_dq008():
    check(pd.DataFrame({"cashflow":[None]}), "DQ008")


def test_dq009():
    check(pd.DataFrame({"roe":[150]}), "DQ009")


def test_dq010():
    check(pd.DataFrame({"roce":[120]}), "DQ010")


def test_dq011():
    check(pd.DataFrame({"pe_ratio":[-5]}), "DQ011")


def test_dq012():
    check(pd.DataFrame({"market_cap":[0]}), "DQ012")


def test_dq013():
    check(pd.DataFrame({"dividend_yield":[-1]}), "DQ013")


def test_dq014():
    df = pd.DataFrame(
        {
            "company_id":["ABB", "ABB"],
            "year":[2024, 2024],
        }
    )

    check(df, "DQ014")

def test_valid_dataframe():
    df = pd.DataFrame({
        "company_id": ["ABB"],
        "year": [2024],
        "sales": [100],
        "net_profit": [20],
        "equity": [50],
        "borrowings": [10],
        "interest": [5],
        "cashflow": [15],
        "roe": [20],
        "roce": [18],
        "pe_ratio": [25],
        "market_cap": [1000],
        "dividend_yield": [2],
    })

    assert validate_dataframe(df) == []