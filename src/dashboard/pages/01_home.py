import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

# ======================================================
# Project Path
# ======================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

# ======================================================
# Database Functions
# ======================================================

from dashboard.utils.db import get_all_ratios, get_companies, get_sectors

# ======================================================
# Page Config
# ======================================================

st.set_page_config(page_title="Home", page_icon="🏠", layout="wide")

st.title("🏠 Nifty 100 Analytics Dashboard")

st.markdown("---")

# ======================================================
# Load Data
# ======================================================

companies = get_companies()
ratios = get_all_ratios()
sectors = get_sectors()

if companies.empty:
    st.error("Companies table is empty.")
    st.stop()

if ratios.empty:
    st.error("Financial Ratios table is empty.")
    st.stop()

# ======================================================
# Latest Financial Year (Maximum Company Coverage)
# ======================================================

year_counts = ratios.groupby("year").size().reset_index(name="count")

latest_year = year_counts.sort_values(["count", "year"], ascending=[False, False]).iloc[
    0
]["year"]

ratios = ratios[ratios["year"] == latest_year]

# ======================================================
# KPI Calculations
# ======================================================

total_companies = len(companies)

average_roe = round(ratios["return_on_equity_pct"].mean(), 2)

median_de = round(ratios["debt_to_equity"].median(), 2)

median_growth = round(ratios["revenue_cagr_5yr"].median(), 2)

debt_free = len(ratios[ratios["debt_to_equity"] == 0])

average_score = round(ratios["composite_quality_score"].mean(), 2)

# ======================================================
# KPI Cards
# ======================================================

st.subheader("📊 Dashboard Summary")

c1, c2, c3 = st.columns(3)

with c1:
    st.metric("Total Companies", total_companies)

with c2:
    st.metric("Average ROE %", average_roe)

with c3:
    st.metric("Median D/E", median_de)

c4, c5, c6 = st.columns(3)

with c4:
    st.metric("Median Revenue CAGR", median_growth)

with c5:
    st.metric("Debt Free Companies", debt_free)

with c6:
    st.metric("Average Quality Score", average_score)

st.markdown("---")

# ======================================================
# Sector Distribution
# ======================================================

st.subheader("🏭 Sector Distribution")

if not sectors.empty:

    sector_counts = sectors.groupby("broad_sector").size().reset_index(name="Companies")

    fig = px.pie(
        sector_counts,
        names="broad_sector",
        values="Companies",
        hole=0.45,
        title="Companies by Sector",
    )

    st.plotly_chart(fig, width="stretch")

st.markdown("---")

# ======================================================
# Top 5 Companies
# ======================================================

st.subheader("⭐ Top 5 Companies by Composite Quality Score")

top5 = ratios.sort_values("composite_quality_score", ascending=False).head(5)

top5 = top5.merge(
    companies[["id", "company_name"]], left_on="company_id", right_on="id", how="left"
)

st.dataframe(
    top5[
        [
            "company_id",
            "company_name",
            "return_on_equity_pct",
            "debt_to_equity",
            "revenue_cagr_5yr",
            "composite_quality_score",
        ]
    ],
    width="stretch",
)

st.markdown("---")

# ======================================================
# Footer
# ======================================================

st.success(f"Dashboard loaded successfully • Latest Financial Year : {latest_year}")
