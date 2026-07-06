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
    "debt_to_equity_eq": "debt_to_equity",
    "free_cash_flow_min": "free_cash_flow_cr",
    "revenue_cagr_5yr_min": "revenue_cagr_5yr",
    "revenue_cagr_3yr_min": "revenue_cagr_3yr",
    "pat_cagr_5yr_min": "pat_cagr_5yr",
    "opm_min": "operating_profit_margin_pct",
    "pe_max": "pe_ratio",
    "pb_max": "pb_ratio",
    "dividend_yield_min": "dividend_yield_pct",
    "dividend_payout_max": "dividend_payout_ratio_pct",
    "icr_min": "interest_coverage_for_filter",
    "market_cap_min": "market_cap_crore",
    "net_profit_min": "net_profit",
    "eps_cagr_min": "eps_cagr",
    "asset_turnover_min": "asset_turnover",
    "sales_min": "sales",
    "free_cash_flow_latest_positive": "free_cash_flow_cr",
    "debt_to_equity_declining_yoy": "debt_to_equity_declining_yoy",
}

MIN_FILTERS = {
    "roe_min",
    "free_cash_flow_min",
    "revenue_cagr_5yr_min",
    "revenue_cagr_3yr_min",
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
    "dividend_payout_max",
    "pe_max",
    "pb_max",
}

EQ_FILTERS = {
    "debt_to_equity_eq",
}

