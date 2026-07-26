import pandas as pd


def main():
    files = {
    "companies": ("data/raw/companies.xlsx", 1),
    "profitandloss": ("data/raw/profitandloss.xlsx", 1),
    "balancesheet": ("data/raw/balancesheet.xlsx", 1),
    "cashflow": ("data/raw/cashflow.xlsx", 1),
    "analysis": ("data/raw/analysis.xlsx", 1),
    "documents": ("data/raw/documents.xlsx", 1),
    "prosandcons": ("data/raw/prosandcons.xlsx", 1),
    "stock_prices": ("data/supporting/stock_prices.xlsx", 0),
    "financial_ratios": ("data/supporting/financial_ratios.xlsx", 0),
    "market_cap": ("data/supporting/market_cap.xlsx", 0),
    "peer_groups": ("data/supporting/peer_groups.xlsx", 0),
    "sectors": ("data/supporting/sectors.xlsx", 0),
    }   

    for name, (path, header_row) in files.items():
        df = pd.read_excel(path, header=header_row)
        print(f"{name}: {len(df)} rows")

if __name__ == "__main__":
    main()