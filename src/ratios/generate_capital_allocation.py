import sqlite3
import sys
from pathlib import Path

import pandas as pd


sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.ratios.cashflow import capital_allocation_pattern


def sign(value):
    return "+" if value >= 0 else "-"


def generate_capital_allocation(
    db_path="db/nifty100.db",
    output_path="output/capital_allocation.csv",
):
    conn = sqlite3.connect(db_path)

    df = pd.read_sql(
        """
        SELECT
            company_id,
            year,
            operating_activity,
            investing_activity,
            financing_activity
        FROM cashflow_clean
        """,
        conn,
    )

    conn.close()

    rows = []

    for _, row in df.iterrows():
        pattern = capital_allocation_pattern(
            row["operating_activity"],
            row["investing_activity"],
            row["financing_activity"],
        )

        rows.append({
            "company_id": row["company_id"],
            "year": row["year"],
            "cfo_sign": sign(row["operating_activity"]),
            "cfi_sign": sign(row["investing_activity"]),
            "cff_sign": sign(row["financing_activity"]),
            "pattern_label": pattern,
        })

    output = pd.DataFrame(rows)
    output.to_csv(output_path, index=False)

    print("capital_allocation.csv generated successfully.")

    return output


if __name__ == "__main__":
    generate_capital_allocation()
