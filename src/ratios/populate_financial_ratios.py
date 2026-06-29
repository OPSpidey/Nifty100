import sqlite3
import pandas as pd

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.ratios.ratios import (
    net_profit_margin,
    operating_profit_margin,
    return_on_equity,
    return_on_capital_employed,
    debt_to_equity,
    high_leverage_flag,
    interest_coverage_ratio,
    asset_turnover,
)

from src.ratios.cashflow import (
    free_cash_flow,
)

from src.ratios.cagr import (
    revenue_cagr,
    pat_cagr,
    eps_cagr,
)


conn = sqlite3.connect("db/nifty100.db")

profit = pd.read_sql("SELECT * FROM profitandloss_clean", conn)
balance = pd.read_sql("SELECT * FROM balancesheet_clean", conn)
cashflow = pd.read_sql("SELECT * FROM cashflow_clean", conn)

companies = pd.read_sql(
    "SELECT * FROM companies",
    conn
)
sectors = pd.read_sql(
    "SELECT company_id, broad_sector FROM sectors",
    conn
)

print("Sectors:", sectors.shape)
print("Companies:", companies.shape)
print(companies.columns.tolist())

cashflow["abs_cfo"] = cashflow["operating_activity"].abs()

cashflow = (
    cashflow
    .sort_values(
        by=["company_id", "year", "abs_cfo"],
        ascending=[True, True, False]
    )
    .drop_duplicates(
        subset=["company_id", "year"],
        keep="first"
    )
    .drop(columns="abs_cfo")
)
print("Cashflow after dedup:", cashflow.shape)

print(
    cashflow.groupby(["company_id", "year"])
    .size()
    .sort_values(ascending=False)
    .head()
)

print("Profit & Loss:", profit.shape)
print("Balance Sheet:", balance.shape)
print("Cash Flow:", cashflow.shape)

print("\nProfit & Loss Columns:")
print(profit.columns.tolist())

print("\nBalance Sheet Columns:")
print(balance.columns.tolist())

print("\nCash Flow Columns:")
print(cashflow.columns.tolist())

merged = (
    profit
    .merge(
        balance,
        on=["company_id", "year"],
        how="inner",
        suffixes=("", "_bal")
    )
    .merge(
        cashflow,
        on=["company_id", "year"],
        how="inner",
        suffixes=("", "_cf")
    )
    .merge(
        sectors,
        on="company_id",
        how="left"
    )
    .merge(
        companies[
            [
                "id",
                "roce_percentage",
                "roe_percentage",
                "book_value",
            ]
        ],
        left_on="company_id",
        right_on="id",
        how="left"
    )
)
merged.drop(columns=["id_x", "id_y"], errors="ignore", inplace=True)

print("\nMerged Shape:", merged.shape)

print("\nMerged Columns:")
print(merged.columns.tolist())

print("\nSample:")
print(
    merged[
        [
            "company_id",
            "year",
            "sales",
            "net_profit",
            "equity_capital",
            "reserves",
            "borrowings",
            "operating_activity",
        ]
    ].head()
)

log = open("output/ratio_edge_cases.log", "w")

log.write("DAY 13 - RATIO EDGE CASES\n")
log.write("=" * 60 + "\n")

results = []

log = open("output/ratio_edge_cases.log", "w")
log.write("DAY 13 - RATIO EDGE CASES\n")
log.write("=" * 60 + "\n")

for _, row in merged.iterrows():

    # Profitability
    npm = net_profit_margin(
        row["net_profit"],
        row["sales"]
    )

    opm, _ = operating_profit_margin(
        row["operating_profit"],
        row["sales"],
        row["opm_percentage"]
    )

    roe = return_on_equity(
        row["net_profit"],
        row["equity_capital"],
        row["reserves"]
    )

    roce = return_on_capital_employed(
        row["operating_profit"],
        row["equity_capital"],
        row["reserves"],
        row["borrowings"]
    )

    de = debt_to_equity(
        row["borrowings"],
        row["equity_capital"],
        row["reserves"]
    )

    leverage_flag = high_leverage_flag(
        de,
        row["broad_sector"]
    )

    # ROE validation
    if pd.notna(row["roe_percentage"]):

        diff = abs(roe - row["roe_percentage"])

        if diff > 5:

            if row["broad_sector"] == "Financials":
                category = "Sector-specific"

            elif diff > 100:
                category = "Formula discrepancy"

            else:
                category = "Source data issue"

            log.write(
                f"{row['company_id']} {row['year']} "
                f"ROE Difference = {diff:.2f} "
                f"(Source={row['roe_percentage']}, Engine={roe:.2f}) "
                f"| Category: {category}\n"
            )

    # ROCE validation
    if pd.notna(row["roce_percentage"]):

        diff = abs(roce - row["roce_percentage"])

        if diff > 5:

            if row["broad_sector"] == "Financials":
                category = "Sector-specific"

            elif diff > 100:
                category = "Formula discrepancy"

            else:
                category = "Source data issue"

            log.write(
                f"{row['company_id']} {row['year']} "
                f"ROCE Difference = {diff:.2f} "
                f"(Source={row['roce_percentage']}, Engine={roce:.2f}) "
                f"| Category: {category}\n"
            )

    icr = interest_coverage_ratio(
        row["operating_profit"],
        row["other_income"],
        row["interest"]
    )

    at = asset_turnover(
        row["sales"],
        row["total_assets"]
    )

    fcf = free_cash_flow(
        row["operating_activity"],
        row["investing_activity"]
    )

    capex = abs(row["investing_activity"])

    if row["equity_capital"] not in (0, None):
        book_value = (
            row["equity_capital"] + row["reserves"]
        ) / row["equity_capital"]
    else:
        book_value = None

    record = {
        "company_id": row["company_id"],
        "year": row["year"],
        "net_profit_margin_pct": npm,
        "operating_profit_margin_pct": opm,
        "return_on_equity_pct": roe,
        "roce_pct": roce,
        "debt_to_equity": de,
        "high_leverage_flag": leverage_flag,
        "interest_coverage": icr,
        "asset_turnover": at,
        "free_cash_flow_cr": fcf,
        "capex_cr": capex,
        "earnings_per_share": row["eps"],
        "book_value_per_share": book_value,
        "dividend_payout_ratio_pct": row["dividend_payout"],
        "total_debt_cr": row["borrowings"],
        "cash_from_operations_cr": row["operating_activity"],
        "source_roe_pct": row["roe_percentage"],
        "source_roce_pct": row["roce_percentage"],
    }

    results.append(record)

log.close()

ratio_df = pd.DataFrame(results)

log.close()

print("ratio_edge_cases.log generated.")
print(ratio_df.head())
print("Rows:", len(ratio_df))

# Write to SQLite
ratio_df.to_sql(
    "financial_ratios",
    conn,
    if_exists="replace",
    index=False
)

print("\nfinancial_ratios table written successfully.")

# Verify row count
count = pd.read_sql(
    "SELECT COUNT(*) AS cnt FROM financial_ratios",
    conn
)

print(count)

conn.close()