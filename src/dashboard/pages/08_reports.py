import streamlit as st
import plotly.express as px
import sys
from pathlib import Path

# ----------------------------------
# Project Path
# ----------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from dashboard.utils.db import get_report_data

# ----------------------------------
# Page Config
# ----------------------------------

st.set_page_config(
    page_title="Reports",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Financial Reports")

st.divider()

# ----------------------------------
# Load Data
# ----------------------------------

df = get_report_data()

companies = sorted(df["company_name"].dropna().unique())

selected_company = st.selectbox(
    "Select Company",
    companies
)

company_df = df[
    df["company_name"] == selected_company
].copy()

company_df = company_df.sort_values("year")

latest = company_df.iloc[-1]

st.subheader("Executive Summary")

c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "Revenue (₹ Cr)",
        f"{latest['sales']:,.0f}"
    )

with c2:
    st.metric(
        "Net Profit (₹ Cr)",
        f"{latest['net_profit']:,.0f}"
    )

with c3:
    st.metric(
        "EPS",
        round(latest["eps"], 2)
    )

c4, c5, c6 = st.columns(3)

with c4:
    st.metric(
        "ROE %",
        round(latest["return_on_equity_pct"], 2)
    )

with c5:
    st.metric(
        "Debt / Equity",
        round(latest["debt_to_equity"], 2)
    )

with c6:
    st.metric(
        "Quality Score",
        round(latest["composite_quality_score"], 2)
    )

st.divider()

st.subheader("Revenue vs Net Profit")

fig = px.bar(

    company_df,

    x="year",

    y=["sales", "net_profit"],

    barmode="group",

    title="Revenue vs Net Profit"

)

st.plotly_chart(
    fig,
    width="stretch"
)

st.subheader("Operating Cash Flow")

fig = px.line(

    company_df,

    x="year",

    y="operating_activity",

    markers=True,

    title="Operating Cash Flow"

)

st.plotly_chart(
    fig,
    width="stretch"
)

st.subheader("Financial Report")

st.dataframe(
    company_df,
    width="stretch"
)

csv = company_df.to_csv(index=False)

st.download_button(

    label="📥 Download CSV Report",

    data=csv,

    file_name=f"{selected_company}_report.csv",

    mime="text/csv"
)