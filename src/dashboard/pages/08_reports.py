import sqlite3
import pandas as pd
import streamlit as st
import requests


st.set_page_config(
    page_title="Annual Reports",
    page_icon="📄",
    layout="wide",
)


DB_PATH = "db/nifty100.db"

def safe_text(value):
    if pd.isna(value) or value == "":
        return "N/A"
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


    reports = pd.read_sql("""
    SELECT
        company_id,
        Year,
        Annual_Report
    FROM documents
    ORDER BY Year DESC
    """, conn)


    conn.close()

    return companies, reports



companies, reports = load_data()

companies["company_name"] = (
    companies["company_name"]
    .fillna("Unknown Company")
)

reports["Annual_Report"] = (
    reports["Annual_Report"]
    .fillna("")
)

st.title("📄 Annual Reports")


search_options = (
    companies["company_name"]
    + " ("
    + companies["id"]
    + ")"
).tolist()


selected_company = st.selectbox(
    "🔍 Search Company",
    search_options
)


ticker = (
    selected_company
    .split("(")[-1]
    .replace(")", "")
    .strip()
)


company_reports = reports[
    reports["company_id"] == ticker
]


st.markdown("---")


st.subheader(
    f"📑 Available Reports - {selected_company}"
)


if company_reports.empty:

    st.warning(
        "No annual reports available."
    )

else:

    for _, row in company_reports.iterrows():

        year = row["Year"]
        url = safe_text(
    row["Annual_Report"]
)


        col1, col2 = st.columns(
            [3,1]
        )


        with col1:

            st.write(
                f"📅 Annual Report {year}"
            )


        with col2:

            if url == "N/A":

                st.error(
        "❌ Report unavailable"
    )

            continue


try:

                headers = {
                    "User-Agent": "Mozilla/5.0"
                }

                response = requests.get(
                    url,
                    headers=headers,
                    timeout=10,
                    stream=True,
                    allow_redirects=True
                )

                if response.status_code == 200:

                    st.link_button(
                        "📥 Open PDF",
                        url
                    )

                else:

                    st.error(
                        "❌ Report unavailable"
                    )

except Exception:

                st.error(
                    "❌ Report unavailable"
                )