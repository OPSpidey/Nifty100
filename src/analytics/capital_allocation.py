def capital_allocation_label(
    roe,
    debt_to_equity,
    free_cash_flow,
    capex,
    dividend_payout,
):
    """
    Classify capital allocation strategy.
    """

    if roe is None:
        return "Unknown"

    if roe > 20 and capex > free_cash_flow:
        return "Reinvest"

    elif roe > 20 and dividend_payout > 40:
        return "Return"

    elif debt_to_equity > 2 and free_cash_flow < 0:
        return "Distress"

    elif debt_to_equity < 0.5 and free_cash_flow > 0:
        return "Cash Rich"

    elif capex > free_cash_flow and dividend_payout < 20:
        return "Expansion"

    elif dividend_payout > 60:
        return "Income"

    elif free_cash_flow > 0 and debt_to_equity < 1:
        return "Balanced"

    else:
        return "Neutral"