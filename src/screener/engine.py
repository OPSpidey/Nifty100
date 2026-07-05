import re
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

try:
    import yaml
except ModuleNotFoundError:
    yaml = None


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "screener_config.yaml"
DEFAULT_DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"


FILTER_COLUMNS = {
    "roe_min": "return_on_equity_pct",
    "debt_to_equity_max": "debt_to_equity",
    "free_cash_flow_min": "free_cash_flow_cr",
    "revenue_cagr_5yr_min": "revenue_cagr_5yr",
    "pat_cagr_5yr_min": "pat_cagr_5yr",
    "opm_min": "operating_profit_margin_pct",
    "pe_max": "pe_ratio",
    "pb_max": "pb_ratio",
    "dividend_yield_min": "dividend_yield_pct",
    "icr_min": "interest_coverage_for_filter",
    "market_cap_min": "market_cap_crore",
    "net_profit_min": "net_profit",
    "eps_cagr_min": "eps_cagr",
    "asset_turnover_min": "asset_turnover",
    "sales_min": "sales",
}

MIN_FILTERS = {
    "roe_min",
    "free_cash_flow_min",
    "revenue_cagr_5yr_min",
    "pat_cagr_5yr_min",
    "opm_min",
    "dividend_yield_min",
    "icr_min",
    "market_cap_min",
    "net_profit_min",
    "eps_cagr_min",
    "asset_turnover_min",
    "sales_min",
}

MAX_FILTERS = {
    "debt_to_equity_max",
    "pe_max",
    "pb_max",
}


def load_config(path=DEFAULT_CONFIG_PATH):
    """
    Load screener thresholds from YAML.
    """
    with open(path, "r", encoding="utf-8") as file:
        if yaml is not None:
            config = yaml.safe_load(file) or {}
        else:
            config = _load_simple_yaml(file)

    config.setdefault("filters", {})
    return config


def _load_simple_yaml(file):
    config = {}
    current_section = None

    for raw_line in file:
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue

        if not line.startswith(" "):
            key = line.rstrip(":")
            config[key] = {}
            current_section = config[key]
            continue

        if current_section is None or ":" not in line:
            continue

        key, value = line.strip().split(":", 1)
        value = value.strip()

        try:
            current_section[key] = float(value) if "." in value else int(value)
        except ValueError:
            current_section[key] = value

    return config


def _extract_metric_value(value):
    if pd.isna(value):
        return np.nan

    if isinstance(value, (int, float, np.number)):
        return float(value)

    matches = re.findall(r"-?\d+(?:\.\d+)?", str(value).replace(",", ""))
    if not matches:
        return np.nan

    return float(matches[-1])


def _year_as_number(series):
    return pd.to_numeric(
        series.astype(str).str.extract(r"(\d{4})")[0],
        errors="coerce",
    )


def _five_year_cagr(group, value_column):
    clean = (
        group[["year_number", value_column]]
        .dropna()
        .sort_values("year_number")
    )

    if len(clean) < 2:
        return np.nan

    end = clean.iloc[-1]
    start_candidates = clean[
        clean["year_number"] <= end["year_number"] - 5
    ]

    start = (
        start_candidates.iloc[-1]
        if not start_candidates.empty
        else clean.iloc[0]
    )

    years = end["year_number"] - start["year_number"]
    start_value = start[value_column]
    end_value = end[value_column]

    if years <= 0 or start_value <= 0 or end_value < 0:
        return np.nan

    return (((end_value / start_value) ** (1 / years)) - 1) * 100


def _add_eps_cagr(df):
    eps_cagr = (
        df.groupby("company_id", group_keys=False)
        .apply(lambda group: _five_year_cagr(group, "earnings_per_share"))
        .rename("eps_cagr")
        .reset_index()
    )

    return df.merge(eps_cagr, on="company_id", how="left")


def _prepare_analysis_cagr(analysis):
    analysis = analysis.copy()

    five_year_mask = (
        analysis["compounded_sales_growth"]
        .astype(str)
        .str.contains(r"\b5\s*Years\b", case=False, na=False)
    )

    analysis = analysis[five_year_mask].copy()
    analysis["revenue_cagr_5yr"] = analysis[
        "compounded_sales_growth"
    ].map(_extract_metric_value)
    analysis["pat_cagr_5yr"] = analysis[
        "compounded_profit_growth"
    ].map(_extract_metric_value)

    return analysis[
        [
            "company_id",
            "compounded_sales_growth",
            "compounded_profit_growth",
            "revenue_cagr_5yr",
            "pat_cagr_5yr",
        ]
    ].drop_duplicates("company_id", keep="last")


