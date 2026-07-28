import sys
from pathlib import Path

import streamlit as st

# ----------------------------------
# Project Path
# ----------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from dashboard.utils.db import get_screener_data

# ----------------------------------
# Page Config
# ----------------------------------

st.set_page_config(page_title="Stock Screener", page_icon="📊", layout="wide")

st.title("📊 Nifty 100 Stock Screener")

st.markdown("---")

# ----------------------------------
# Load Data
# ----------------------------------

df = get_screener_data()

# ----------------------------------
# Latest Financial Year
# ----------------------------------

if df.empty:

    st.error("No screener data found.")

    st.stop()


# Remove Null Years

df = df.dropna(subset=["year"])


# Find Year Having Maximum Companies

year_counts = df["year"].value_counts()


latest_year = year_counts.idxmax()


# Keep Only Latest Financial Year

df = df[df["year"] == latest_year].copy()


# Display Information

st.success(f"Showing Latest Financial Year : {latest_year}")

st.info(f"Companies Available : {len(df)}")

# ----------------------------------
# Sidebar Filters
# ----------------------------------

st.sidebar.subheader("📌 Screener Mode")

preset = st.sidebar.radio(
    "Choose Mode",
    ["Custom", "Quality", "Value", "Growth", "Dividend", "Debt Free", "Turnaround"],
)

# ----------------------------------
# Free Cash Flow Limits
# ----------------------------------

fcf_values = df["free_cash_flow_cr"].fillna(0)

fcf_min = float(fcf_values.min())

fcf_max = float(fcf_values.max())

# Streamlit slider does not allow
# min_value == max_value.

if fcf_min == fcf_max:

    fcf_max = fcf_max + 1

roe = 0.0
de = 10.0
growth = -50.0
pat = -50.0
fcf = fcf_min
opm = 0.0
asset = 0.0
icr = 0.0
score = 0.0

# ----------------------------------
# Custom Filters
# ----------------------------------

if preset == "Custom":

    st.sidebar.subheader("Custom Filters")

    roe = st.sidebar.slider("Minimum ROE (%)", 0.0, 100.0, 0.0)

    de = st.sidebar.slider("Maximum Debt / Equity", 0.0, 10.0, 10.0)

    growth = st.sidebar.slider("Minimum Revenue CAGR (%)", -50.0, 100.0, -50.0)

    pat = st.sidebar.slider("Minimum PAT CAGR (%)", -50.0, 100.0, -50.0)

    # ----------------------------------
    # Free Cash Flow Filter
    # ----------------------------------

    fcf_default = fcf_min

    fcf_default = min(fcf_default, fcf_max)

    fcf = st.sidebar.slider(
        "Minimum Free Cash Flow",
        min_value=fcf_min,
        max_value=fcf_max,
        value=fcf_default,
    )

    # ----------------------------------
    # Remaining Filters
    # ----------------------------------

    asset = st.sidebar.slider("Minimum Asset Turnover", 0.0, 5.0, 0.0)

    icr = st.sidebar.slider("Minimum Interest Coverage", 0.0, 100.0, 0.0)

    score = st.sidebar.slider("Minimum Composite Score", 0.0, 100.0, 0.0)

# ----------------------------------
# Preset Filters
# ----------------------------------

elif preset == "Quality":

    roe = 20.0
    de = 1.0
    growth = 15.0
    score = 70.0


elif preset == "Value":

    roe = 15.0
    de = 1.0
    score = 60.0


elif preset == "Growth":

    roe = 15.0
    growth = 20.0
    pat = 20.0


elif preset == "Dividend":

    roe = 10.0
    fcf = 0.0


elif preset == "Debt Free":

    de = 0.05


elif preset == "Turnaround":

    growth = 5.0
    pat = 5.0


# ----------------------------------
# Apply Filters
# ----------------------------------

filtered = df.copy()


# ROE

if roe > 0:

    filtered = filtered[filtered["return_on_equity_pct"].fillna(0) >= roe]


# Debt / Equity

if de < 10:

    filtered = filtered[filtered["debt_to_equity"].fillna(999) <= de]


# Revenue CAGR

if growth > -50:

    filtered = filtered[filtered["revenue_cagr_5yr"].fillna(-999) >= growth]


# PAT CAGR

if pat > -50:

    filtered = filtered[filtered["pat_cagr_5yr"].fillna(-999) >= pat]


# Free Cash Flow

if fcf > fcf_min:

    filtered = filtered[filtered["free_cash_flow_cr"].fillna(fcf_min) >= fcf]


# Interest Coverage

if icr > 0:

    filtered = filtered[filtered["interest_coverage"].fillna(0) >= icr]


# Asset Turnover

if asset > 0:

    filtered = filtered[filtered["asset_turnover"].fillna(0) >= asset]


# Composite Score

if score > 0:

    filtered = filtered[filtered["composite_quality_score"].fillna(0) >= score]


# Reset Index

filtered = filtered.reset_index(drop=True)

# ----------------------------------
# Results Section
# ----------------------------------

st.subheader("📈 Filtered Companies")


if filtered.empty:

    st.warning("No companies match the selected filters.")


else:

    st.success(f"{len(filtered)} Companies Match Your Filters")

    required_columns = [
        "company_id",
        "company_name",
        "broad_sector",
        "return_on_equity_pct",
        "debt_to_equity",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "free_cash_flow_cr",
        "interest_coverage",
        "asset_turnover",
        "composite_quality_score",
    ]

    available_columns = [
        column for column in required_columns if column in filtered.columns
    ]

    result_df = filtered[available_columns].sort_values(
        "composite_quality_score", ascending=False
    )

    st.dataframe(result_df, width="stretch")

    csv = result_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name="screener_results.csv",
        mime="text/csv",
    )

# ----------------------------------
# Footer
# ----------------------------------

st.markdown("---")

st.success(f"Screener loaded successfully • Latest Financial Year : {latest_year}")
