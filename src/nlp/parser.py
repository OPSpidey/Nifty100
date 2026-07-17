import re
import sqlite3
from pathlib import Path

import pandas as pd


DATA_FILE = Path("data/raw/analysis.xlsx")
OUTPUT_DIR = Path("output")

OUTPUT_DIR.mkdir(exist_ok=True)


REGEX = re.compile(
    r"(\d+)\s*Years?:?\s*([\d.-]+)%"
)


analysis = pd.read_excel(
    DATA_FILE,
    header=1
)


analysis.columns = [
    col.strip()
    for col in analysis.columns
]


TARGET_FIELDS = [
    "compounded_sales_growth",
    "compounded_profit_growth",
    "stock_price_cagr",
    "roe",
]

parsed_rows = []
failed_rows = []

for _, row in analysis.iterrows():

    company_id = row["company_id"]

    for metric in TARGET_FIELDS:

        text = str(row[metric]).strip()

        match = REGEX.search(text)

        if match:

            parsed_rows.append({
                "company_id": company_id,
                "metric_type": metric,
                "period_years": int(match.group(1)),
                "value_pct": float(match.group(2)),
            })

        else:

            failed_rows.append({
                "company_id": company_id,
                "metric_type": metric,
                "text": text,
            })


parsed_df = pd.DataFrame(parsed_rows)

failed_df = pd.DataFrame(failed_rows)

parsed_df.to_csv(
    OUTPUT_DIR / "analysis_parsed.csv",
    index=False
)

failed_df.to_csv(
    OUTPUT_DIR / "parse_failures.csv",
    index=False
)

print(f"Parsed records   : {len(parsed_df)}")
print(f"Failed records   : {len(failed_df)}")

print("\nFiles generated:")
print("output/analysis_parsed.csv")
print("output/parse_failures.csv")

conn = sqlite3.connect("db/nifty100.db")

ratios = pd.read_sql("""
SELECT
    company_id,
    revenue_cagr_5yr,
    pat_cagr_5yr
FROM financial_ratios
WHERE year='Mar 2024'
""", conn)

conn.close()

review_rows = []

sales = parsed_df[
    parsed_df["metric_type"] == "compounded_sales_growth"
]

profit = parsed_df[
    parsed_df["metric_type"] == "compounded_profit_growth"
]

for _, row in sales.iterrows():

    ratio = ratios[
        ratios["company_id"] == row["company_id"]
    ]

    if ratio.empty:
        continue

    computed = ratio.iloc[0]["revenue_cagr_5yr"]

    if pd.isna(computed):
        continue

    diff = abs(row["value_pct"] - computed)

    if diff > 5:

        review_rows.append({
            "company_id": row["company_id"],
            "metric": "Revenue CAGR",
            "parsed_value": row["value_pct"],
            "computed_value": computed,
            "difference_pct": round(diff, 2),
        })


for _, row in profit.iterrows():

    ratio = ratios[
        ratios["company_id"] == row["company_id"]
    ]

    if ratio.empty:
        continue

    computed = ratio.iloc[0]["pat_cagr_5yr"]

    if pd.isna(computed):
        continue

    diff = abs(row["value_pct"] - computed)

    if diff > 5:

        review_rows.append({
            "company_id": row["company_id"],
            "metric": "PAT CAGR",
            "parsed_value": row["value_pct"],
            "computed_value": computed,
            "difference_pct": round(diff, 2),
        })


review_df = pd.DataFrame(review_rows)

review_df.to_csv(
    OUTPUT_DIR / "cagr_manual_review.csv",
    index=False
)

print(f"Manual review rows : {len(review_df)}")