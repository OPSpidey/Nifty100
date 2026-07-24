import sqlite3

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Capital Allocation",
    page_icon="💰",
    layout="wide",
)


DB_PATH = "db/nifty100.db"

def safe_text(value):
    if pd.isna(value):
        return "N/A"
    return value            


@st.cache_data(ttl=600)
def load_data():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql("""
    SELECT
        c.id AS company_id,
        c.company_name,
        fr.capital_allocation
    FROM companies c

    LEFT JOIN financial_ratios fr
    ON c.id = fr.company_id

    WHERE fr.year='Mar 2024'

    """, conn)


    conn.close()

    return df



df = load_data()

df = df.replace(
    [float("inf"), -float("inf")],
    pd.NA
)

st.title("💰 Capital Allocation Map")


df["capital_allocation"] = (
    df["capital_allocation"]
    .fillna("Unknown")
)

df["company_name"] = (
    df["company_name"]
    .fillna("Unknown Company")
)


st.subheader(
    "📊 Capital Allocation Patterns"
)

if df.empty:
    st.warning(
        "No capital allocation data available."
    )
    st.stop()

fig = px.treemap(
    df,

    path=[
        "capital_allocation",
        "company_name"
    ],

    values=None,

    title="Companies by Capital Allocation Pattern",

    hover_data=[
        "company_id"
    ],
)

fig.update_layout(
    height=700
)


selected = st.plotly_chart(
    fig,
    use_container_width=True,
    on_select="rerun",
)


st.markdown("---")


st.subheader(
    "🏢 Companies by Pattern"
)


patterns = sorted(
    df["capital_allocation"]
    .dropna()
    .unique()
)


selected_pattern = st.selectbox(
    "Select Capital Allocation Pattern",
    patterns
)


pattern_df = df[
    df["capital_allocation"] == selected_pattern
]


st.success(
    f"{len(pattern_df)} companies in {selected_pattern}"
)


st.dataframe(
    pattern_df[
        [
            "company_id",
            "company_name",
            "capital_allocation"
        ]
    ],
    hide_index=True,
    use_container_width=True,
)