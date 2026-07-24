import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = "db/nifty100.db"

MARKET_CAP_FILE = "./data/supporting/market_cap.xlsx"

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


def load_data():

    conn = sqlite3.connect(DB_PATH)

    companies = pd.read_sql("""
    SELECT
        id AS company_id,
        company_name
    FROM companies
    """, conn)


    sectors = pd.read_sql("""
    SELECT
        company_id,
        broad_sector
    FROM sectors
    """, conn)


    ratios = pd.read_sql("""
    SELECT
        company_id,
        year,
        free_cash_flow_cr
    FROM financial_ratios
    WHERE year='Mar 2024'
    """, conn)


    conn.close()


    market_cap = pd.read_excel(
        MARKET_CAP_FILE
    )


    return (
        companies,
        sectors,
        ratios,
        market_cap
    )



if __name__ == "__main__":

    companies, sectors, ratios, market_cap = load_data()


    # Latest market cap year
    market_cap = (
        market_cap[
            market_cap["year"] == 2024
        ]
    )


    valuation = (
        companies
        .merge(
            sectors,
            on="company_id",
            how="left"
        )
        .merge(
            ratios,
            on="company_id",
            how="left"
        )
        .merge(
            market_cap,
            on="company_id",
            how="left"
        )
    )


    valuation["FCF_yield_pct"] = (
        valuation["free_cash_flow_cr"]
        /
        valuation["market_cap_crore"]
        *
        100
    )


    valuation["FCF_yield_pct"] = (
        valuation["FCF_yield_pct"]
        .round(2)
    )


    print(
        valuation[
            [
                "company_id",
                "free_cash_flow_cr",
                "market_cap_crore",
                "FCF_yield_pct"
            ]
        ]
        .head()
    )

# Sector median P/E calculation

sector_pe_median = (
    valuation
    .groupby("broad_sector")["pe_ratio"]
    .median()
    .reset_index()
)


sector_pe_median.columns = [
    "broad_sector",
    "5yr_median_PE"
]


valuation = valuation.merge(
    sector_pe_median,
    on="broad_sector",
    how="left"
)


# PE comparison with sector median

valuation["PE_vs_sector_median_pct"] = (
    (
        valuation["pe_ratio"]
        -
        valuation["5yr_median_PE"]
    )
    /
    valuation["5yr_median_PE"]
    *
    100
)


# Valuation flags

def valuation_flag(row):

    if pd.isna(row["pe_ratio"]) or pd.isna(row["5yr_median_PE"]):
        return "Fair"

    if row["pe_ratio"] > row["5yr_median_PE"] * 1.5:
        return "Caution"

    elif row["pe_ratio"] < row["5yr_median_PE"] * 0.7:
        return "Discount"

    else:
        return "Fair"



valuation["flag"] = valuation.apply(
    valuation_flag,
    axis=1
)


print(
    valuation[
        [
            "company_id",
            "broad_sector",
            "pe_ratio",
            "5yr_median_PE",
            "PE_vs_sector_median_pct",
            "flag"
        ]
    ]
    .head()
)

# Rename columns for final output

valuation_output = valuation[
    [
        "company_id",
        "company_name",
        "broad_sector",
        "pe_ratio",
        "pb_ratio",
        "ev_ebitda",
        "FCF_yield_pct",
        "5yr_median_PE",
        "PE_vs_sector_median_pct",
        "flag"
    ]
].copy()


valuation_output.columns = [
    "company_id",
    "company_name",
    "sector",
    "P/E",
    "P/B",
    "EV/EBITDA",
    "FCF_yield_pct",
    "5yr_median_PE",
    "PE_vs_sector_median_pct",
    "flag"
]


valuation_output = valuation_output.round(2)


# Save complete valuation summary

valuation_output.to_excel(
    OUTPUT_DIR / "valuation_summary.xlsx",
    index=False
)


# Save only flagged companies

flags = valuation_output[
    valuation_output["flag"].isin(
        [
            "Caution",
            "Discount"
        ]
    )
]


flags.to_csv(
    OUTPUT_DIR / "valuation_flags.csv",
    index=False
)