BOOL_FILTERS = {
    "free_cash_flow_latest_positive",
    "debt_to_equity_declining_yoy",
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
    config.setdefault("presets", {})
    return config


def _load_simple_yaml(file):
    config = {}
    stack = [(0, config)]

    for raw_line in file:
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue

        if ":" not in line:
            continue

        indent = len(line) - len(line.lstrip(" "))
        key, value = line.strip().split(":", 1)
        value = value.strip()

        while stack and indent < stack[-1][0]:
            stack.pop()

        parent = stack[-1][1]

        if value == "":
            parent[key] = {}
            stack.append((indent + 2, parent[key]))
            continue

        if value.lower() in {"true", "false"}:
            parsed_value = value.lower() == "true"
        else:
            try:
                parsed_value = float(value) if "." in value else int(value)
            except ValueError:
                parsed_value = value

        parent[key] = parsed_value

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


def _cagr_to_each_row(group, value_column, years):
    clean = group[["year_number", value_column]].copy()
    clean[value_column] = pd.to_numeric(clean[value_column], errors="coerce")
    values = []

    for _, row in clean.iterrows():
        history = (
            clean[
                (clean["year_number"].notna())
                & (clean["year_number"] <= row["year_number"])
                & (clean[value_column].notna())
            ]
            .sort_values("year_number")
        )

        if len(history) < 2:
            values.append(np.nan)
            continue

        starts = history[
            history["year_number"] <= row["year_number"] - years
        ]

        start = starts.iloc[-1] if not starts.empty else history.iloc[0]
        end = history.iloc[-1]
        period = end["year_number"] - start["year_number"]

        if period <= 0 or start[value_column] <= 0 or end[value_column] < 0:
            values.append(np.nan)
        else:
            values.append(
                (((end[value_column] / start[value_column]) ** (1 / period)) - 1)
                * 100
            )

    return pd.Series(values, index=group.index)


def _add_eps_cagr(df):
    eps_cagr = (
        df.groupby("company_id", group_keys=False)
        .apply(lambda group: _five_year_cagr(group, "earnings_per_share"))
        .rename("eps_cagr")
        .reset_index()
    )

    return df.merge(eps_cagr, on="company_id", how="left")


def _add_time_series_metrics(df):
    df = df.sort_values(["company_id", "year_number"]).copy()

    df["revenue_cagr_3yr"] = (
        df.groupby("company_id", group_keys=False)
        .apply(lambda group: _cagr_to_each_row(group, "sales", 3))
    )
    df["fcf_cagr_5yr"] = (
        df.groupby("company_id", group_keys=False)
        .apply(lambda group: _cagr_to_each_row(group, "free_cash_flow_cr", 5))
    )
    df["debt_to_equity_previous"] = df.groupby("company_id")[
        "debt_to_equity"
    ].shift(1)
    df["debt_to_equity_declining_yoy"] = (
        pd.to_numeric(df["debt_to_equity"], errors="coerce")
        < pd.to_numeric(df["debt_to_equity_previous"], errors="coerce")
    )
    df["cfo_pat_ratio"] = (
        pd.to_numeric(df["cash_from_operations_cr"], errors="coerce")
        / pd.to_numeric(df["net_profit"], errors="coerce")
    ).replace([np.inf, -np.inf], np.nan)
    df["free_cash_flow_positive_flag"] = (
        pd.to_numeric(df["free_cash_flow_cr"], errors="coerce") > 0
    ).astype(int)

    return df


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

    for column in ("revenue_cagr_5yr", "pat_cagr_5yr"):
        stored_column = f"{column}_x"
        analysis_column = f"{column}_y"

        if stored_column in df.columns or analysis_column in df.columns:
            if stored_column in df.columns:
                df[column] = df[stored_column]
            else:
                df[column] = df[analysis_column]

            if stored_column in df.columns and analysis_column in df.columns:
                df[column] = df[column].combine_first(df[analysis_column])

            df.drop(
                columns=[stored_column, analysis_column],
                errors="ignore",
                inplace=True,
            )

    df = _add_eps_cagr(df)
    df = _add_time_series_metrics(df)

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
            if column != "debt_to_equity_declining_yoy":
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

        if filter_name == "free_cash_flow_latest_positive":
            filtered = filtered[filtered[column].gt(0)]
            continue

        if filter_name == "debt_to_equity_declining_yoy":
            filtered = filtered[filtered[column].eq(bool(threshold))]
            continue

        if filter_name in MIN_FILTERS:
            filtered = filtered[filtered[column].gt(threshold)]
        elif filter_name in MAX_FILTERS:
            filtered = filtered[filtered[column].lt(threshold)]
        elif filter_name in EQ_FILTERS:
            filtered = filtered[np.isclose(filtered[column], threshold, equal_nan=False)]

    return filtered.copy()


def latest_qualifying_companies(df, max_companies=50):
    latest = (
        df.sort_values(["company_id", "year_number"])
        .groupby("company_id", as_index=False)
        .tail(1)
    )

    latest = latest.sort_values(
        by=["composite_quality_score", "market_cap_crore"],
        ascending=[False, False],
        na_position="last",
    )

    return latest.head(max_companies).reset_index(drop=True)


def run_preset(name, df=None, config=None, max_companies=50):
    if config is None:
        config = load_config()
    if df is None:
        df = load_financial_ratios()

    presets = config.get("presets", {})
    if name not in presets:
        raise KeyError(f"Unknown preset: {name}")

    scored = composite_quality_score(df)
    filtered = apply_filters(scored, {"filters": presets[name]})

    return latest_qualifying_companies(filtered, max_companies=max_companies)


def run_all_presets(config_path=DEFAULT_CONFIG_PATH, db_path=DEFAULT_DB_PATH):
    config = load_config(config_path)
    df = composite_quality_score(load_financial_ratios(db_path))

    return {
        name: run_preset(
            name,
            df=df,
            config=config,
            max_companies=50,
        )
        for name in config.get("presets", {})
    }


def _winsorized_score(values, higher_is_better=True):
    numeric = pd.to_numeric(values, errors="coerce").replace(
        [np.inf, -np.inf],
        np.nan,
    )

    if numeric.notna().sum() < 2:
        score = pd.Series(50.0, index=values.index)
    else:
        low = numeric.quantile(0.10)
        high = numeric.quantile(0.90)

        if pd.isna(low) or pd.isna(high) or low == high:
            score = pd.Series(50.0, index=values.index)
        else:
            clipped = numeric.clip(lower=low, upper=high)
            score = ((clipped - low) / (high - low)) * 100

    if not higher_is_better:
        score = 100 - score

    return score.fillna(0)


def _sector_relative_score(df, column, higher_is_better=True):
    return (
        df.groupby("broad_sector", group_keys=False)[column]
        .apply(lambda values: _winsorized_score(values, higher_is_better))
    )


def composite_quality_score(df, config=None):
    """
    Add the Sprint 3 weighted, sector-relative composite quality score.
    """
    if df.empty:
        scored = df.copy()
        scored["composite_quality_score"] = pd.Series(dtype=float)
        return scored

    scored = _prepare_filter_columns(df)
    scored["broad_sector"] = scored["broad_sector"].fillna("Unassigned")

    required_score_columns = [
        "roce_pct",
        "net_profit_margin_pct",
        "fcf_cagr_5yr",
        "cfo_pat_ratio",
        "free_cash_flow_positive_flag",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "debt_to_equity",
        "interest_coverage_for_filter",
    ]

    for column in required_score_columns:
        if column not in scored.columns:
            scored[column] = np.nan

    scored["score_roe"] = _sector_relative_score(
        scored,
        "return_on_equity_pct",
    )
    scored["score_roce"] = _sector_relative_score(scored, "roce_pct")
    scored["score_npm"] = _sector_relative_score(
        scored,
        "net_profit_margin_pct",
    )
    scored["score_fcf_cagr"] = _sector_relative_score(scored, "fcf_cagr_5yr")
    scored["score_cfo_pat"] = _sector_relative_score(scored, "cfo_pat_ratio")
    scored["score_fcf_positive"] = scored["free_cash_flow_positive_flag"] * 100
    scored["score_revenue_cagr"] = _sector_relative_score(
        scored,
        "revenue_cagr_5yr",
    )
    scored["score_pat_cagr"] = _sector_relative_score(scored, "pat_cagr_5yr")
    scored["score_de"] = _sector_relative_score(
        scored,
        "debt_to_equity",
        higher_is_better=False,
    )
    scored["score_icr"] = _sector_relative_score(
        scored,
        "interest_coverage_for_filter",
    )

    component_columns = [
        "score_roe",
        "score_roce",
        "score_npm",
        "score_fcf_cagr",
        "score_cfo_pat",
        "score_fcf_positive",
        "score_revenue_cagr",
        "score_pat_cagr",
        "score_de",
        "score_icr",
    ]

    scored[component_columns] = scored[component_columns].fillna(0)

    scored["composite_quality_score"] = (
        scored["score_roe"] * 0.15
        + scored["score_roce"] * 0.10
        + scored["score_npm"] * 0.10
        + scored["score_fcf_cagr"] * 0.15
        + scored["score_cfo_pat"] * 0.10
        + scored["score_fcf_positive"] * 0.05
        + scored["score_revenue_cagr"] * 0.10
        + scored["score_pat_cagr"] * 0.10
        + scored["score_de"] * 0.10
        + scored["score_icr"] * 0.05
    ).round(2)

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
