from src.ratios.ratios import (
    net_profit_margin,
    operating_profit_margin,
    return_on_equity,
    return_on_capital_employed,
    return_on_assets,
    roce_benchmark,
    debt_to_equity,
    high_leverage_flag,
    interest_coverage_ratio,
    icr_label,
    icr_warning_flag,
    net_debt,
    asset_turnover,
)


def test_net_profit_margin():
    assert net_profit_margin(20, 100) == 20.0


def test_net_profit_margin_zero_sales():
    assert net_profit_margin(20, 0) is None


def test_operating_profit_margin():
    opm, mismatch = operating_profit_margin(25, 100, 25)
    assert opm == 25.0
    assert mismatch is False


def test_operating_profit_margin_mismatch():
    opm, mismatch = operating_profit_margin(25, 100, 20)
    assert mismatch is True


def test_return_on_equity():
    assert return_on_equity(20, 50, 50) == 20.0


def test_return_on_equity_negative_equity():
    assert return_on_equity(20, -50, 20) is None


def test_return_on_capital_employed():
    assert return_on_capital_employed(30, 50, 50, 50) == 20.0


def test_return_on_assets():
    assert return_on_assets(20, 100) == 20.0


def test_debt_to_equity():
    assert debt_to_equity(100, 50, 50) == 1.0


def test_debt_to_equity_debt_free():
    assert debt_to_equity(0, 50, 50) == 0


def test_high_leverage_flag():
    assert high_leverage_flag(6.0, "Industrials") is True


def test_high_leverage_financials():
    assert high_leverage_flag(6.0, "Financials") is False


def test_interest_coverage_ratio():
    assert interest_coverage_ratio(100, 20, 20) == 6.0


def test_interest_coverage_zero_interest():
    assert interest_coverage_ratio(100, 20, 0) is None


def test_icr_label():
    assert icr_label(None) == "Debt Free"


def test_asset_turnover():
    assert asset_turnover(200, 100) == 2.0