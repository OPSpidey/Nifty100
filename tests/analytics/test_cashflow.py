from src.ratios.cashflow import (
    capex_intensity,
    capital_allocation_pattern,
    cfo_quality_score,
    fcf_conversion_rate,
    free_cash_flow,
)


def test_free_cash_flow():
    assert free_cash_flow(100, -40) == 60


def test_cfo_quality_high():
    ratio, label = cfo_quality_score(120, 100)
    assert round(ratio, 2) == 1.20
    assert label == "High Quality"


def test_cfo_quality_pat_zero():
    ratio, label = cfo_quality_score(100, 0)
    assert ratio is None
    assert label is None


def test_capex_intensity():
    value, label = capex_intensity(-20, 500)
    assert round(value, 2) == 4.00
    assert label == "Moderate"


def test_fcf_conversion():
    assert fcf_conversion_rate(60, 100) == 60.0


def test_fcf_conversion_zero_op():
    assert fcf_conversion_rate(60, 0) is None


def test_reinvestor():
    assert capital_allocation_pattern(100, -50, -20, 0.8) == "Reinvestor"


def test_shareholder_returns():
    assert capital_allocation_pattern(100, -50, -20, 1.2) == "Shareholder Returns"

def test_distress_signal():
    assert capital_allocation_pattern(-100, 50, 20) == "Distress Signal"


def test_growth_funded_by_debt():
    assert capital_allocation_pattern(-100, -50, 20) == "Growth Funded by Debt"


def test_cash_accumulator():
    assert capital_allocation_pattern(100, 50, 20) == "Cash Accumulator"


def test_unknown_pattern():
    assert capital_allocation_pattern(100, 50, -20) == "Liquidating Assets"