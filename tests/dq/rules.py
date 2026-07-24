import pandas as pd


def validate_dataframe(df: pd.DataFrame):
    issues = []

    if "company_id" in df.columns and df["company_id"].isna().any():
        issues.append({"rule_id": "DQ001", "severity": "ERROR"})

    if "year" in df.columns and df["year"].isna().any():
        issues.append({"rule_id": "DQ002", "severity": "ERROR"})

    if "sales" in df.columns and (df["sales"] < 0).any():
        issues.append({"rule_id": "DQ003", "severity": "ERROR"})

    if "net_profit" in df.columns and df["net_profit"].isna().any():
        issues.append({"rule_id": "DQ004", "severity": "WARNING"})

    if "equity" in df.columns and (df["equity"] <= 0).any():
        issues.append({"rule_id": "DQ005", "severity": "WARNING"})

    if "borrowings" in df.columns and (df["borrowings"] < 0).any():
        issues.append({"rule_id": "DQ006", "severity": "ERROR"})

    if "interest" in df.columns and (df["interest"] < 0).any():
        issues.append({"rule_id": "DQ007", "severity": "WARNING"})

    if "cashflow" in df.columns and df["cashflow"].isna().any():
        issues.append({"rule_id": "DQ008", "severity": "ERROR"})

    if "roe" in df.columns and (df["roe"] > 100).any():
        issues.append({"rule_id": "DQ009", "severity": "WARNING"})

    if "roce" in df.columns and (df["roce"] > 100).any():
        issues.append({"rule_id": "DQ010", "severity": "ERROR"})

    if "pe_ratio" in df.columns and (df["pe_ratio"] < 0).any():
        issues.append({"rule_id": "DQ011", "severity": "WARNING"})

    if "market_cap" in df.columns and (df["market_cap"] <= 0).any():
        issues.append({"rule_id": "DQ012", "severity": "ERROR"})

    if "dividend_yield" in df.columns and (df["dividend_yield"] < 0).any():
        issues.append({"rule_id": "DQ013", "severity": "WARNING"})

    if df.duplicated().any():
        issues.append({"rule_id": "DQ014", "severity": "ERROR"})

    return issues