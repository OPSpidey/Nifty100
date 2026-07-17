import sqlite3
from pathlib import Path

import pandas as pd


DB_PATH = "db/nifty100.db"
OUTPUT_DIR = Path("output")

OUTPUT_DIR.mkdir(exist_ok=True)


conn = sqlite3.connect(DB_PATH)


ratios = pd.read_sql("""
SELECT *
FROM financial_ratios
ORDER BY company_id, year
""", conn)


pl = pd.read_sql("""
SELECT *
FROM profitandloss
ORDER BY company_id, year
""", conn)


bs = pd.read_sql("""
SELECT *
FROM balancesheet
ORDER BY company_id, year
""", conn)


cf = pd.read_sql("""
SELECT *
FROM cashflow
ORDER BY company_id, year
""", conn)


market = pd.read_sql("""
SELECT *
FROM market_cap
ORDER BY company_id, year
""", conn)


sectors = pd.read_sql("""
SELECT *
FROM sectors
""", conn)


companies = pd.read_sql("""
SELECT
id,
company_name
FROM companies
ORDER BY id
""", conn)


conn.close()


generated = []

annual_ratios = ratios[
    ratios["year"] != "TTM"
].copy()

latest_year = (
    annual_ratios["year"]
    .dropna()
    .sort_values()
    .unique()[-1]
)

latest = annual_ratios[
    annual_ratios["year"] == latest_year
].copy()

