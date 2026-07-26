import streamlit as st
import plotly.express as px
import pandas as pd
import sys
from pathlib import Path

# ----------------------------------
# Project Path
# ----------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]

SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from dashboard.utils.db import (
    get_companies,
    get_pl,
    get_cf,
    get_ratios
)

# ----------------------------------
# Page Config
# ----------------------------------

st.set_page_config(
    page_title="Company Profile",
    page_icon="🏢",
    layout="wide"
)

st.title("🏢 Company Profile")

st.divider()

# ----------------------------------
# Load Companies
# ----------------------------------

companies = get_companies()

company_names = companies["company_name"].tolist()

selected_company = st.selectbox(
    "Search Company",
    company_names
)

company = companies[
    companies["company_name"] == selected_company
].iloc[0]

company_id = company["id"]
# ----------------------------------
# Company Card
# ----------------------------------

st.subheader("Company Overview")

left, right = st.columns([1, 3])

with left:

    st.image(
        "src/dashboard/assets/default_company_logo.png",
        width=200
    )

with right:

    st.markdown(
        f"## {company['company_name']}"
    )

    st.write(
        f"**Ticker :** {company_id}"
    )

    if pd.notna(company["website"]):

        st.markdown(
            f"**Website :** {company['website']}"
        )

    st.write("")

    if pd.notna(company["about_company"]):

        st.write(
            company["about_company"]
        )

st.divider()

# ----------------------------------
# ROE & ROCE
# ----------------------------------

st.subheader("Company Highlights")

c1, c2 = st.columns(2)

with c1:

    st.metric(
        "ROE %",
        round(
            company["roe_percentage"],
            2
        )
        if pd.notna(company["roe_percentage"])
        else "N/A"
    )

with c2:

    st.metric(
        "ROCE %",
        round(
            company["roce_percentage"],
            2
        )
        if pd.notna(company["roce_percentage"])
        else "N/A"
    )

st.divider()
# ----------------------------------
# Financial Data
# ----------------------------------

pl = get_pl(company_id)

ratios = get_ratios(company_id)
cf = get_cf(company_id)

if not pl.empty:

    pl = pl.copy()

    pl["year"] = (
        pl["year"]
        .str.replace("Mar ", "", regex=False)
    )

    latest = pl.iloc[-1]

else:

    latest = None
# ----------------------------------
# Financial KPI Cards
# ----------------------------------

st.subheader("Financial Highlights")

if latest is not None:

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

    latest_cf = None

    if not cf.empty:
        latest_cf = cf.iloc[-1]

    with c4:

        if latest_cf is not None:

            st.metric(
                "Operating Cash Flow",
                f"{latest_cf['operating_activity']:,.0f}"
            )

        else:

            st.metric(
                "Operating Cash Flow",
                "N/A"
            )

    with c5:

        st.metric(
            "ROE %",
            round(company["roe_percentage"], 2)
        )

    with c6:

        st.metric(
            "ROCE %",
            round(company["roce_percentage"], 2)
        )

st.divider()

# ----------------------------------
# Revenue Trend
# ----------------------------------

st.subheader("Revenue Trend")

fig = px.bar(

    pl,

    x="year",

    y="sales",

    text="sales",

    title="Revenue (₹ Crore)"

)

fig.update_traces(

    textposition="outside"

)

st.plotly_chart(

    fig,

    width="stretch"

)

# ----------------------------------
# Net Profit Trend
# ----------------------------------

st.subheader("Net Profit Trend")

fig = px.bar(

    pl,

    x="year",

    y="net_profit",

    text="net_profit",

    title="Net Profit (₹ Crore)"

)

fig.update_traces(

    textposition="outside"

)

st.plotly_chart(

    fig,

    width="stretch"

)

# ----------------------------------
# ROE Trend
# ----------------------------------

st.subheader("📈 ROE Trend")

if not ratios.empty:

    roe = ratios.copy()

    roe["year"] = (
        roe["year"]
        .str.replace("Mar ", "", regex=False)
    )

    fig = px.line(

        roe,

        x="year",

        y="return_on_equity_pct",

        markers=True,

        title="Return on Equity (%)"

    )

    st.plotly_chart(

        fig,

        width="stretch"

    )

else:

    st.warning(
        "ROE history not available."
    )
# ----------------------------------
# ROCE Information
# ----------------------------------

st.info(
    "Historical ROCE trend is unavailable because yearly ROCE values are not present in the source dataset."
)

# ----------------------------------
# Pros & Cons
# ----------------------------------

st.divider()

st.subheader("📋 Pros & Cons")

left, right = st.columns(2)

with left:

    st.success("Pros")

    if company["roe_percentage"] >= 20:
        st.write("✔ Strong Return on Equity")

    if latest is not None:

        if latest["sales"] > 50000:
            st.write("✔ Large Revenue Base")

        if latest["net_profit"] > 5000:
            st.write("✔ Healthy Profitability")

with right:

    st.error("Cons")

    if not ratios.empty:

        latest_ratio = ratios.iloc[-1]

        if latest_ratio["debt_to_equity"] > 2:
            st.write("✖ High Debt")

        if latest_ratio["interest_coverage"] < 2:
            st.write("✖ Weak Interest Coverage")

        if latest_ratio["free_cash_flow_cr"] < 0:
            st.write("✖ Negative Free Cash Flow")

    else:

        st.info("No risk data available.")