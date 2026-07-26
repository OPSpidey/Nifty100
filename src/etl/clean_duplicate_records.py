import sqlite3

import pandas as pd

conn = sqlite3.connect("db/nifty100.db")

tables = [
    "profitandloss",
    "balancesheet",
    "cashflow"
]

def main():
    conn = sqlite3.connect("db/nifty100.db")

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
            df["abs_cfo"] = df["operating_activity"].abs()
            df = (
                df.sort_values(
                    by=["company_id", "year", "abs_cfo"],
                    ascending=[True, True, False]
                )
                .drop_duplicates(
                    subset=["company_id", "year"],
                    keep="first"
                )
                .drop(columns="abs_cfo")
            )
        else:
            df = df.drop_duplicates(
                subset=["company_id", "year"],
                keep="first"
            )

        after = len(df)

        print(f"Rows before : {before}")
        print(f"Rows after  : {after}")
        print(f"Removed     : {before-after}")

        df.to_sql(
            f"{table}_clean",
            conn,
            if_exists="replace",
            index=False
        )

    conn.close()

    print("\nClean tables created successfully.")

if __name__ == "__main__":
    main()