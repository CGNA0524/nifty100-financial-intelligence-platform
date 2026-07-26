from pathlib import Path
import sqlite3
import pandas as pd

# =====================================================
# Project Paths
# =====================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"

OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_FILE = OUTPUT_DIR / "sector_intelligence.xlsx"


# =====================================================
# Load Sector Data
# =====================================================

def load_sectors():

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT
        company_id,
        broad_sector,
        sub_sector,
        index_weight_pct,
        market_cap_category
    FROM sectors
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df


# =====================================================
# Sector Health
# =====================================================

def get_sector_health(row):

    if row["avg_index_weight"] >= 2.50:
        return "Strong"

    elif row["avg_index_weight"] >= 1.50:
        return "Moderate"

    else:
        return "Emerging"


# =====================================================
# Sector Insight
# =====================================================

def get_sector_insight(row):

    if row["sector_health"] == "Strong":
        return (
            "High sector representation with strong presence in the Nifty 100."
        )

    elif row["sector_health"] == "Moderate":
        return (
            "Balanced sector representation with steady market participation."
        )

    else:
        return (
            "Lower representation but may offer future growth opportunities."
        )


# =====================================================
# Main
# =====================================================

def main():

    print("=" * 60)
    print("Sprint 5 - Day 33")
    print("Sector Intelligence Report")
    print("=" * 60)

    df = load_sectors()

    print("\nRows Loaded :", len(df))

    sector_summary = (
        df.groupby("broad_sector")
        .agg(
            companies=("company_id", "count"),
            avg_index_weight=("index_weight_pct", "mean"),
            large_cap=("market_cap_category", lambda x: (x == "Large Cap").sum()),
            mid_cap=("market_cap_category", lambda x: (x == "Mid Cap").sum()),
            small_cap=("market_cap_category", lambda x: (x == "Small Cap").sum())
        )
        .reset_index()
    )

    sector_summary["avg_index_weight"] = (
        sector_summary["avg_index_weight"].round(2)
    )

    sector_summary["sector_health"] = sector_summary.apply(
        get_sector_health,
        axis=1
        )

    sector_summary["sector_insight"] = sector_summary.apply(
        get_sector_insight,
        axis=1
        )

    sector_summary.to_excel(
        OUTPUT_FILE,
        index=False
    )

    print("\nSectors Found :", len(sector_summary))

    print("\nPreview:\n")
    print(sector_summary)

    print("\nSaved:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()