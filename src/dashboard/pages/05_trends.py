import sqlite3
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(
    page_title="Trend Analysis",
    page_icon="📈",
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

    companies = pd.read_sql("""
    SELECT
        id,
        company_name
    FROM companies
    ORDER BY company_name
    """, conn)

    ratios = pd.read_sql("""
    SELECT
        company_id,
        year,
        return_on_equity_pct,
        roce_pct,
        net_profit_margin_pct,
        operating_profit_margin_pct,
        revenue_cagr_5yr,
        pat_cagr_5yr,
        debt_to_equity,
        interest_coverage,
        free_cash_flow_cr
    FROM financial_ratios
    WHERE year!='TTM'
    ORDER BY year
    """, conn)

    conn.close()

    return companies, ratios


companies, ratios = load_data()

st.title("📈 Trend Analysis")

search_options = (
    companies["company_name"]
    + " ("
    + companies["id"]
    + ")"
).tolist()

selected_company = st.selectbox(
    "🔍 Select Company",
    search_options,
)

ticker = selected_company.split("(")[-1].replace(")", "").strip()

company_df = (
    ratios[
        ratios["company_id"] == ticker
    ]
    .sort_values("year")
)

if company_df.empty:
    st.warning("No trend data available for this company.")
    st.stop()
    
metric_map = {
    "ROE (%)": "return_on_equity_pct",
    "ROCE (%)": "roce_pct",
    "Net Profit Margin (%)": "net_profit_margin_pct",
    "Operating Margin (%)": "operating_profit_margin_pct",
    "Revenue CAGR (%)": "revenue_cagr_5yr",
    "PAT CAGR (%)": "pat_cagr_5yr",
    "Debt / Equity": "debt_to_equity",
    "Interest Coverage": "interest_coverage",
    "Free Cash Flow": "free_cash_flow_cr",
}

selected_metrics = st.multiselect(
    "📊 Select up to 3 Metrics",
    options=list(metric_map.keys()),
    default=["ROE (%)"],
    max_selections=3,
)

st.markdown("---")
st.subheader("📈 10-Year Metric Trend")


if selected_metrics:

        fig = go.Figure()

        for metric in selected_metrics:

            column = metric_map[metric]

            trend_df = company_df[
                [
                    "year",
                    column
                ]
            ].copy()

            trend_df[column] = pd.to_numeric(
                trend_df[column],
                errors="coerce"
            )

        trend_df = trend_df.dropna()
        trend_df["YoY %"] = (
    trend_df[column]
    .pct_change(fill_method=None)
    * 100
)

        fig.add_trace(
        go.Scatter(
            x=trend_df["year"],
            y=trend_df[column],
            mode="lines+markers+text",
            name=metric,

            text=[
                ""
                if pd.isna(yoy)
                else f"{yoy:+.1f}%"
                for yoy in trend_df["YoY %"]
            ],

            textposition="top center",

            hovertemplate=
            "<b>%{x}</b><br>"
            + metric
            + ": %{y:.2f}<br>"
            + "YoY Change: %{text}"
            + "<extra></extra>",
        )
        )


        fig.update_layout(
        height=600,

        title=f"{selected_company} - Historical Trend",

        xaxis_title="Financial Year",

        yaxis_title="Value",

        hovermode="x unified",

        legend=dict(
        orientation="h",
        y=1.1,
        x=0.5,
        xanchor="center",
        ),
        )


        st.plotly_chart(
        fig,
        use_container_width=True,
        )

else:

    st.info(
    "Please select at least one metric."
    )