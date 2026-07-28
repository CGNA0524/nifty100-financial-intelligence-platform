import sys
from pathlib import Path

import streamlit as st

# ======================================================
# Add Project Root to Python Path
# ======================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

# ======================================================
# Streamlit Configuration
# ======================================================

st.set_page_config(
    page_title="Nifty 100 Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ======================================================
# Dashboard Header
# ======================================================

st.title("📈 Nifty 100 Financial Intelligence Platform")

st.markdown("---")

st.success("Sprint 4 Dashboard Started Successfully!")

st.write("""
Welcome to the **Nifty 100 Financial Intelligence Platform**.

Use the navigation menu from the sidebar to explore all dashboard screens.
""")

# ======================================================
# Sidebar
# ======================================================

with st.sidebar:

    st.title("📊 Navigation")

    st.success("Dashboard Loaded")

    st.markdown("---")

    st.subheader("Sprint Progress")

    st.progress(0.50)

    st.write("Sprint 4")

    st.write("Days 22 – 28")

    st.markdown("---")

    st.subheader("Available Screens")

    st.markdown("""
🏠 Home

🏢 Company Profile

📊 Screener

📈 Peer Comparison

📉 Trend Analysis

🏭 Sector Analysis

💰 Capital Allocation

📄 Reports
""")

    st.markdown("---")

    st.info("Select any page from the left sidebar.")

# ======================================================
# Main Page
# ======================================================

col1, col2 = st.columns([2, 1])

with col1:

    st.subheader("Project Overview")

    st.write("""
This dashboard provides:

- Company Financial Profiles
- Financial Ratio Analysis
- Stock Screener
- Peer Comparison
- Trend Analysis
- Sector Analytics
- Capital Allocation
- Reports & Insights
""")

with col2:

    st.metric("Project", "Nifty100")

    st.metric("Sprint", "Sprint 4")

    st.metric("Status", "In Progress")

st.markdown("---")

st.info("Navigate using the sidebar to access the dashboard pages.")
