import math

from src.analytics.ratios import (
    asset_turnover,
    cagr_decline_to_loss,
    cagr_turnaround_flag,
    calculate_cagr,
    cfo_quality_score,
    debt_to_equity,
    high_leverage_flag,
    icr_warning_flag,
    interest_coverage_ratio,
    net_profit_margin,
    operating_profit_margin,
    return_on_assets,
    return_on_capital_employed,
    return_on_equity,
)

# ---------- Net Profit Margin ----------

def test_net_profit_margin():
    assert net_profit_margin(20, 100) == 20


def test_net_profit_margin_zero_sales():
    assert net_profit_margin(20, 0) is None


# ---------- Operating Profit Margin ----------

def test_operating_profit_margin():
    value, mismatch = operating_profit_margin(30, 100)
    assert value == 30
    assert mismatch is False


def test_opm_divergence_flag():
    _, mismatch = operating_profit_margin(
        30,
        100,
        opm_percentage=20,
    )
    assert mismatch is True


# ---------- ROE ----------

def test_roe_positive():
    assert return_on_equity(100, 200, 300) == 20


def test_roe_negative_equity():
    assert return_on_equity(100, -200, 100) is None


# ---------- ROCE ----------

def test_roce():
    assert return_on_capital_employed(
        100,
        200,
        200,
        100,
    ) == 20


# ---------- ROA ----------

def test_roa():
    assert return_on_assets(100, 500) == 20


# ---------- Debt to Equity ----------

def test_debt_free():
    assert debt_to_equity(0, 100, 100) == 0


def test_negative_equity():
    assert debt_to_equity(100, -100, 0) is None


# ---------- High Leverage ----------

def test_high_leverage():
    assert high_leverage_flag(6, "Industrials") is True


def test_financial_not_flagged():
    assert high_leverage_flag(6, "Financials") is False


# ---------- ICR ----------

def test_interest_coverage():
    assert interest_coverage_ratio(
        100,
        20,
        10,
    ) == 12


def test_interest_zero():
    assert interest_coverage_ratio(
        100,
        20,
        0,
    ) is None


def test_icr_warning():
    assert icr_warning_flag(1.2) is True


# ---------- Asset Turnover ----------

def test_asset_turnover():
    assert asset_turnover(200, 100) == 2


# ---------- CAGR ----------

def test_cagr_turnaround():
    assert cagr_turnaround_flag(-50, 50)


def test_cagr_decline():
    assert cagr_decline_to_loss(50, -20)


def test_cagr_normal():

    value = calculate_cagr(
        100,
        200,
        5,
    )

    assert math.isclose(
        value,
        14.869835,
        rel_tol=1e-5,
    )


# ---------- CFO Quality ----------

def test_cfo_quality():
    assert cfo_quality_score(200, 100) == 2