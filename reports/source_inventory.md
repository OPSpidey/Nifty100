# Source Inventory

Core datasets: 7
Supporting datasets: 5

Core:
- companies
- profitandloss
- balancesheet
- cashflow
- analysis
- documents
- prosandcons

Supporting:
- stock_prices
- financial_ratios
- market_cap
- sectors
- peer_groups

# src/etl/day5_record_check.py

import pandas as pd

files = {
    "companies":
    "data/raw/companies.xlsx",

    "profitandloss":
    "data/raw/profitandloss.xlsx",

    "balancesheet":
    "data/raw/balancesheet.xlsx",

    "cashflow":
    "data/raw/cashflow.xlsx",

    "analysis":
    "data/raw/analysis.xlsx",

    "documents":
    "data/raw/documents.xlsx",

    "prosandcons":
    "data/raw/prosandcons.xlsx",

    "stock_prices":
    "data/supporting/stock_prices.xlsx",

    "financial_ratios":
    "data/supporting/financial_ratios.xlsx",

    "market_cap":
    "data/supporting/market_cap.xlsx",

    "peer_groups":
    "data/supporting/peer_groups.xlsx",

    "sectors":
    "data/supporting/sectors.xlsx"
}

for name,path in files.items():

    df = pd.read_excel(path)

    print(
        f"{name}: {len(df)} rows"
    )