
import pandas as pd

FILES = {
    "analysis.xlsx": ("data/raw/analysis.xlsx", 1),
    "balancesheet.xlsx": ("data/raw/balancesheet.xlsx", 1),
    "cashflow.xlsx": ("data/raw/cashflow.xlsx", 1),
    "companies.xlsx": ("data/raw/companies.xlsx", 1),
    "documents.xlsx": ("data/raw/documents.xlsx", 1),
    "profitandloss.xlsx": ("data/raw/profitandloss.xlsx", 1),
    "prosandcons.xlsx": ("data/raw/prosandcons.xlsx", 1),
    "financial_ratios.xlsx": ("data/supporting/financial_ratios.xlsx", 0),
    "market_cap.xlsx": ("data/supporting/market_cap.xlsx", 0),
    "peer_groups.xlsx": ("data/supporting/peer_groups.xlsx", 0),
    "sectors.xlsx": ("data/supporting/sectors.xlsx", 0),
    "stock_prices.xlsx": ("data/supporting/stock_prices.xlsx", 0),
}


def load_excel(path):
    """Load Bluestock raw Excel files using header row 1."""
    return load_source_file(path, 1)


def load_source_file(path, header_row):
    df = pd.read_excel(path, header=header_row)
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    return df


def create_load_audit(output_path="output/load_audit.csv"):
    audit = []

    for file_name, (file_path, header_row) in FILES.items():
        df = load_source_file(file_path, header_row)

        audit.append({
            "file_name": file_name,
            "rows": len(df),
            "columns": len(df.columns)
        })

        print(
            f"{file_name}: "
            f"{len(df)} rows "
            f"{len(df.columns)} columns"
        )

    audit_df = pd.DataFrame(audit)
    audit_df.to_csv(output_path, index=False)

    print("\nAudit file created.")

    return audit_df


if __name__ == "__main__":
    create_load_audit()
