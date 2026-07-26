def free_cash_flow(operating_activity, investing_activity):
    """
    Free Cash Flow = CFO + Investing Activity
    """
    if operating_activity is None or investing_activity is None:
        return None

    return operating_activity + investing_activity


def cfo_quality_score(cfo, pat):
    """
    CFO / PAT
    """
    if pat is None or cfo is None:
        return None, None

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
    if sales is None or sales == 0:
        return None, None

    if investing_activity is None:
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
    if (
        operating_profit is None
        or operating_profit == 0
        or fcf is None
    ):
        return None

    return (fcf / operating_profit) * 100

def capital_allocation_pattern(cfo, cfi, cff, cfo_pat_ratio=None):
    """
    Capital allocation pattern classifier.
    """
    if (
    cfo is None
    or cfi is None
    or cff is None
    ):
        return "Unknown"

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

def calculate_cagr(values):
    """
    Calculate CAGR from a list/Series of values.
    Returns None if CAGR cannot be computed.
    """

    values = [v for v in values if pd.notna(v)]

    if len(values) < 2:
        return None

    start = values[0]
    end = values[-1]
    years = len(values) - 1

    if (
        start <= 0
        or end <= 0
        or years <= 0
    ):
        return None

    return ((end / start) ** (1 / years) - 1) * 100

import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

DB_PATH = "db/nifty100.db"
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

def main():

    conn = sqlite3.connect(DB_PATH)

    cashflow = pd.read_sql("""
    SELECT
    company_id,
    year,
    operating_activity,
    investing_activity,
    financing_activity
    FROM cashflow
    """, conn)

    profit = pd.read_sql("""
    SELECT
    company_id,
    year,
    sales,
    net_profit,
    operating_profit
    FROM profitandloss
    """, conn)

    balance = pd.read_sql("""
    SELECT
    company_id,
    year,
    borrowings
    FROM balancesheet
    """, conn)

    ratios = pd.read_sql("""
    SELECT
    company_id,
    year,
    free_cash_flow_cr,
    cash_from_operations_cr,
    capital_allocation,
    eps_cagr_5yr
    FROM financial_ratios
    """, conn)

    sectors = pd.read_sql("""
    SELECT
    company_id,
    broad_sector
    FROM sectors
    """, conn)

    companies = pd.read_sql("""
    SELECT
    id AS company_id
    FROM companies
    ORDER BY id
    """, conn)

    conn.close()

    results = []
    distress = []
    missing_cashflow = []

    for company_id in companies["company_id"]:

        cf = (
            cashflow[cashflow["company_id"] == company_id]
            .sort_values("year")
        )

        if cf.empty:
            missing_cashflow.append(company_id)
            continue

        pl = (
            profit[profit["company_id"] == company_id]
            .sort_values("year")
        )

        merged = cf.merge(
            pl,
            on=["company_id", "year"],
            how="inner",
        )

        if merged.empty:
            continue

        cfo_scores = []

        for _, row in merged.iterrows():

            score, _ = cfo_quality_score(
                row["operating_activity"],
                row["net_profit"],
            )

            if score is not None:
                cfo_scores.append(score)

        if len(cfo_scores) >= 5:
            avg_cfo_score = np.mean(cfo_scores[-5:])
        elif len(cfo_scores) > 0:
            avg_cfo_score = np.mean(cfo_scores)
        else:
            avg_cfo_score = None

        if avg_cfo_score is None:
            quality_label = None
        elif avg_cfo_score > 1:
            quality_label = "High Quality"
        elif avg_cfo_score >= 0.5:
            quality_label = "Moderate"
        else:
            quality_label = "Accrual Risk"

        latest_cf = merged.iloc[-1]

        capex_value, capex_label = capex_intensity(
            latest_cf["investing_activity"],
            latest_cf["sales"],
        )

        distress_flag = False

        if (
            latest_cf["operating_activity"] < 0
            and latest_cf["financing_activity"] > 0
        ):

            distress_flag = True

            latest_profit = merged.iloc[-1]["net_profit"]

            distress.append({
                "company_id": company_id,
                "cfo_value": latest_cf["operating_activity"],
                "cff_value": latest_cf["financing_activity"],
                "latest_net_profit": latest_profit,
            })

            # ---------- Deleveraging Flag ----------
        deleveraging_flag = False

        company_bs = (
            balance[
                balance["company_id"] == company_id
            ]
            .sort_values("year")
        )

        company_ratios = (
        ratios[
            ratios["company_id"] == company_id
        ]
        .sort_values("year")
        )

        fcf_cagr = calculate_cagr(
            company_ratios["free_cash_flow_cr"].tolist()
        )

        if len(company_bs) >= 2:

            latest_borrowing = company_bs.iloc[-1]["borrowings"]
            previous_borrowing = company_bs.iloc[-2]["borrowings"]

            if (
                latest_cf["financing_activity"] < 0
                and latest_borrowing < previous_borrowing
            ):
                deleveraging_flag = True

        results.append({
            "company_id": company_id,
            "cfo_quality_score": avg_cfo_score,
            "cfo_quality_label": quality_label,
            "capex_intensity_pct": capex_value,
            "capex_label": capex_label,
            "fcf_cagr_5yr": fcf_cagr,
            "distress_flag": distress_flag,
            "deleveraging_flag": deleveraging_flag,        
        })

    results_df = pd.DataFrame(results)

    # Latest sector
    latest_sector = sectors.drop_duplicates(
        subset=["company_id"]
    )

    results_df = results_df.merge(
        latest_sector,
        on="company_id",
        how="left"
    )

    # Latest financial ratios
    latest_ratios = (
        ratios
        .sort_values("year")
        .groupby("company_id")
        .tail(1)
    )

    results_df = results_df.merge(
        latest_ratios[
            [
                "company_id",
                "free_cash_flow_cr",
                "cash_from_operations_cr",
                "capital_allocation",
            ]
        ],
        on="company_id",
        how="left",
    )

    # ---------- FCF Conversion ----------
    results_df["cash_from_operations_cr"] = (
    results_df["cash_from_operations_cr"].replace(0, pd.NA)
)

    results_df["fcf_conversion_pct"] = (
        results_df["free_cash_flow_cr"]
        / results_df["cash_from_operations_cr"]
        * 100
    )
   
    results_df.rename(
        columns={
            "broad_sector": "sector",
            "capital_allocation": "capital_allocation_label",
        },
        inplace=True,
    )

    results_df = results_df[
        [
            "company_id",
            "sector",
            "cfo_quality_score",
            "cfo_quality_label",
            "capex_intensity_pct",
            "capex_label",
            "fcf_cagr_5yr",
            "fcf_conversion_pct",
            "distress_flag",
            "deleveraging_flag",
            "capital_allocation_label",
        ]
    ]

    results_df.to_excel(
        OUTPUT_DIR / "cashflow_intelligence.xlsx",
        index=False,
    )

    pd.DataFrame(distress).to_csv(
        OUTPUT_DIR / "distress_alerts.csv",
        index=False,
    )

    print(f"Companies processed : {len(results_df)}")
    print(f"Distress alerts     : {len(distress)}")
    print("\nGenerated files:")
    print("output/cashflow_intelligence.xlsx")
    print("output/distress_alerts.csv")

    if missing_cashflow:
        print("\nCompanies skipped (missing cashflow data):")

        for company in missing_cashflow:
            print(f"- {company}")

    pd.DataFrame(
        {"company_id": missing_cashflow}
    ).to_csv(
        OUTPUT_DIR / "missing_cashflow_companies.csv",
        index=False,
    )

if __name__ == "__main__":
    main()

        