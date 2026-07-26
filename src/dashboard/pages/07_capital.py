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

from dashboard.utils.db import get_capital_data

# ----------------------------------
# Page Config
# ----------------------------------

st.set_page_config(
    page_title="Capital Allocation",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Capital Allocation")

st.divider()

# ----------------------------------
# Load Data
# ----------------------------------

df = get_capital_data()

companies = sorted(df["company_name"].unique())

selected = st.selectbox(
    "Select Company",
    companies
)

company_df = df[
    df["company_name"] == selected
].copy()

company_df = company_df.sort_values("year")
st.subheader("Cash Flow Overview")

latest = company_df.iloc[-1]

c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "Operating CF",
        f"{latest['operating_activity']:,.0f}"
    )

with c2:
    st.metric(
        "Investing CF",
        f"{latest['investing_activity']:,.0f}"
    )

with c3:
    st.metric(
        "Financing CF",
        f"{latest['financing_activity']:,.0f}"
    )

st.divider()

st.subheader("Cash Flow Trend")

fig = px.line(

    company_df,

    x="year",

    y=[
        "operating_activity",
        "investing_activity",
        "financing_activity"
    ],

    markers=True,

    title="Cash Flow History"
)

st.plotly_chart(
    fig,
    width="stretch"
)

st.subheader("Free Cash Flow")

fig = px.bar(

    company_df,

    x="year",

    y="free_cash_flow_cr",

    text="free_cash_flow_cr",

    title="Free Cash Flow"
)

fig.update_traces(
    textposition="outside"
)

st.plotly_chart(
    fig,
    width="stretch"
)

st.subheader("CAPEX")

fig = px.bar(

    company_df,

    x="year",

    y="capex_cr",

    text="capex_cr",

    title="Capital Expenditure"
)

fig.update_traces(
    textposition="outside"
)

st.plotly_chart(
    fig,
    width="stretch"
)

st.subheader("Capital Allocation Data")

st.dataframe(
    company_df,
    width="stretch"
)