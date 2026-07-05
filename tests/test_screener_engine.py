import numpy as np
import pandas as pd

from src.screener.engine import (
    _prepare_analysis_cagr,
    apply_filters,
    composite_quality_score,
)


def _base_frame():
    return pd.DataFrame(
        [
            {
                "company_id": "BANK",
                "broad_sector": "Financials",
                "return_on_equity_pct": 20,
                "debt_to_equity": 8,
                "free_cash_flow_cr": 100,
                "revenue_cagr_5yr": 12,
                "pat_cagr_5yr": 12,
                "operating_profit_margin_pct": 20,
                "pe_ratio": 20,
                "pb_ratio": 3,
                "dividend_yield_pct": 1,
                "interest_coverage": 1,
                "market_cap_crore": 20000,
                "net_profit": 500,
                "eps_cagr": 15,
                "asset_turnover": 1,
                "sales": 1000,
                "total_debt_cr": 100,
            },
            {
                "company_id": "IND",
                "broad_sector": "Industrials",
                "return_on_equity_pct": 20,
                "debt_to_equity": 8,
                "free_cash_flow_cr": 100,
                "revenue_cagr_5yr": 12,
                "pat_cagr_5yr": 12,
                "operating_profit_margin_pct": 20,
                "pe_ratio": 20,
                "pb_ratio": 3,
                "dividend_yield_pct": 1,
                "interest_coverage": 1,
                "market_cap_crore": 20000,
                "net_profit": 500,
                "eps_cagr": 15,
                "asset_turnover": 1,
                "sales": 1000,
                "total_debt_cr": 100,
            },
        ]
    )


def test_debt_to_equity_filter_skips_financials():
    filtered = apply_filters(
        _base_frame(),
        {"filters": {"debt_to_equity_max": 1}},
    )

    assert filtered["company_id"].tolist() == ["BANK"]


def test_debt_free_interest_coverage_passes_minimum():
    df = _base_frame().head(1).copy()
    df["broad_sector"] = "Industrials"
    df["interest_coverage"] = "Debt Free"

    filtered = apply_filters(df, {"filters": {"icr_min": 100}})

    assert filtered["company_id"].tolist() == ["BANK"]
    assert np.isinf(filtered["interest_coverage_for_filter"].iloc[0])


def test_composite_quality_score_column_is_added():
    scored = composite_quality_score(_base_frame())

    assert "composite_quality_score" in scored.columns
    assert scored["composite_quality_score"].notna().all()


def test_analysis_cagr_uses_only_five_year_rows():
    analysis = pd.DataFrame(
        [
            {
                "company_id": "ABC",
                "compounded_sales_growth": "10 Years: 21%",
                "compounded_profit_growth": "10 Years: 22%",
            },
            {
                "company_id": "ABC",
                "compounded_sales_growth": "5 Years: 12%",
                "compounded_profit_growth": "5 Years: 14%",
            },
        ]
    )

    result = _prepare_analysis_cagr(analysis)

    assert len(result) == 1
    assert result["revenue_cagr_5yr"].iloc[0] == 12
    assert result["pat_cagr_5yr"].iloc[0] == 14
