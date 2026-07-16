import streamlit as st

st.set_page_config(
    page_title="Nifty 100 Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📈 Nifty 100 Analytics Dashboard")

st.success("Welcome to the Nifty 100 Financial Analytics Dashboard!")

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