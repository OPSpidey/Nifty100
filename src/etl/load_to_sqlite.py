import pandas as pd
import sqlite3

conn = sqlite3.connect("db/nifty100.db")

files = {
    "companies": ("data/raw/companies.xlsx", 1),
    "profitandloss": ("data/raw/profitandloss.xlsx", 1),
    "balancesheet": ("data/raw/balancesheet.xlsx", 1),
    "cashflow": ("data/raw/cashflow.xlsx", 1),
    "analysis": ("data/raw/analysis.xlsx", 1),
    "documents": ("data/raw/documents.xlsx", 1),
    "prosandcons": ("data/raw/prosandcons.xlsx", 1),
    "financial_ratios": ("data/supporting/financial_ratios.xlsx", 0),
    "sectors": ("data/supporting/sectors.xlsx", 0),
    "stock_prices": ("data/supporting/stock_prices.xlsx", 0),
}

for table, (file_path, header_row) in files.items():

    print(f"Trying {table}...")

    try:
        df = pd.read_excel(file_path, header=header_row)

        print(df.dtypes)

        df.to_sql(
            table,
            conn,
            if_exists="append",
            index=False
        )

        print(f"SUCCESS: {table}")

    except Exception as e:
        print(f"FAILED: {table}")
        print(e)
        break

conn.close()