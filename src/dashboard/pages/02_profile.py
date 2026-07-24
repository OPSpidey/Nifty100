import re
import sqlite3

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Company Profile",
    page_icon="👤",
    layout="wide",
)

DB_PATH = "db/nifty100.db"

def safe_value(value, suffix=""):
    if pd.isna(value):
        return "N/A"
    
    return f"{value:.2f}{suffix}"

@st.cache_data(ttl=600)
def load_companies():
    conn = sqlite3.connect(DB_PATH)

    companies = pd.read_sql("""
    SELECT
        c.id,
        c.company_name,
        c.about_company,
        s.broad_sector,
        s.sub_sector
    FROM companies c
    LEFT JOIN sectors s
    ON c.id = s.company_id
    ORDER BY c.company_name
    """, conn)

    ratios = pd.read_sql("""
    SELECT
        company_id,
        year,
        source_roe_pct,
        source_roce_pct,
        return_on_equity_pct,
        roce_pct,
        net_profit_margin_pct,
        debt_to_equity,
        revenue_cagr_5yr,
        free_cash_flow_cr
    FROM financial_ratios
    """, conn)

    pl = pd.read_sql("""
    SELECT
        company_id,
        year,
        sales,
        net_profit
    FROM profitandloss
    """, conn)

    pros_cons = pd.read_sql("""
    SELECT
        company_id,
        pros,
        cons
    FROM prosandcons
    """, conn)

    conn.close()

    return companies, ratios, pl, pros_cons


companies, ratios, pl, pros_cons = load_companies()

st.title("👤 Company Profile")

search_options = (
    companies["company_name"] + " (" + companies["id"] + ")"
).tolist()

selected_company = st.selectbox(
    "🔍 Search Company",
    options=search_options,
    index=None,
    placeholder="Type company name or ticker...",
)

if selected_company:
    ticker = selected_company.split("(")[-1].replace(")", "").strip()

    company_match = companies[companies["id"] == ticker]

    if company_match.empty:
        st.warning("⚠️ Ticker not found — please try another.")
        st.stop()

    company = companies[companies["id"] == ticker].iloc[0]
    
    from html import unescape

    about = company["about_company"]

    if pd.notna(about):
        about = unescape(about)
        about = re.sub(r"<[^>]*>", "", about)
        about = re.sub(r"\n\s*\n+", "\n\n", about)
        about = about.strip()
    else:
        about = "Description not available."


    company_ratios = (
    ratios[
        (ratios["company_id"] == ticker) &
        (ratios["year"] != "TTM")
    ]
    .sort_values("year")
    )

    if company_ratios.empty:
        st.warning("Financial data not available.")
        st.stop()

    latest_ratio = company_ratios.iloc[-1]

    company_pl = (
    pl[
        (pl["company_id"] == ticker) &
        (pl["year"] != "TTM")
    ]
    .sort_values("year")
    )

    company_pc = pros_cons[pros_cons["company_id"] == ticker]

    st.markdown(
    f"""
    <div style="
    border:1px solid #333;
    border-radius:12px;
    padding:20px;
    background:#111827;
    margin-top:15px;
    ">

    <h2 style="margin-bottom:10px;">{company['company_name']}</h2>

    <p><b>🏷️ NSE Ticker:</b> {company['id']}</p>

    <p><b>🏭 Sector:</b> {company['broad_sector']}</p>

    <p><b>📂 Sub-sector:</b> {company['sub_sector']}</p>

    <p><b>📝 About Company</b></p>

    <p>{about}</p>

    </div>
    """,
    unsafe_allow_html=True,
    )

    st.markdown("### 📈 Financial KPIs")

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

    kpi(
        cols[0],
        "ROE",
        safe_value(
    latest_ratio["source_roe_pct"],
    "%"
    )
    )

    kpi(
        cols[1],
        "ROCE",
        safe_value(
    latest_ratio["source_roe_pct"],
    "%"
    )
    )

    kpi(
        cols[2],
        "Net Profit Margin",
        safe_value(
    latest_ratio["net_profit_margin_pct"],
    "%"
    )
    )

    kpi(
        cols[3],
        "Debt / Equity",
        safe_value(
    latest_ratio["debt_to_equity"]
    )
    )

    kpi(
    cols[4],
    "Revenue CAGR",
    safe_value(
        latest_ratio["revenue_cagr_5yr"],
        "%"
    )
    )

    kpi(
        cols[5],
        "Free Cash Flow",
        "N/A" if pd.isna(latest_ratio["free_cash_flow_cr"])
    else f'₹ {latest_ratio["free_cash_flow_cr"]:.2f} Cr'
    )

    st.markdown("---")
    st.subheader("📊 Revenue vs Net Profit (10 Years)")

    fig = px.bar(
        company_pl,
        x="year",
        y=["sales", "net_profit"],
        barmode="group",
        labels={
            "value": "₹ Crores",
            "year": "Financial Year",
            "variable": "Metric",
        },
        title="Revenue and Net Profit",
    )

    fig.update_layout(
        height=550,
        legend_title="",
        xaxis_title="Financial Year",
        yaxis_title="₹ Crores",
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("📈 ROE & ROCE Trend (10 Years)")

    fig = go.Figure()

    fig.add_trace(
    go.Scatter(
        x=company_ratios["year"],
        y=company_ratios["return_on_equity_pct"],
        mode="lines+markers",
        name="ROE (%)",
        line={"width": 3},
        yaxis="y1",
    )
    )

    fig.add_trace(
    go.Scatter(
        x=company_ratios["year"],
        y=company_ratios["roce_pct"],
        mode="lines+markers",
        name="ROCE (%)",
        line={"width": 3},
        yaxis="y2",
    )
    )

    fig.update_layout(
    title="ROE & ROCE Trend",
    height=550,
    hovermode="x unified",

    xaxis={
    "title": "Financial Year",
    },

    yaxis={
    "title": "ROE (%)",
    "side": "left",
    },

    yaxis2={
    "title": "ROCE (%)",
    "overlaying": "y",
    "side": "right",
    },

    legend={
    "orientation": "h",
    "y": 1.08,
    "x": 0.5,
    "xanchor": "center",
    }

    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("✅ Pros & ❌ Cons")

    if company_pc.empty:
        st.info("Pros & Cons are not available for this company.")
    else:
        left, right = st.columns(2)

        with left:
            st.markdown("### ✅ Pros")
            for pro in company_pc["pros"].dropna():
                st.success(pro)

        with right:
            st.markdown("### ❌ Cons")
            for con in company_pc["cons"].dropna():
                st.error(con)
