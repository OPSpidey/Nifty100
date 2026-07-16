import sqlite3
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(
    page_title="Peer Comparison",
    page_icon="👥",
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

    peer_groups = pd.read_sql("""
    SELECT
        pg.peer_group_name,
        pg.company_id,
        pg.is_benchmark,
        c.company_name
    FROM peer_groups pg
    JOIN companies c
        ON pg.company_id = c.id
    ORDER BY pg.peer_group_name, c.company_name
    """, conn)

    ratios = pd.read_sql("""
    SELECT
        company_id,
        year,
        return_on_equity_pct,
        roce_pct,
        net_profit_margin_pct,
        operating_profit_margin_pct,
        debt_to_equity,
        revenue_cagr_5yr,
        pat_cagr_5yr,
        interest_coverage,
        composite_quality_score
    FROM financial_ratios
    WHERE year='Mar 2024'
    """, conn)

    conn.close()

    return peer_groups, ratios


peer_groups, ratios = load_data()

st.title("👥 Peer Comparison")

peer_group = st.selectbox(
    "Select Peer Group",
    sorted(peer_groups["peer_group_name"].unique())
)

group_df = peer_groups[
    peer_groups["peer_group_name"] == peer_group
]

peer_ratios = ratios.merge(
    group_df[["company_id"]],
    on="company_id",
)

peer_ratios = peer_ratios.fillna(0)

company = st.selectbox(
    "Select Company",
    group_df["company_name"] + " (" + group_df["company_id"] + ")"
)

ticker = company.split("(")[-1].replace(")", "").strip()

company_data = peer_ratios[
    peer_ratios["company_id"] == ticker
]

if company_data.empty:
    st.warning("Financial data not available for this company.")
    st.stop()

company_metrics = company_data.iloc[0]

peer_avg = peer_ratios.mean(
    numeric_only=True
).fillna(0)

benchmark = group_df[
    group_df["is_benchmark"] == 1
]

if not benchmark.empty:
    benchmark_name = (
        benchmark.iloc[0]["company_name"]
        + " ("
        + benchmark.iloc[0]["company_id"]
        + ")"
    )

    st.success(f"🏆 Benchmark Company: {benchmark_name}")
else:
    st.warning("No benchmark company defined.")

    st.markdown("---")
st.subheader("📈 Company vs Peer Average")

metrics = [
    "return_on_equity_pct",
    "roce_pct",
    "net_profit_margin_pct",
    "operating_profit_margin_pct",
    "debt_to_equity",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "interest_coverage",
]

labels = [
    "ROE",
    "ROCE",
    "NPM",
    "OPM",
    "D/E",
    "Revenue CAGR",
    "PAT CAGR",
    "ICR",
]

fig = go.Figure()

fig.add_trace(
    go.Scatterpolar(
        r=[safe_numeric(company_metrics[m])for m in metrics],
        theta=labels,
        fill="toself",
        name="Selected Company",
    )
)

fig.add_trace(
    go.Scatterpolar(
        r=[
    safe_numeric(peer_avg[m])
    for m in metrics
],
        theta=labels,
        fill="toself",
        name="Peer Average",
    )
)

fig.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True
        )
    ),
    height=650,
    showlegend=True,
)

st.plotly_chart(
    fig,
    use_container_width=True,
)

st.markdown("---")
st.subheader("📋 Peer KPI Comparison")

comparison = (
    group_df[["company_id", "company_name", "is_benchmark"]]
    .merge(ratios, on="company_id")
)

comparison = comparison[
    [
        "company_name",
        "return_on_equity_pct",
        "roce_pct",
        "net_profit_margin_pct",
        "operating_profit_margin_pct",
        "debt_to_equity",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "interest_coverage",
        "composite_quality_score",
        "is_benchmark",
    ]
]

comparison.columns = [
    "Company",
    "ROE",
    "ROCE",
    "NPM",
    "OPM",
    "D/E",
    "Revenue CAGR",
    "PAT CAGR",
    "ICR",
    "Composite Score",
    "Benchmark",
]

def highlight_benchmark(row):
    if row["Benchmark"] == 1:
        return ["background-color:#1b5e20;color:white"] * len(row)
    return [""] * len(row)

styled = (
    comparison
    .style
    .apply(highlight_benchmark, axis=1)
    .hide(axis="index")
)

st.dataframe(
    styled,
    use_container_width=True,
)