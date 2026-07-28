import sqlite3
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"
OUTPUT_DIR = PROJECT_ROOT / "output"

OUTPUT_DIR.mkdir(exist_ok=True)


def get_connection():
    """Return SQLite connection."""
    return sqlite3.connect(DB_PATH)


def load_latest_ratios():
    """Load the latest financial ratios for each company."""

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


def generate_portfolio_statistics():

    df = load_latest_ratios()

    candidate_metrics = [
        "return_on_equity_pct",
        "operating_profit_margin_pct",
        "net_profit_margin_pct",
        "debt_to_equity",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "eps_cagr_5yr",
        "free_cash_flow_cr",
        "cash_conversion_ratio",
        "composite_quality_score",
    ]

    metrics = [m for m in candidate_metrics if m in df.columns]

    rows = []

    for metric in metrics:

        values = pd.to_numeric(df[metric], errors="coerce").dropna()

        if values.empty:
            continue

        rows.append(
            {
                "metric": metric,
                "P10": values.quantile(0.10),
                "P25": values.quantile(0.25),
                "P50": values.quantile(0.50),
                "P75": values.quantile(0.75),
                "P90": values.quantile(0.90),
                "Mean": values.mean(),
                "Std": values.std(),
                "Count": len(values),
            }
        )

    stats_df = pd.DataFrame(rows)

    output_file = OUTPUT_DIR / "portfolio_stats.csv"

    stats_df.to_csv(output_file, index=False)

    print(f"Metrics Processed : {len(stats_df)}")
    print(f"Saved to : {output_file}")


if __name__ == "__main__":
    generate_portfolio_statistics()
