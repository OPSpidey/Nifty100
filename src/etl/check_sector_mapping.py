import pandas as pd

companies = pd.read_excel(
    "data/raw/companies.xlsx",
    header=1
)

sectors = pd.read_excel(
    "data/supporting/sectors.xlsx"
)

print("Companies:", len(companies))
print("Sector Records:", len(sectors))

missing = (
    set(companies["id"])
    - set(sectors["company_id"])
)

print("\nMissing Sector Mapping:")

if missing:
    for company in missing:
        print(company)
else:
    print("None")