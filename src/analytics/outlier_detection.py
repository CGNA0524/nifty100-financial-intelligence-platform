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


def load_data():
    """Load latest financial ratios merged with sector information."""

    conn = get_connection()

    query = """
    SELECT
        fr.*,
        s.broad_sector,
        c.company_name
    FROM financial_ratios fr

    INNER JOIN (
        SELECT company_id, MAX(year) latest_year
        FROM financial_ratios
        GROUP BY company_id
    ) latest
        ON fr.company_id = latest.company_id
       AND fr.year = latest.latest_year

    LEFT JOIN sectors s
        ON fr.company_id = s.company_id

    LEFT JOIN companies c
        ON fr.company_id = c.id
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df


def detect_outliers():

    df = load_data()

    metrics = [
        "return_on_equity_pct",
        "operating_profit_margin_pct",
        "net_profit_margin_pct",
        "debt_to_equity",
        "revenue_cagr_5yr",
        "eps_cagr_5yr",
        "free_cash_flow_cr",
        "composite_quality_score",
    ]

    available_metrics = [m for m in metrics if m in df.columns]

    outliers = []

    for sector, sector_df in df.groupby("broad_sector"):

        for metric in available_metrics:

            values = pd.to_numeric(sector_df[metric], errors="coerce")

            mean = values.mean()
            std = values.std()

            if pd.isna(std) or std == 0:
                continue

            z_scores = (values - mean) / std

            sector_copy = sector_df.copy()
            sector_copy["metric"] = metric
            sector_copy["value"] = values
            sector_copy["z_score"] = z_scores

            flagged = sector_copy[sector_copy["z_score"].abs() > 3]

            outliers.append(flagged)

    if outliers:
        result = pd.concat(outliers, ignore_index=True)
    else:
        result = pd.DataFrame(
            columns=[
                "company_id",
                "company_name",
                "broad_sector",
                "metric",
                "value",
                "z_score",
            ]
        )

    result = result[
        [
            "company_id",
            "company_name",
            "broad_sector",
            "metric",
            "value",
            "z_score",
        ]
    ]

    output_file = OUTPUT_DIR / "outlier_report.csv"

    result.to_csv(output_file, index=False)

    print(f"Outliers Found : {len(result)}")
    print(f"Saved to : {output_file}")


if __name__ == "__main__":
    detect_outliers()