for _, company in companies.iterrows():

    ticker = company["id"]

    history = (
    ratios[
        (ratios["company_id"] == ticker)
        & (ratios["year"] != "TTM")
    ]
    .sort_values("year")
)

    if history.empty:
        continue

    current = history.iloc[-1]

    if ticker in ["TCS", "RELIANCE"]:
        print("\n" + "="*60)
        print("Ticker:", ticker)
        print("Current Year:", current["year"])
        print("OPM:", current["operating_profit_margin_pct"])
        print("ICR:", current["interest_coverage"])
        print("D/E:", current["debt_to_equity"])
        print("FCF:", current["free_cash_flow_cr"])

    # ---------- PRO RULE 1 ----------
    roe_history = history["source_roe_pct"].dropna()

    if (
        len(roe_history) >= 3
        and (roe_history.tail(3) > 20).all()
    ):

        generated.append({
            "company_id": ticker,
            "type": "pro",
            "rule_id": 1,
            "text": "Consistently high return on equity above 20% demonstrates exceptional capital efficiency.",
            "confidence_pct": 95,
        })

    # ---------- PRO RULE 2 ----------
    fcf_history = history["free_cash_flow_cr"].dropna()

    if (
        len(fcf_history) >= 5
        and (fcf_history.tail(5) > 0).all()
    ):

        generated.append({
            "company_id": ticker,
            "type": "pro",
            "rule_id": 2,
            "text": "Strong free cash flow generation over 5 years signals healthy business fundamentals.",
            "confidence_pct": 92,
        })

    # ---------- PRO RULE 3 ----------
    if (
        pd.notna(current["debt_to_equity"])
        and current["debt_to_equity"] == 0
    ):

        generated.append({
            "company_id": ticker,
            "type": "pro",
            "rule_id": 3,
            "text": "Debt-free balance sheet provides financial flexibility and eliminates interest burden.",
            "confidence_pct": 98,
        })

    # ---------- PRO RULE 4 ----------
    if (
        pd.notna(current["revenue_cagr_5yr"])
        and current["revenue_cagr_5yr"] > 15
    ):

        generated.append({
            "company_id": ticker,
            "type": "pro",
            "rule_id": 4,
            "text": "Revenue growing at above 15% CAGR over 5 years reflects strong business momentum.",
            "confidence_pct": 90,
        })

    # ---------- PRO RULE 5 ----------

    if (
        pd.notna(current["operating_profit_margin_pct"])
        and current["operating_profit_margin_pct"] > 25
    ):

        generated.append({
            "company_id": ticker,
            "type": "pro",
            "rule_id": 5,
            "text": "Operating profit margin above 25% indicates strong pricing power and cost discipline.",
            "confidence_pct": 90,
        })

    # ---------- PRO RULE 6 ----------
    if (
        pd.notna(current["pat_cagr_5yr"])
        and current["pat_cagr_5yr"] > 20
    ):

        generated.append({
            "company_id": ticker,
            "type": "pro",
            "rule_id": 6,
            "text": "Net profit compounding at above 20% over 5 years creates significant shareholder value.",
            "confidence_pct": 92,
        })
            # ---------- PRO RULE 7 ----------
    if (
        (
            pd.notna(current["interest_coverage"])
            and current["interest_coverage"] > 10
        )
        or (
            pd.notna(current["debt_to_equity"])
            and current["debt_to_equity"] == 0
        )
    ):

        generated.append({
            "company_id": ticker,
            "type": "pro",
            "rule_id": 7,
            "text": "Very high interest coverage ratio reflects negligible financial stress from debt servicing.",
            "confidence_pct": 90,
        })

    # ---------- PRO RULE 8 ----------
    dividend = market[
        (market["company_id"] == ticker)
        & (market["year"] == 2024)
    ]

    if (
        not dividend.empty
        and pd.notna(dividend.iloc[0]["dividend_yield_pct"])
        and dividend.iloc[0]["dividend_yield_pct"] > 2
        and pd.notna(current["free_cash_flow_cr"])
        and current["free_cash_flow_cr"] > 0
    ):

        generated.append({
            "company_id": ticker,
            "type": "pro",
            "rule_id": 8,
            "text": "Consistent dividend yield above 2% backed by positive free cash flow.",
            "confidence_pct": 88,
        })

    # ---------- PRO RULE 9 ----------
    if (
        pd.notna(current.get("eps_cagr_5yr"))
        and current["eps_cagr_5yr"] > 15
    ):

        generated.append({
            "company_id": ticker,
            "type": "pro",
            "rule_id": 9,
            "text": "Earnings per share growing above 15% CAGR indicates strong earnings quality and compounding.",
            "confidence_pct": 90,
        })

    # ---------- PRO RULE 10 ----------
    roe = history["source_roe_pct"].dropna()

    if (
        len(roe) >= 3
        and roe.iloc[-3] < roe.iloc[-2] < roe.iloc[-1]
    ):

        generated.append({
            "company_id": ticker,
            "type": "pro",
            "rule_id": 10,
            "text": "Return on equity improving for 3 consecutive years shows strengthening business quality.",
            "confidence_pct": 85,
        })

    # ---------- PRO RULE 11 ----------
    if (
        pd.notna(current["revenue_cagr_5yr"])
        and pd.notna(current["pat_cagr_5yr"])
        and current["pat_cagr_5yr"] > current["revenue_cagr_5yr"]
    ):

        generated.append({
            "company_id": ticker,
            "type": "pro",
            "rule_id": 11,
            "text": "Revenue growing slower than profits shows improving operating leverage and scale benefits.",
            "confidence_pct": 87,
        })

    # ---------- PRO RULE 12 ----------
    assets = bs[
        bs["company_id"] == ticker
    ].sort_values("year")

    debt = history["debt_to_equity"].dropna()

    if (
        len(assets) >= 2
        and "total_assets" in assets.columns
        and assets["total_assets"].iloc[-1] > assets["total_assets"].iloc[-2]
        and len(debt) >= 2
        and debt.iloc[-1] < debt.iloc[-2]
    ):

        generated.append({
            "company_id": ticker,
            "type": "pro",
            "rule_id": 12,
            "text": "Growing asset base funded by internal accruals reflects self-sustaining growth.",
            "confidence_pct": 85,
        })

