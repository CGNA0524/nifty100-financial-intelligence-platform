import sys
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from dashboard.utils.db import get_peer_data

st.set_page_config(page_title="Peer Comparison", page_icon="📈", layout="wide")

st.title("📈 Peer Comparison")

df = get_peer_data()

# Latest year only
latest_year = sorted(df["year"].dropna().unique())[-1]
df = df[df["year"] == latest_year].copy()

peer_groups = sorted(df["peer_group_name"].dropna().unique())

selected_group = st.selectbox("Select Peer Group", peer_groups)

peer_df = df[df["peer_group_name"] == selected_group]

companies = sorted(peer_df["company_name"].dropna().unique())

selected_company = st.selectbox("Select Company", companies)

company = peer_df[peer_df["company_name"] == selected_company].iloc[0]
metrics = [
    "return_on_equity_pct",
    "debt_to_equity",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "asset_turnover",
    "interest_coverage",
    "free_cash_flow_cr",
    "composite_quality_score",
]

company_values = []

for m in metrics:
    company_values.append(float(company[m]) if company[m] == company[m] else 0)

fig = go.Figure()

fig.add_trace(
    go.Scatterpolar(
        r=company_values, theta=metrics, fill="toself", name=selected_company
    )
)

fig.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=True)

st.plotly_chart(fig, width="stretch")

st.subheader("Peer Comparison Table")

st.dataframe(
    peer_df[
        [
            "company_name",
            "return_on_equity_pct",
            "debt_to_equity",
            "revenue_cagr_5yr",
            "pat_cagr_5yr",
            "composite_quality_score",
        ]
    ].sort_values("composite_quality_score", ascending=False),
    width="stretch",
)
