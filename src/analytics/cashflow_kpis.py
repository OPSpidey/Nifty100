def free_cash_flow(operating_activity, investing_activity):
    """
    Free Cash Flow = CFO + Investing Activity
    """
    return operating_activity + investing_activity


def cfo_quality_score(cfo, pat):
    """
    CFO / PAT
    """
    if pat == 0:
        return None, None

    ratio = cfo / pat

    if ratio > 1:
        label = "High Quality"
    elif ratio >= 0.5:
        label = "Moderate"
    else:
        label = "Accrual Risk"

    return ratio, label


def capex_intensity(investing_activity, sales):
    """
    CapEx Intensity
    """
    if sales == 0:
        return None, None

    value = abs(investing_activity) / sales * 100

    if value < 3:
        label = "Asset Light"
    elif value <= 8:
        label = "Moderate"
    else:
        label = "Capital Intensive"

    return value, label


def fcf_conversion_rate(fcf, operating_profit):
    """
    FCF Conversion Rate
    """
    if operating_profit == 0:
        return None

    return (fcf / operating_profit) * 100

def capital_allocation_pattern(cfo, cfi, cff, cfo_pat_ratio=None):
    """
    Capital allocation pattern classifier.
    """

    signs = (
        "+" if cfo >= 0 else "-",
        "+" if cfi >= 0 else "-",
        "+" if cff >= 0 else "-"
    )

    if signs == ("+", "-", "-"):
        if cfo_pat_ratio is not None and cfo_pat_ratio > 1:
            return "Shareholder Returns"
        return "Reinvestor"

    if signs == ("+", "+", "-"):
        return "Liquidating Assets"

    if signs == ("-", "+", "+"):
        return "Distress Signal"

    if signs == ("-", "-", "+"):
        return "Growth Funded by Debt"

    if signs == ("+", "+", "+"):
        return "Cash Accumulator"

    if signs == ("-", "-", "-"):
        return "Pre-Revenue"

    if signs == ("+", "-", "+"):
        return "Mixed"

    return "Unknown"