if ticker == "TCS":
    print("\n===== TCS PROS GENERATED SO FAR =====")
    for item in generated:
        if item["company_id"] == "TCS":
            print(item)



            # ---------- CON RULE 1 ----------
    sector = sectors[
        sectors["company_id"] == ticker
    ]

    is_financial = (
        not sector.empty
        and sector.iloc[0]["broad_sector"] == "Financials"
    )

    if (
        not is_financial
        and pd.notna(current["debt_to_equity"])
        and current["debt_to_equity"] > 2
    ):

        generated.append({
            "company_id": ticker,
            "type": "con",
            "rule_id": 1,
            "text": f"Debt-to-equity ratio of {current['debt_to_equity']:.2f} is elevated for a non-financial company and warrants monitoring.",
            "confidence_pct": 90,
        })

    # ---------- CON RULE 2 ----------
    fcf = history["free_cash_flow_cr"].dropna()

    if (
        len(fcf) >= 3
        and (fcf.tail(3) < 0).all()
    ):

        generated.append({
            "company_id": ticker,
            "type": "con",
            "rule_id": 2,
            "text": "Free cash flow negative for 3 consecutive years raises concern about cash generation quality.",
            "confidence_pct": 90,
        })

    # ---------- CON RULE 3 ----------
    opm = history["operating_profit_margin_pct"].dropna()

    if (
        len(opm) >= 3
        and opm.iloc[-3] > opm.iloc[-2] > opm.iloc[-1]
    ):

        generated.append({
            "company_id": ticker,
            "type": "con",
            "rule_id": 3,
            "text": "Operating margins declining for 3 consecutive years suggest pricing or cost pressure.",
            "confidence_pct": 85,
        })

    # ---------- CON RULE 4 ----------
    profit = pl[
        pl["company_id"] == ticker
    ].sort_values("year")

    if (
        not profit.empty
        and pd.notna(profit.iloc[-1]["net_profit"])
        and profit.iloc[-1]["net_profit"] < 0
    ):

        generated.append({
            "company_id": ticker,
            "type": "con",
            "rule_id": 4,
            "text": "Company reported a net loss in the most recent financial year.",
            "confidence_pct": 95,
        })

    # ---------- CON RULE 5 ----------
    revenue = profit["sales"].dropna()

    if (
        len(revenue) >= 3
        and revenue.iloc[-2] < revenue.iloc[-3]
        and revenue.iloc[-1] < revenue.iloc[-2]
    ):

        generated.append({
            "company_id": ticker,
            "type": "con",
            "rule_id": 5,
            "text": "Revenue contraction over 2 consecutive years indicates demand weakness or market share loss.",
            "confidence_pct": 88,
        })

    # ---------- CON RULE 6 ----------
    if (
        pd.notna(current["interest_coverage"])
        and current["interest_coverage"] < 1.5
    ):

        generated.append({
            "company_id": ticker,
            "type": "con",
            "rule_id": 6,
            "text": "Interest coverage ratio below 1.5x indicates the company is at risk of not meeting its debt obligations.",
            "confidence_pct": 95,
        })
            # ---------- CON RULE 7 ----------
    if (
        pd.notna(current.get("dividend_payout_pct"))
        and current["dividend_payout_pct"] > 100
    ):

        generated.append({
            "company_id": ticker,
            "type": "con",
            "rule_id": 7,
            "text": "Dividend payout ratio above 100% means the company is paying dividends from reserves, which is unsustainable.",
            "confidence_pct": 90,
        })

    # ---------- CON RULE 8 ----------
    de = history["debt_to_equity"].dropna()

    if (
        len(de) >= 3
        and de.iloc[-3] < de.iloc[-2] < de.iloc[-1]
    ):

        generated.append({
            "company_id": ticker,
            "type": "con",
            "rule_id": 8,
            "text": "Rising debt-to-equity ratio over 3 years suggests increasing financial leverage risk.",
            "confidence_pct": 88,
        })

    # ---------- CON RULE 9 ----------
    if (
        "eps" in profit.columns
    ):

        eps = profit["eps"].dropna()

        if (
            len(eps) >= 3
            and eps.iloc[-3] > eps.iloc[-2] > eps.iloc[-1]
        ):

            generated.append({
                "company_id": ticker,
                "type": "con",
                "rule_id": 9,
                "text": "Earnings per share declining for 3 consecutive years reflects deteriorating profitability.",
                "confidence_pct": 90,
            })

    # ---------- CON RULE 10 ----------
    if (
        pd.notna(current["roce_pct"])
        and current["roce_pct"] < 10
    ):

        generated.append({
            "company_id": ticker,
            "type": "con",
            "rule_id": 10,
            "text": "Return on capital employed below 10% suggests the business is not generating sufficient returns on invested capital.",
            "confidence_pct": 90,
        })

    # ---------- CON RULE 11 ----------
    if (
        "net_debt_to_ebitda" in current.index
        and pd.notna(current["net_debt_to_ebitda"])
        and current["net_debt_to_ebitda"] > 3
    ):

        generated.append({
            "company_id": ticker,
            "type": "con",
            "rule_id": 11,
            "text": "Net debt exceeding 3 times EBITDA is a high leverage ratio and limits financial flexibility.",
            "confidence_pct": 92,
        })

    # ---------- CON RULE 12 ----------
    if (
        pd.notna(current["revenue_cagr_5yr"])
        and current["revenue_cagr_5yr"] < 5
    ):

        generated.append({
            "company_id": ticker,
            "type": "con",
            "rule_id": 12,
            "text": "Revenue growing at below 5% over 5 years lags inflation and suggests limited business momentum.",
            "confidence_pct": 85,
        })

