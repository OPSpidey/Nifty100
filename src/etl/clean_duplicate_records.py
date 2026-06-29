import sqlite3
import pandas as pd

conn = sqlite3.connect("db/nifty100.db")

tables = [
    "profitandloss",
    "balancesheet",
    "cashflow"
]

for table in tables:

    print(f"\nCleaning {table}...")

    df = pd.read_sql(f"SELECT * FROM {table}", conn)

    before = len(df)

    # Remove exact duplicate rows except for the auto-generated id
    cols = [c for c in df.columns if c != "id"]

    df = df.drop_duplicates(subset=cols)

    # Remove placeholder cashflow rows where all values are zero
    if table == "cashflow":
        df = df[
            ~(
                (df["operating_activity"] == 0)
                & (df["investing_activity"] == 0)
                & (df["financing_activity"] == 0)
                & (df["net_cash_flow"] == 0)
            )
        ]

    after = len(df)

    print(f"Rows before : {before}")
    print(f"Rows after  : {after}")
    print(f"Removed     : {before-after}")

    df.to_sql(
        table + "_clean",
        conn,
        if_exists="replace",
        index=False
    )

conn.close()

print("\nClean tables created successfully.")