import pandas as pd


def main():
    prices = pd.read_excel(
        "data/supporting/stock_prices.xlsx"
    )

    companies = (
        prices["company_id"]
        .drop_duplicates()
        .sample(5, random_state=42)
    )

    print("5 Random Companies:\n")

    for company in companies:
        print(company)

if __name__ == "__main__":
    main()