generated_df = pd.DataFrame(generated)

print("\n===== TCS GENERATED RULES =====")
print(
    generated_df.loc[
        generated_df["company_id"] == "TCS",
        ["type", "rule_id", "text"]
    ]
)

generated_df = generated_df[
    generated_df["confidence_pct"] > 60
]

# ---------------- Fallback Rules ----------------

latest_profit = (
    pl[
        pl["year"] != "TTM"
    ]
    .sort_values("year")
    .groupby("company_id")
    .tail(1)
    .set_index("company_id")
)

for ticker in companies["id"]:

    company_entries = generated_df[
        generated_df["company_id"] == ticker
    ]

    has_pro = (company_entries["type"] == "pro").any()
    has_con = (company_entries["type"] == "con").any()

    # Fallback Pro
    if not has_pro:

        generated_df.loc[len(generated_df)] = {
            "company_id": ticker,
            "type": "pro",
            "rule_id": 99,
            "text": "The company continues to operate with an established business presence and remains under continuous financial evaluation.",
            "confidence_pct": 65,
        }

    # Fallback Con
    if not has_con:

        generated_df.loc[len(generated_df)] = {
            "company_id": ticker,
            "type": "con",
            "rule_id": 99,
            "text": "No major financial concerns were identified by the current rule set; continued monitoring is recommended.",
            "confidence_pct": 65,
        }

generated_df.to_csv(
    OUTPUT_DIR / "pros_cons_generated.csv",
    index=False,
)

print(f"Generated statements : {len(generated_df)}")

summary = (
    generated_df
    .groupby(["company_id", "type"])
    .size()
    .unstack(fill_value=0)
)

missing_pro = summary[summary.get("pro", 0) == 0]
missing_con = summary[summary.get("con", 0) == 0]

print(f"Companies without Pro : {len(missing_pro)}")
print(f"Companies without Con : {len(missing_con)}")

if len(missing_pro):
    print("\nMissing Pro:")
    print(missing_pro.index.tolist())

if len(missing_con):
    print("\nMissing Con:")
    print(missing_con.index.tolist())