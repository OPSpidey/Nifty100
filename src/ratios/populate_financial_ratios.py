import sqlite3
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.analytics.cagr import (
    eps_cagr,
    pat_cagr,
    revenue_cagr,
)
from src.analytics.capital_allocation import capital_allocation_label
from src.analytics.cashflow_kpis import (
    capital_allocation_pattern,
    free_cash_flow,
)
from src.analytics.ratios import (
    asset_turnover,
    debt_to_equity,
    high_leverage_flag,
    interest_coverage_ratio,
    net_profit_margin,
    operating_profit_margin,
    return_on_capital_employed,
    return_on_equity,
)


def sign_label(value):
    return "+" if value >= 0 else "-"


def five_year_company_cagr(df, value_column, output_column, cagr_func):
    results = []

    work = df[["company_id", "year", value_column]].copy()
    work["year_number"] = pd.to_numeric(
        work["year"].astype(str).str.extract(r"(\d{4})")[0],
        errors="coerce"
    )

    for company_id, group in work.groupby("company_id"):
        clean = (
            group.dropna(subset=["year_number", value_column])
            .sort_values("year_number")
        )

        if len(clean) < 2:
            value = None
        else:
            end = clean.iloc[-1]
            starts = clean[
                clean["year_number"] <= end["year_number"] - 5
            ]
            start = starts.iloc[-1] if not starts.empty else clean.iloc[0]
            years = end["year_number"] - start["year_number"]

            value, _ = cagr_func(
                start[value_column],
                end[value_column],
                years
            )

        results.append({
            "company_id": company_id,
            output_column: value,
        })

    return pd.DataFrame(results)


def add_composite_quality_score(df):
    score_columns = {
        "return_on_equity_pct": 1,
        "free_cash_flow_cr": 1,
        "revenue_cagr_5yr": 1,
        "pat_cagr_5yr": 1,
        "operating_profit_margin_pct": 1,
        "interest_coverage": 1,
        "asset_turnover": 1,
        "eps_cagr_5yr": 1,
        "debt_to_equity": -1,
    }

    parts = []

    for column, direction in score_columns.items():
        values = pd.to_numeric(df[column], errors="coerce")
        minimum = values.min(skipna=True)
        maximum = values.max(skipna=True)

        if pd.isna(minimum) or pd.isna(maximum) or minimum == maximum:
            normalized = pd.Series(0.5, index=df.index)
        else:
            normalized = (values - minimum) / (maximum - minimum)

        if direction < 0:
            normalized = 1 - normalized

        parts.append(normalized.fillna(0))

    df["composite_quality_score"] = (
        pd.concat(parts, axis=1).mean(axis=1) * 100
    ).round(2)

    return df


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
        how="left",
        suffixes=("", "_bal")
    )
    .merge(
        cashflow,
        on=["company_id", "year"],
        how="left",
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

results = []

with open("output/ratio_edge_cases.log", "w") as log:
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
            row["reserves"],
        )

        leverage_flag = high_leverage_flag(
            de,
            row["broad_sector"]
        )

        # ROE validation
        if (
        roe is not None
        and pd.notna(row["roe_percentage"])
    ):

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
        if (
            roce is not None
            and pd.notna(row["roce_percentage"])
        ):

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

        allocation = capital_allocation_label(
            roe,
            de,
            fcf,
            capex,
            row["dividend_payout"],
        )

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
            "capital_allocation": allocation,
        }

        results.append(record)



    ratio_df = pd.DataFrame(results)

    cagr_frames = [
        five_year_company_cagr(
            profit,
            "sales",
            "revenue_cagr_5yr",
            revenue_cagr,
        ),
        five_year_company_cagr(
            profit,
            "net_profit",
            "pat_cagr_5yr",
            pat_cagr,
        ),
        five_year_company_cagr(
            profit,
            "eps",
            "eps_cagr_5yr",
            eps_cagr,
        ),
    ]

    for cagr_frame in cagr_frames:
        ratio_df = ratio_df.merge(
            cagr_frame,
            on="company_id",
            how="left",
        )

    ratio_df = add_composite_quality_score(ratio_df)

    

    print("ratio_edge_cases.log generated.")

    print(ratio_df.head())
    print("Rows:", len(ratio_df))

    capital_allocation_df = merged[
        [
            "company_id",
            "year",
            "operating_activity",
            "investing_activity",
            "financing_activity",
        ]
    ].copy()

    capital_allocation_df = capital_allocation_df[
        capital_allocation_df["year"] != "TTM"
    ].copy()

    capital_allocation_df = capital_allocation_df.drop_duplicates(
        subset=["company_id", "year"],
        keep="first",
    )
    capital_allocation_df["cfo_sign"] = capital_allocation_df[
        "operating_activity"
    ].map(sign_label)
    capital_allocation_df["cfi_sign"] = capital_allocation_df[
        "investing_activity"
    ].map(sign_label)
    capital_allocation_df["cff_sign"] = capital_allocation_df[
        "financing_activity"
    ].map(sign_label)
    capital_allocation_df["pattern_label"] = capital_allocation_df.apply(
        lambda row: capital_allocation_pattern(
            row["operating_activity"],
            row["investing_activity"],
            row["financing_activity"],
        ),
        axis=1,
    )
    capital_allocation_df[
        [
            "company_id",
            "year",
            "cfo_sign",
            "cfi_sign",
            "cff_sign",
            "pattern_label",
        ]
    ].to_csv(
        "output/capital_allocation.csv",
        index=False,
    )

    print("capital_allocation.csv generated.")

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
