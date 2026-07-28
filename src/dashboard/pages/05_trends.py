import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

# ----------------------------------
# Project Path
# ----------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from dashboard.utils.db import get_trend_data

# ----------------------------------
# Page Config
# ----------------------------------

st.set_page_config(page_title="Trend Analysis", page_icon="📉", layout="wide")

st.title("📉 Trend Analysis")

st.markdown("---")

df = get_trend_data()

companies = sorted(df["company_name"].dropna().unique())

selected_company = st.selectbox("Select Company", companies)

company_df = df[df["company_name"] == selected_company].copy()

company_df = company_df.sort_values("year")
metrics = st.multiselect(
    "Select Metrics",
    [
        "sales",
        "net_profit",
        "eps",
        "return_on_equity_pct",
        "operating_profit_margin_pct",
    ],
    default=["sales"],
)
if metrics:

    fig = px.line(
        company_df, x="year", y=metrics, markers=True, title="Company Financial Trends"
    )

    st.plotly_chart(fig, width="stretch")
    st.subheader("Financial Data")

st.dataframe(company_df, width="stretch")
