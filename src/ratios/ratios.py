def net_profit_margin(net_profit, sales):
    """
    Net Profit Margin = (Net Profit / Sales) * 100
    """
    if sales == 0 or sales is None:
        return None

    return (net_profit / sales) * 100


def operating_profit_margin(operating_profit, sales, opm_percentage=None):
    """
    Operating Profit Margin = (Operating Profit / Sales) * 100
    Returns:
        calculated_opm, mismatch
    """
    if sales == 0 or sales is None:
        return None, False

    calculated = (operating_profit / sales) * 100

    mismatch = False

    if opm_percentage is not None:
        if abs(calculated - opm_percentage) > 1:
            mismatch = True

    return calculated, mismatch


def return_on_equity(net_profit, equity_capital, reserves):
    """
    ROE = Net Profit / (Equity Capital + Reserves) * 100
    """
    capital = equity_capital + reserves

    if capital <= 0:
        return None

    return (net_profit / capital) * 100


def return_on_capital_employed(ebit, equity_capital, reserves, borrowings):
    """
    ROCE = EBIT / (Equity + Reserves + Borrowings) * 100
    """
    capital_employed = equity_capital + reserves + borrowings

    if capital_employed <= 0:
        return None

    return (ebit / capital_employed) * 100


def return_on_assets(net_profit, total_assets):
    """
    ROA = Net Profit / Total Assets * 100
    """
    if total_assets == 0 or total_assets is None:
        return None

    return (net_profit / total_assets) * 100

def roce_benchmark(roce, broad_sector):
    """
    ROCE benchmark check.
    Financial companies use sector-relative benchmark.
    """
    if roce is None:
        return None

    if broad_sector == "Financials":
        return "Sector Benchmark"

    return roce >= 15

def debt_to_equity(borrowings, equity_capital, reserves):
    """
    Debt-to-Equity Ratio
    """
    if borrowings == 0:
        return 0

    equity = equity_capital + reserves

    if equity <= 0:
        return None

    return borrowings / equity


def high_leverage_flag(debt_to_equity_ratio, broad_sector):
    """
    High leverage flag.
    """
    if debt_to_equity_ratio is None:
        return False

    return debt_to_equity_ratio > 5 and broad_sector != "Financials"

def interest_coverage_ratio(operating_profit, other_income, interest):
    """
    Interest Coverage Ratio
    """
    if interest == 0:
        return None

    return (operating_profit + other_income) / interest


def icr_label(icr):
    """
    Label debt-free companies.
    """
    if icr is None:
        return "Debt Free"

    return None


def icr_warning_flag(icr):
    """
    Interest coverage warning.
    """
    if icr is None:
        return False

    return icr < 1.5


def net_debt(borrowings, investments):
    """
    Net Debt
    """
    return borrowings - investments


def asset_turnover(sales, total_assets):
    """
    Asset Turnover Ratio
    """
    if total_assets == 0:
        return None

    return sales / total_assets