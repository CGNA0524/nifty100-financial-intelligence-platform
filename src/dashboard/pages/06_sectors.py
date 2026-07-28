import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from dashboard.utils.db import get_sector_analysis

st.set_page_config(page_title="Sector Analysis", page_icon="🏭", layout="wide")

st.title("🏭 Sector Analysis")

st.markdown("---")

df = get_sector_analysis()

# Latest year only
df = df.sort_values("year")

df = df.groupby("company_name", as_index=False).last()
sector = st.selectbox("Select Sector", sorted(df["broad_sector"].dropna().unique()))

sector_df = df[df["broad_sector"] == sector]
c1, c2, c3 = st.columns(3)

with c1:
    st.metric("Companies", len(sector_df))

with c2:
    st.metric("Average ROE", round(sector_df["return_on_equity_pct"].mean(), 2))

with c3:
    st.metric("Average Score", round(sector_df["composite_quality_score"].mean(), 2))
# ----------------------------------
# Clean Data For Plot
# ----------------------------------

plot_df = sector_df.copy()


plot_df["debt_to_equity"] = plot_df["debt_to_equity"].fillna(0)


plot_df["return_on_equity_pct"] = plot_df["return_on_equity_pct"].fillna(0)


plot_df["composite_quality_score"] = plot_df["composite_quality_score"].fillna(1)


plot_df["revenue_cagr_5yr"] = plot_df["revenue_cagr_5yr"].fillna(0)
plot_df = plot_df.reset_index(drop=True)

# ----------------------------------
# Scatter Plot
# ----------------------------------

fig = px.scatter(
    plot_df,
    x="debt_to_equity",
    y="return_on_equity_pct",
    size="composite_quality_score",
    color="revenue_cagr_5yr",
    hover_name="company_name",
    title="Sector Comparison",
)


st.plotly_chart(fig, width="stretch")


st.subheader("Companies")

st.dataframe(
    sector_df.sort_values("composite_quality_score", ascending=False), width="stretch"
)
