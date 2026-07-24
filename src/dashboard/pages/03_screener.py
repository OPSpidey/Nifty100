import sqlite3

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Screener",
    page_icon="🔎",
    layout="wide",
)

DB_PATH = "db/nifty100.db"

def clean_numeric(df):
    numeric_cols = [
        "source_roe_pct",
        "debt_to_equity",
        "free_cash_flow_cr",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "operating_profit_margin_pct",
        "interest_coverage",
        "composite_quality_score",
        "pe_ratio",
        "pb_ratio",
        "dividend_yield_pct",
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    return df

@st.cache_data(ttl=600)
def load_data():
    conn = sqlite3.connect(DB_PATH)

    ratios = pd.read_sql("""
    SELECT
        fr.company_id,
        c.company_name,
        s.broad_sector,

        fr.source_roe_pct,
        fr.debt_to_equity,
        fr.free_cash_flow_cr,
        fr.revenue_cagr_5yr,
        fr.pat_cagr_5yr,
        fr.operating_profit_margin_pct,
        fr.interest_coverage,
        fr.composite_quality_score,

        mc.pe_ratio,
        mc.pb_ratio,
        mc.dividend_yield_pct

    FROM financial_ratios fr

    JOIN companies c
        ON fr.company_id = c.id

    LEFT JOIN sectors s
        ON fr.company_id = s.company_id

    LEFT JOIN market_cap mc
        ON fr.company_id = mc.company_id

    WHERE fr.year='Mar 2024'
      AND mc.year=2024
    """, conn)

    conn.close()

    return ratios


df = load_data()
df = clean_numeric(df)


st.title("🔎 Stock Screener")
st.subheader("📌 Quick Presets")

c1, c2, c3, c4, c5, c6 = st.columns(6)

if c1.button("⭐ Quality"):
    st.session_state.roe_min = 20.0
    st.session_state.de_max = 1.0
    st.session_state.fcf_min = 0.0
    st.session_state.rev_cagr_min = 10.0
    st.session_state.pat_cagr_min = 10.0
    st.session_state.opm_min = 15.0
    st.session_state.pe_max = 100.0
    st.session_state.pb_max = 25.0
    st.session_state.dividend_min = 0.0
    st.session_state.icr_min = 3.0
    st.rerun()

if c2.button("💰 Value"):
    st.session_state.roe_min = 10.0
    st.session_state.de_max = 2.0
    st.session_state.fcf_min = 0.0
    st.session_state.rev_cagr_min = 0.0
    st.session_state.pat_cagr_min = 0.0
    st.session_state.opm_min = 5.0
    st.session_state.pe_max = 20.0
    st.session_state.pb_max = 3.0
    st.session_state.dividend_min = 0.0
    st.session_state.icr_min = 1.5
    st.rerun()

if c3.button("🚀 Growth"):
    st.session_state.roe_min = 15.0
    st.session_state.de_max = 2.0
    st.session_state.fcf_min = 0.0
    st.session_state.rev_cagr_min = 20.0
    st.session_state.pat_cagr_min = 20.0
    st.session_state.opm_min = 10.0
    st.session_state.pe_max = 150.0
    st.session_state.pb_max = 25.0
    st.session_state.dividend_min = 0.0
    st.session_state.icr_min = 2.0
    st.rerun()

if c4.button("💵 Dividend"):
    st.session_state.roe_min = 10.0
    st.session_state.de_max = 2.0
    st.session_state.fcf_min = 0.0
    st.session_state.rev_cagr_min = 5.0
    st.session_state.pat_cagr_min = 5.0
    st.session_state.opm_min = 5.0
    st.session_state.pe_max = 100.0
    st.session_state.pb_max = 10.0
    st.session_state.dividend_min = 2.0
    st.session_state.icr_min = 1.5
    st.rerun()

if c5.button("🏦 Debt-Free"):
    st.session_state.roe_min = 10.0
    st.session_state.de_max = 0.0
    st.session_state.fcf_min = 0.0
    st.session_state.rev_cagr_min = 5.0
    st.session_state.pat_cagr_min = 5.0
    st.session_state.opm_min = 5.0
    st.session_state.pe_max = 150.0
    st.session_state.pb_max = 25.0
    st.session_state.dividend_min = 0.0
    st.session_state.icr_min = 2.0
    st.rerun()

if c6.button("🔄 Turnaround"):
    st.session_state.roe_min = 5.0
    st.session_state.de_max = 3.0
    st.session_state.fcf_min = -500.0
    st.session_state.rev_cagr_min = 15.0
    st.session_state.pat_cagr_min = 15.0
    st.session_state.opm_min = 5.0
    st.session_state.pe_max = 150.0
    st.session_state.pb_max = 25.0
    st.session_state.dividend_min = 0.0
    st.session_state.icr_min = 1.0
    st.rerun()



st.sidebar.header("Filters")

roe_min = st.sidebar.slider(
    "ROE Min (%)",
    0.0,
    100.0,
    value=st.session_state.get("roe_min", 15.0),
    key="roe_min",
)

de_max = st.sidebar.slider(
    "Debt / Equity Max",
    0.0,
    5.0,
    value=st.session_state.get("de_max", 1.0),
    key="de_max",
)

fcf_min = st.sidebar.slider(
    "Free Cash Flow Min (₹ Cr)",
    float(df["free_cash_flow_cr"].min()),
    float(df["free_cash_flow_cr"].max()),
    value=st.session_state.get("fcf_min", 0.0),
    key="fcf_min",
)

rev_cagr_min = st.sidebar.slider(
    "Revenue CAGR Min (%)",
    -20.0,
    100.0,
    value=st.session_state.get("rev_cagr_min", 10.0),
    key="rev_cagr_min",
)

pat_cagr_min = st.sidebar.slider(
    "PAT CAGR Min (%)",
    -20.0,
    100.0,
    value=st.session_state.get("pat_cagr_min", 10.0),
    key="pat_cagr_min",
)

opm_min = st.sidebar.slider(
    "Operating Margin Min (%)",
    0.0,
    80.0,
    value=st.session_state.get("opm_min", 15.0),
    key="opm_min",
)

pe_max = st.sidebar.slider(
    "P/E Max",
    0.0,
    150.0,
    value=st.session_state.get("pe_max", 40.0),
    key="pe_max",
)

pb_max = st.sidebar.slider(
    "P/B Max",
    0.0,
    25.0,
    value=st.session_state.get("pb_max", 10.0),
    key="pb_max",
)

dividend_min = st.sidebar.slider(
    "Dividend Yield Min (%)",
    0.0,
    10.0,
    value=st.session_state.get("dividend_min", 0.0),
    key="dividend_min",
)

icr_min = st.sidebar.slider(
    "Interest Coverage Min",
    0.0,
    100.0,
    value=st.session_state.get("icr_min", 2.0),
    key="icr_min",
)

st.success("✅ Sidebar filters loaded successfully.")

df = df.fillna(0)

filtered = df.copy()

filtered = filtered[
    (filtered["source_roe_pct"] >= roe_min)
    & (filtered["debt_to_equity"] <= de_max)
    & (filtered["free_cash_flow_cr"] >= fcf_min)
    & (filtered["revenue_cagr_5yr"] >= rev_cagr_min)
    & (filtered["pat_cagr_5yr"] >= pat_cagr_min)
    & (filtered["operating_profit_margin_pct"] >= opm_min)
    & (filtered["pe_ratio"] <= pe_max)
    & (filtered["pb_ratio"] <= pb_max)
    & (filtered["dividend_yield_pct"] >= dividend_min)
    & (filtered["interest_coverage"] >= icr_min)
]

filtered = filtered.sort_values(
    "composite_quality_score",
    ascending=False,
)

st.markdown("---")

st.subheader(
    f"📊 {len(filtered)} Companies Match Your Filters"
)

display_df = filtered[
    [
        "company_id",
        "company_name",
        "broad_sector",
        "composite_quality_score",
        "source_roe_pct",
        "debt_to_equity",
        "free_cash_flow_cr",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "operating_profit_margin_pct",
        "interest_coverage",
        "pe_ratio",
        "pb_ratio",
        "dividend_yield_pct",
    ]
].copy()

display_df.columns = [
    "Ticker",
    "Company",
    "Sector",
    "Composite Score",
    "ROE (%)",
    "Debt / Equity",
    "FCF (₹ Cr)",
    "Revenue CAGR (%)",
    "PAT CAGR (%)",
    "OPM (%)",
    "ICR",
    "P/E",
    "P/B",
    "Dividend Yield (%)",
]

display_df = display_df.fillna("N/A")
if filtered.empty:
    st.info("No companies match your selected filters.")

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
)

csv = display_df.to_csv(index=False).encode("utf-8")

st.download_button(
    "📥 Download CSV",
    csv,
    file_name="stock_screener_results.csv",
    mime="text/csv",
)