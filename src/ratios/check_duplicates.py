import sqlite3
import pandas as pd

conn = sqlite3.connect("db/nifty100.db")

for table in ["profitandloss_clean", "balancesheet_clean", "cashflow_clean"]:
    print(f"\n===== {table} =====")

    df = pd.read_sql(f"""
        SELECT company_id, year, COUNT(*) AS cnt
        FROM {table}
        GROUP BY company_id, year
        HAVING COUNT(*) > 1
        ORDER BY cnt DESC
    """, conn)

    print(df)

conn.close()