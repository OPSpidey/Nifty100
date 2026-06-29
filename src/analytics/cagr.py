def calculate_cagr(start_value, end_value, years):
    """
    CAGR = ((End / Start) ** (1 / Years) - 1) * 100
    Returns:
        (cagr, flag)
    """

    if years <= 0:
        return None, "INSUFFICIENT"

    if start_value == 0:
        return None, "ZERO_BASE"

    if start_value > 0 and end_value < 0:
        return None, "DECLINE_TO_LOSS"

    if start_value < 0 and end_value > 0:
        return None, "TURNAROUND"

    if start_value < 0 and end_value < 0:
        return None, "BOTH_NEGATIVE"

    cagr = (((end_value / start_value) ** (1 / years)) - 1) * 100

    return cagr, None

def revenue_cagr(start_sales, end_sales, years):
    return calculate_cagr(start_sales, end_sales, years)


def pat_cagr(start_profit, end_profit, years):
    return calculate_cagr(start_profit, end_profit, years)


def eps_cagr(start_eps, end_eps, years):
    return calculate_cagr(start_eps, end_eps, years)