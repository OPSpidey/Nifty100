import sqlite3

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Sector Analysis",
    page_icon="🏭",
    layout="wide",
)


DB_PATH = "db/nifty100.db"

def safe_numeric(value):
    if pd.isna(value):
        return 0
    return value


@st.cache_data(ttl=600)
def load_data():

    conn = sqlite3.connect(DB_PATH)

    data = pd.read_sql("""
    SELECT
        c.id AS company_id,
        c.company_name,

        s.broad_sector,
        s.sub_sector,

        fr.source_roe_pct,
        fr.return_on_equity_pct,
        fr.net_profit_margin_pct,
        fr.operating_profit_margin_pct,

        pl.sales,

        mc.market_cap_crore

    FROM companies c

    LEFT JOIN sectors s
    ON c.id = s.company_id

    LEFT JOIN financial_ratios fr
    ON c.id = fr.company_id
    AND fr.year='Mar 2024'

    LEFT JOIN profitandloss pl
    ON c.id = pl.company_id
    AND pl.year='Mar 2024'

    LEFT JOIN market_cap mc
    ON c.id = mc.company_id
    AND mc.year=2024

    """, conn)


    conn.close()

    return data



df = load_data()

df = df.replace(
    [float("inf"), -float("inf")],
    pd.NA
)

numeric_cols = [
    "source_roe_pct",
    "return_on_equity_pct",
    "net_profit_margin_pct",
    "operating_profit_margin_pct",
    "sales",
    "market_cap_crore",
]

for col in numeric_cols:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

st.title("🏭 Sector Analysis")


sector_list = sorted(
    df["broad_sector"]
    .dropna()
    .unique()
)


selected_sector = st.selectbox(
    "🏭 Select Sector",
    sector_list
)


sector_df = df[
    df["broad_sector"] == selected_sector
].copy()

numeric_cols = [
    "source_roe_pct",
    "return_on_equity_pct",
    "net_profit_margin_pct",
    "operating_profit_margin_pct",
    "sales",
    "market_cap_crore",
]

for col in numeric_cols:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

st.markdown("---")

st.subheader(
    "📊 Sector Company Bubble Map"
)
sector_df = sector_df.dropna(
    subset=[
        "sales",
        "return_on_equity_pct",
        "market_cap_crore"
    ]
)

fig = px.scatter(
    sector_df,

    x="sales",

    y="return_on_equity_pct",

    size="market_cap_crore",

    color="sub_sector",

    hover_name="company_name",

    hover_data=[
        "company_id",
        "source_roe_pct",
        "market_cap_crore",
        "sales",
    ],

    size_max=60,

    labels={
        "sales": "Revenue (₹ Cr)",
        "return_on_equity_pct": "ROE (%)",
        "market_cap_crore": "Market Cap (₹ Cr)",
    },

    title=f"{selected_sector} Companies",
)


fig.update_layout(
    height=650,
)


st.plotly_chart(
    fig,
    use_container_width=True
)

st.markdown("---")

st.subheader("📊 Sector Median KPI Comparison")

sector_df = sector_df.fillna(0)

median_kpi = (
    sector_df[
        [
            "return_on_equity_pct",
            "net_profit_margin_pct",
            "operating_profit_margin_pct",
            "source_roe_pct",
        ]
    ]
    .median()
    .reset_index()
)


median_kpi.columns = [
    "Metric",
    "Median Value"
]


metric_names = {
    "return_on_equity_pct": "ROE (%)",
    "net_profit_margin_pct": "Net Profit Margin (%)",
    "operating_profit_margin_pct": "Operating Margin (%)",
    "source_roe_pct": "Source ROE (%)",
}


median_kpi["Metric"] = (
    median_kpi["Metric"]
    .map(metric_names)
)


bar = px.bar(
    median_kpi,
    x="Metric",
    y="Median Value",
    text="Median Value",
    title=f"{selected_sector} Median KPIs",
)


bar.update_traces(
    texttemplate="%{text:.2f}",
    textposition="outside"
)


bar.update_layout(
    height=450,
    yaxis_title="Median Value (%)",
    xaxis_title=""
)


st.plotly_chart(
    bar,
    use_container_width=True
)