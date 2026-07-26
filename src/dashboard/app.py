import streamlit as st

st.set_page_config(
    page_title="Nifty 100 Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

with st.container():

    st.title("📈 Nifty 100 Analytics Dashboard")

    st.success("Welcome to the Nifty 100 Financial Analytics Dashboard!")

    col1, col2, col3 = st.columns(3)

    col1.metric("Companies", "92")
    col2.metric("Financial Years", "2012–2024")
    col3.metric("KPIs", "50+")

st.markdown(
    """
## Welcome

This dashboard provides comprehensive analytics for Nifty 100 companies.

### Available Modules

- 🏠 Home
- 👤 Company Profile
- 🔎 Screener
- 👥 Peer Analysis
- 📈 Trends
- 🏭 Sector Analysis
- 💰 Capital Allocation
- 📄 Reports

⬅️ **Use the sidebar to navigate between pages.**
"""
)

st.divider()

st.caption(
    "Nifty 100 Analytics Dashboard"
)