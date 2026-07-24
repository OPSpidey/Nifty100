import sqlite3

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Home",
    page_icon="🏠",
    layout="wide",
)

DB_PATH = "db/nifty100.db"

def safe_format(value, suffix=""):
    if pd.isna(value):
        return "N/A"
    return f"{value:.2f}{suffix}"

@st.cache_data(ttl=600)
def load_home_data():
    conn = sqlite3.connect(DB_PATH)

    ratios = pd.read_sql(
        "SELECT * FROM financial_ratios",
        conn,
    )

    market = pd.read_sql(
    "SELECT * FROM market_cap",
    conn,
    )

    companies = pd.read_sql(
        "SELECT id FROM companies",
        conn,
    )

    sector_df = pd.read_sql(
    """
    SELECT
        broad_sector,
        COUNT(company_id) AS company_count
    FROM sectors
    GROUP BY broad_sector
    ORDER BY company_count DESC
    """,
    conn,
    )

    top5_df = pd.read_sql(
    """
    SELECT
        company_id,
        year,
        composite_quality_score,
        source_roe_pct,
        source_roce_pct
    FROM financial_ratios
    ORDER BY composite_quality_score DESC
    """,
    conn,
    )


    conn.close()

    return ratios, market, companies, sector_df, top5_df

st.title("🏠 Home")

selected_year = st.sidebar.selectbox(
    "📅 Select Financial Year",
    ["2019", "2020", "2021", "2022", "2023", "2024"],
    index=5,
)

ratios, market, companies, sector_df, top5_df = load_home_data()

ratios = ratios.replace(
    [float("inf"), -float("inf")],
    pd.NA
)

market = market.replace(
    [float("inf"), -float("inf")],
    pd.NA
)

top5_df = top5_df.replace(
    [float("inf"), -float("inf")],
    pd.NA
)

ratio_year = f"Mar {selected_year}"

top5_df = top5_df[top5_df["year"] == ratio_year].nlargest(
    5, "composite_quality_score"
)

ratios = ratios[ratios["year"] == ratio_year]
market = market[market["year"] == int(selected_year)]

avg_roe = ratios["source_roe_pct"].mean()
median_pe = market["pe_ratio"].median()
median_de = ratios["debt_to_equity"].median()
total_companies = companies["id"].nunique()
median_rev_cagr = ratios["revenue_cagr_5yr"].median()
debt_free = (ratios["debt_to_equity"] == 0).sum()


cols = st.columns(6)


def kpi(col, title, value):
    html = f"""
<div style="border:1px solid #333;border-radius:10px;padding:18px;background:#111827;text-align:center;">
    <div style="font-size:16px;color:#bbbbbb;margin-bottom:12px;">
        {title}
    </div>
    <div style="font-size:30px;font-weight:bold;color:white;">
        {value}
    </div>
</div>
"""

    col.markdown(html, unsafe_allow_html=True)


kpi(cols[0], "Average ROE", safe_format(avg_roe, "%"))
kpi(cols[1], "Median P/E", safe_format(median_pe))
kpi(cols[2], "Median D/E", safe_format(median_de))
kpi(cols[3], "Companies", f"{total_companies}")
kpi(cols[4], "Rev CAGR", safe_format(median_rev_cagr, "%"))
kpi(cols[5], "Debt-Free", f"{debt_free}")


st.markdown("---")
st.subheader("📊 Sector Breakdown")

if sector_df.empty:
    st.warning("Sector data unavailable.")
    st.stop()

fig = px.pie(
    sector_df,
    names="broad_sector",
    values="company_count",
    hole=0.55,
    title="Nifty 100 Sector Distribution"
)

fig.update_traces(
    textposition="inside",
    textinfo="percent+label"
)

fig.update_layout(
    height=600,
    title_x=0.5,
    legend={
    "orientation": "h",
    "y": -0.15,
    "x": 0.5,
    "xanchor": "center",
    "yanchor": "top",
},
    margin={
    "t": 60,
    "b": 80,
    "l": 20,
    "r": 20,
}
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("🏆 Top 5 Companies by Composite Quality Score")

top5_display = top5_df.rename(
    columns={
        "company_id": "Company",
        "composite_quality_score": "Quality Score",
        "source_roe_pct": "ROE (%)",
        "source_roce_pct": "ROCE (%)",
    }
)

top5_display["ROE (%)"] = top5_display["ROE (%)"].round(2)
top5_display["ROE (%)"] = top5_display["ROE (%)"].where(
    top5_display["ROE (%)"].notna(),
    float("nan")
)

top5_display = top5_display.fillna("N/A")

st.dataframe(
    top5_display,
    width="stretch",
    hide_index=True,
)