import pandas as pd

files = {
    "companies": "data/raw/companies.xlsx",
    "profitandloss": "data/raw/profitandloss.xlsx",
    "balancesheet": "data/raw/balancesheet.xlsx",
    "cashflow": "data/raw/cashflow.xlsx",
    "analysis": "data/raw/analysis.xlsx",
    "documents": "data/raw/documents.xlsx",
    "prosandcons": "data/raw/prosandcons.xlsx",
    "stock_prices": "data/supporting/stock_prices.xlsx",
    "financial_ratios": "data/supporting/financial_ratios.xlsx",
    "market_cap": "data/supporting/market_cap.xlsx",
    "peer_groups": "data/supporting/peer_groups.xlsx",
    "sectors": "data/supporting/sectors.xlsx"
}

for name, path in files.items():
    df = pd.read_excel(path)
    print(f"{name}: {len(df)} rows")