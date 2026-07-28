import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"
REPORTS_DIR = PROJECT_ROOT / "reports"

REPORTS_DIR.mkdir(exist_ok=True)


def get_connection():
    """Return SQLite connection."""
    return sqlite3.connect(DB_PATH)


def load_latest_ratios():
    """Load latest financial ratios for every company."""

    conn = get_connection()

    query = """
    SELECT fr.*
    FROM financial_ratios fr
    INNER JOIN (
        SELECT company_id, MAX(year) AS latest_year
        FROM financial_ratios
        GROUP BY company_id
    ) latest
    ON fr.company_id = latest.company_id
    AND fr.year = latest.latest_year
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df


def generate_heatmap():

    df = load_latest_ratios()

    candidate_columns = [
        "return_on_equity_pct",
        "return_on_capital_employed_pct",
        "operating_profit_margin_pct",
        "net_profit_margin_pct",
        "debt_to_equity",
        "current_ratio",
        "interest_coverage_ratio",
        "asset_turnover_ratio",
        "revenue_cagr_5yr",
        "eps_cagr_5yr",
        "free_cash_flow_cr",
        "cash_conversion_ratio",
        "composite_quality_score",
    ]

    available_columns = [c for c in candidate_columns if c in df.columns]

    corr = (
        df[available_columns]
        .apply(pd.to_numeric, errors="coerce")
        .corr(method="pearson")
    )

    plt.figure(figsize=(12, 10))

    sns.heatmap(
        corr,
        annot=True,
        cmap="coolwarm",
        fmt=".2f",
        square=True,
    )

    plt.title("Financial KPI Correlation Heatmap")

    plt.tight_layout()

    output_file = REPORTS_DIR / "correlation_heatmap.png"

    plt.savefig(output_file, dpi=300)

    plt.close()

    print(f"Heatmap saved to: {output_file}")


if __name__ == "__main__":
    generate_heatmap()