def load_financial_ratios(db_path=DEFAULT_DB_PATH):
    """
    Load financial ratios and enrich them with fields needed by the screener.
    """
    with sqlite3.connect(db_path) as conn:
        ratios = pd.read_sql("SELECT * FROM financial_ratios", conn)

        sectors = pd.read_sql(
            """
            SELECT company_id, broad_sector
            FROM sectors
            """,
            conn,
        )

        analysis = pd.read_sql(
            """
            SELECT
                company_id,
                compounded_sales_growth,
                compounded_profit_growth
            FROM analysis
            """,
            conn,
        )

        market = pd.read_sql(
            """
            SELECT
                company_id,
                year,
                market_cap_crore,
                pe_ratio,
                pb_ratio,
                dividend_yield_pct
            FROM market_cap
            """,
            conn,
        )

        profit = pd.read_sql(
            """
            SELECT
                company_id,
                year,
                sales,
                net_profit
            FROM profitandloss_clean
            """,
            conn,
        )

    ratios["year_number"] = _year_as_number(ratios["year"])
    profit["year_number"] = _year_as_number(profit["year"])

    analysis = _prepare_analysis_cagr(analysis)

    df = (
        ratios.merge(analysis, on="company_id", how="left")
        .merge(sectors, on="company_id", how="left")
        .merge(
            market,
            left_on=["company_id", "year_number"],
            right_on=["company_id", "year"],
            how="left",
            suffixes=("", "_market"),
        )
        .merge(
            profit,
            on=["company_id", "year_number"],
            how="left",
            suffixes=("", "_profit"),
        )
    )

    df.drop(
        columns=["year_market", "year_profit"],
        errors="ignore",
        inplace=True,
    )

    df = _add_eps_cagr(df)

    return df


def _debt_free_icr_mask(df):
    text_columns = [
        column
        for column in ("interest_coverage", "capital_allocation")
        if column in df.columns
    ]

    if not text_columns:
        return pd.Series(False, index=df.index)

    mask = pd.Series(False, index=df.index)
    for column in text_columns:
        mask |= df[column].astype(str).str.contains(
            "debt free",
            case=False,
            na=False,
        )

    numeric_debt = pd.to_numeric(df.get("total_debt_cr"), errors="coerce")
    mask |= numeric_debt.fillna(0).eq(0)

    return mask


def _prepare_filter_columns(df):
    df = df.copy()

    for column in set(FILTER_COLUMNS.values()):
        if column in df.columns and column != "interest_coverage_for_filter":
            df[column] = pd.to_numeric(df[column], errors="coerce")

    df["interest_coverage_for_filter"] = pd.to_numeric(
        df["interest_coverage"],
        errors="coerce",
    ).astype(float)

    debt_free_mask = _debt_free_icr_mask(df)
    if debt_free_mask.any():
        df.loc[debt_free_mask, "interest_coverage_for_filter"] = np.inf

    return df


def apply_filters(df, config):
    """
    Apply configured threshold filters to the financial ratios DataFrame.
    """
    filters = config.get("filters", {})
    filtered = _prepare_filter_columns(df)

    for filter_name, threshold in filters.items():
        if threshold is None or filter_name not in FILTER_COLUMNS:
            continue

        column = FILTER_COLUMNS[filter_name]

        if filter_name == "debt_to_equity_max":
            financials = filtered["broad_sector"].eq("Financials")
            passes = filtered[column].le(threshold)
            filtered = filtered[financials | passes]
            continue

        if filter_name in MIN_FILTERS:
            filtered = filtered[filtered[column].ge(threshold)]
        elif filter_name in MAX_FILTERS:
            filtered = filtered[filtered[column].le(threshold)]

    return filtered.copy()


def composite_quality_score(df, config=None):
    """
    Add a composite score from normalized quality, growth, valuation, and scale metrics.
    """
    if df.empty:
        scored = df.copy()
        scored["composite_quality_score"] = pd.Series(dtype=float)
        return scored

    scored = df.copy()
    score_columns = {
        "return_on_equity_pct": 1,
        "free_cash_flow_cr": 1,
        "revenue_cagr_5yr": 1,
        "pat_cagr_5yr": 1,
        "operating_profit_margin_pct": 1,
        "dividend_yield_pct": 1,
        "interest_coverage_for_filter": 1,
        "market_cap_crore": 1,
        "net_profit": 1,
        "eps_cagr": 1,
        "asset_turnover": 1,
        "sales": 1,
        "debt_to_equity": -1,
        "pe_ratio": -1,
        "pb_ratio": -1,
    }

    normalized_parts = []

    for column, direction in score_columns.items():
        if column not in scored.columns:
            continue

        values = pd.to_numeric(scored[column], errors="coerce")
        values = values.replace([np.inf, -np.inf], np.nan)

        minimum = values.min(skipna=True)
        maximum = values.max(skipna=True)

        if pd.isna(minimum) or pd.isna(maximum) or minimum == maximum:
            normalized = pd.Series(0.5, index=scored.index)
        else:
            normalized = (values - minimum) / (maximum - minimum)

        if direction < 0:
            normalized = 1 - normalized

        normalized_parts.append(normalized.fillna(0))

    if normalized_parts:
        scored["composite_quality_score"] = (
            pd.concat(normalized_parts, axis=1).mean(axis=1) * 100
        ).round(2)
    else:
        scored["composite_quality_score"] = 0.0

    return scored


def run(config_path=DEFAULT_CONFIG_PATH, db_path=DEFAULT_DB_PATH):
    config = load_config(config_path)
    df = load_financial_ratios(db_path)
    filtered_df = apply_filters(df, config)
    scored_df = composite_quality_score(filtered_df, config)

    sort_columns = ["composite_quality_score", "market_cap_crore"]
    sort_columns = [column for column in sort_columns if column in scored_df.columns]

    if sort_columns:
        scored_df = scored_df.sort_values(
            by=sort_columns,
            ascending=[False] * len(sort_columns),
        )

    return scored_df.reset_index(drop=True)


if __name__ == "__main__":
    result = run()
    print("Rows After:", len(result))
    print(result.head())
