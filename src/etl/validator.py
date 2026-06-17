import pandas as pd

failures = []


def add_failure(
    company_id,
    year,
    field,
    issue,
    severity
):
    failures.append({
        "company_id": company_id,
        "year": year,
        "field": field,
        "issue": issue,
        "severity": severity
    })


def validate_profitandloss(df):

    # Missing company_id
    missing_company = df[df["company_id"].isna()]

    for _, row in missing_company.iterrows():

        add_failure(
            "",
            row["year"],
            "company_id",
            "Missing company_id",
            "CRITICAL"
        )

    # Missing year
    missing_year = df[df["year"].isna()]

    for _, row in missing_year.iterrows():

        add_failure(
            row["company_id"],
            "",
            "year",
            "Missing year",
            "CRITICAL"
        )

    # Tax rate
    invalid_tax = df[
        (df["tax_percentage"] < 0)
        |
        (df["tax_percentage"] > 100)
    ]

    for _, row in invalid_tax.iterrows():

        add_failure(
            row["company_id"],
            row["year"],
            "tax_percentage",
            "Tax rate outside range",
            "WARNING"
        )
    # Dividend payout
    invalid_dividend = df[
        df["dividend_payout"] > 100
    ]

    for _, row in invalid_dividend.iterrows():

        add_failure(
            row["company_id"],
            row["year"],
            "dividend_payout",
            "Dividend payout exceeds 100%",
            "WARNING"
        )

    # EPS validation
    invalid_eps = df[
        (df["net_profit"] > 0)
        &
        (df["eps"] < 0)
    ]

    for _, row in invalid_eps.iterrows():

        add_failure(
            row["company_id"],
            row["year"],
            "eps",
            "Positive profit with negative EPS",
            "CRITICAL"
        )

def validate_companies(df):

    url_columns = [
        "website",
        "nse_profile",
        "bse_profile"
    ]

    for col in url_columns:

        invalid = df[
            ~df[col]
            .fillna("")
            .str.startswith(
                ("http://", "https://")
            )
        ]

        for _, row in invalid.iterrows():

            add_failure(
                row["company_name"],
                "",
                col,
                "Invalid URL",
                "WARNING"
            )


def main():

    pnl = pd.read_excel(
        "data/raw/profitandloss.xlsx",
        header=1
    )

    companies = pd.read_excel(
        "data/raw/companies.xlsx",
        header=1
    )

    validate_profitandloss(pnl)

    validate_companies(companies)

    output = pd.DataFrame(failures)

    output.to_csv(
        "output/validation_failures.csv",
        index=False
    )

    print(
        f"{len(output)} failures found"
    )


if __name__ == "__main__":
    main()