import sqlite3
from pathlib import Path

import pandas as pd

# ==========================================================
# Paths
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"

OUTPUT_DIR = PROJECT_ROOT / "output"

OUTPUT_DIR.mkdir(exist_ok=True)

CLUSTER_FILE = OUTPUT_DIR / "cluster_labels.csv"

PROFILE_OUTPUT = OUTPUT_DIR / "cluster_profile_summary.csv"

# ==========================================================
# Database Connection
# ==========================================================


def get_connection():
    """
    Return SQLite database connection.
    """
    return sqlite3.connect(DB_PATH)


# ==========================================================
# Load Cluster Labels
# ==========================================================


def load_cluster_labels():
    """
    Load cluster assignments created in Day 36.
    """

    df = pd.read_csv(CLUSTER_FILE)

    print("=" * 60)
    print("Sprint 6 - Day 37")
    print("Cluster Profiling")
    print("=" * 60)

    print(f"\nCompanies Loaded : {len(df)}")

    return df


# ==========================================================
# Load Latest Financial Metrics
# ==========================================================


def load_financial_metrics():

    conn = get_connection()

    query = """
    SELECT

        fr.company_id,

        fr.return_on_equity_pct,

        fr.debt_to_equity,

        fr.revenue_cagr_5yr,

        fr.free_cash_flow_cr,

        fr.operating_profit_margin_pct,

        s.broad_sector

    FROM financial_ratios fr

    LEFT JOIN sectors s
        ON fr.company_id = s.company_id

    WHERE fr.year = (

        SELECT MAX(f2.year)

        FROM financial_ratios f2

        WHERE f2.company_id = fr.company_id

    )
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df


# ==========================================================
# Merge Cluster Labels
# ==========================================================


def prepare_dataset():

    clusters = load_cluster_labels()

    financials = load_financial_metrics()

    # Remove duplicate broad_sector since it already exists
    financials = financials.drop(columns=["broad_sector"])

    df = clusters.merge(financials, on="company_id", how="left")

    print("\n✓ Cluster dataset prepared.")

    return df


# ==========================================================
# Cluster Summary
# ==========================================================


def generate_cluster_summary(df):

    summary = (
        df.groupby(["cluster_id", "cluster_name"])
        .agg(
            companies=("company_id", "count"),
            avg_roe=("return_on_equity_pct", "mean"),
            avg_debt=("debt_to_equity", "mean"),
            avg_revenue_cagr=("revenue_cagr_5yr", "mean"),
            avg_fcf=("free_cash_flow_cr", "mean"),
            avg_opm=("operating_profit_margin_pct", "mean"),
        )
        .reset_index()
    )

    summary = summary.round(2)

    print("\n✓ Cluster statistics calculated.")

    return summary


# ==========================================================
# Sector Distribution
# ==========================================================


def generate_sector_distribution(df):

    sector_summary = (
        df.groupby(["cluster_id", "cluster_name", "broad_sector"])
        .size()
        .reset_index(name="companies")
        .sort_values(["cluster_id", "companies"], ascending=[True, False])
    )

    print("\n✓ Sector distribution calculated.")

    return sector_summary


# ==========================================================
# Export Results
# ==========================================================


def export_results(summary, sector_summary):

    summary.to_csv(OUTPUT_DIR / "cluster_profile_summary.csv", index=False)

    sector_summary.to_csv(OUTPUT_DIR / "cluster_sector_distribution.csv", index=False)

    print("\n✓ Cluster profile exported.")

    print("\nSaved Files:")

    print(OUTPUT_DIR / "cluster_profile_summary.csv")

    print(OUTPUT_DIR / "cluster_sector_distribution.csv")


# ==========================================================
# Main
# ==========================================================


def main():

    df = prepare_dataset()

    summary = generate_cluster_summary(df)

    sector_summary = generate_sector_distribution(df)

    export_results(summary, sector_summary)

    print("\n" + "=" * 60)

    print("Sprint 6 - Day 37 Completed")

    print("=" * 60)

    print(f"\nClusters : {df['cluster_id'].nunique()}")

    print(f"Companies : {len(df)}")


if __name__ == "__main__":
    main()
