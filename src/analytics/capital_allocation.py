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
    
import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = "db/nifty100.db"
OUTPUT_DIR = Path("output")

conn = sqlite3.connect(DB_PATH)

valid_companies = pd.read_sql(
    """
    SELECT id
    FROM companies
    """,
    conn,
)["id"]

conn.close()

capital = pd.read_csv(
    OUTPUT_DIR / "capital_allocation.csv"
)

original_rows = len(capital)

capital = capital[
    capital["company_id"].isin(valid_companies)
].copy()

capital.to_csv(
    OUTPUT_DIR / "capital_allocation.csv",
    index=False,
)

print("Capital Allocation Verification")
print("--------------------------------")
print(f"Original Rows   : {original_rows}")
print(f"Filtered Rows   : {len(capital)}")
print(f"Companies       : {capital['company_id'].nunique()}")
print(f"Years           : {capital['year'].nunique()}")

if capital["company_id"].nunique() == len(valid_companies):
    print("\n Verification Passed")
else:
    print("\n Verification Failed")

# ---------- Latest Company-wise Distribution ----------

capital_no_ttm = capital[
    capital["year"] != "TTM"
].copy()

latest_company = (
    capital_no_ttm
    .sort_values("year")
    .groupby("company_id")
    .tail(1)
)

distribution = (
    latest_company["pattern_label"]
    .value_counts()
    .rename_axis("pattern_label")
    .reset_index(name="company_count")
)

distribution.to_csv(
    OUTPUT_DIR / "capital_allocation_distribution.csv",
    index=False,
)

print("\nLatest records used :", len(latest_company))
print("Companies covered   :", latest_company["company_id"].nunique())

print("\nPattern Distribution")
print(distribution)

print("\nSaved:")
print("output/capital_allocation_distribution.csv")

# ---------- Pattern Changes Report ----------

pattern_changes = []

for company_id, group in (
    capital_no_ttm
    .sort_values("year")
    .groupby("company_id")
):

    latest_two = group.tail(2)

    if len(latest_two) < 2:
        continue

    previous = latest_two.iloc[0]
    latest = latest_two.iloc[1]

    if previous["pattern_label"] != latest["pattern_label"]:

        pattern_changes.append({
            "company_id": company_id,
            "previous_year": previous["year"],
            "previous_pattern": previous["pattern_label"],
            "latest_year": latest["year"],
            "latest_pattern": latest["pattern_label"],
        })

pattern_changes_df = pd.DataFrame(pattern_changes)

pattern_changes_df.to_csv(
    OUTPUT_DIR / "pattern_changes.csv",
    index=False,
)

print("\nPattern Changes Found :", len(pattern_changes_df))
print("Saved:")
print("output/pattern_changes.csv")