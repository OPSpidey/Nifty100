import pandas as pd

prices = pd.read_excel(
    "data/supporting/stock_prices.xlsx"
)

sample_companies = [
    "HEROMOTOCO",
    "CANBK",
    "JSWENERGY",
    "PNB",
    "ABB"
]

for company in sample_companies:

    company_data = prices[
        prices["company_id"] == company
    ]

    company_data["date"] = pd.to_datetime(
        company_data["date"]
    )

    first_date = company_data["date"].min()
    last_date = company_data["date"].max()

    years = company_data["date"].dt.year.nunique()

    print("\n" + "=" * 50)
    print("Company:", company)
    print("First Date:", first_date.date())
    print("Last Date:", last_date.date())
    print("Years Covered:", years)