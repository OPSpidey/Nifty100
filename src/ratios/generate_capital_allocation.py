import sqlite3
import pandas as pd

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.ratios.cashflow import capital_allocation_pattern
conn = sqlite3.connect("db/nifty100.db")

df = pd.read_sql("""
SELECT
    company_id,
    year,
    operating_activity,
    investing_activity,
    financing_activity
FROM cashflow
""", conn)

conn.close()


def sign(value):
    return "+" if value >= 0 else "-"


rows = []

for _, row in df.iterrows():

    cfo_sign = sign(row["operating_activity"])
    cfi_sign = sign(row["investing_activity"])
    cff_sign = sign(row["financing_activity"])

    pattern = capital_allocation_pattern(
        row["operating_activity"],
        row["investing_activity"],
        row["financing_activity"],
    )

    rows.append({
        "company_id": row["company_id"],
        "year": row["year"],
        "cfo_sign": cfo_sign,
        "cfi_sign": cfi_sign,
        "cff_sign": cff_sign,
        "pattern_label": pattern
    })

output = pd.DataFrame(rows)

output.to_csv(
    "output/capital_allocation.csv",
    index=False
)

print("capital_allocation.csv generated successfully.")