import pandas as pd

prices = pd.read_excel(
    "data/supporting/stock_prices.xlsx"
)

prices["date"] = pd.to_datetime(
    prices["date"]
)

coverage = (
    prices.groupby("company_id")["date"]
    .apply(lambda x: x.dt.year.nunique())
    .reset_index()
)

coverage.columns = [
    "company_id",
    "years_covered"
]

lt5 = coverage[
    coverage["years_covered"] < 5
]

print("\nCompanies with <5 years coverage:\n")
print(lt5)

print("\nCount:", len(lt5))