from pathlib import Path
import sqlite3
import pandas as pd

# =====================================================
# Project Paths
# =====================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"

OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_FILE = OUTPUT_DIR / "executive_summary.xlsx"


# =====================================================
# Load Executive Data
# =====================================================

def load_summary():

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT
        c.id,
        c.company_name,
        s.broad_sector,
        c.roe_percentage,
        c.roce_percentage,
        c.book_value,
        c.face_value
    FROM companies c
    LEFT JOIN sectors s
        ON c.id = s.company_id
    ORDER BY c.id
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df


# =====================================================
# Main
# =====================================================

def main():

    print("=" * 60)
    print("Sprint 5 - Day 35")
    print("Executive Summary Report")
    print("=" * 60)

    summary = load_summary()

    print("\nCompanies Loaded :", len(summary))

    summary["roe_percentage"] = summary["roe_percentage"].round(2)
    summary["roce_percentage"] = summary["roce_percentage"].round(2)

    total_companies = len(summary)
    total_sectors = summary["broad_sector"].nunique()
    avg_roe = summary["roe_percentage"].mean()
    avg_roce = summary["roce_percentage"].mean()

    executive_summary = pd.DataFrame({
        "Metric": [
            "Total Companies",
            "Total Sectors",
            "Average ROE (%)",
            "Average ROCE (%)"
        ],
        "Value": [
            total_companies,
            total_sectors,
            round(avg_roe, 2),
            round(avg_roce, 2)
        ]
    })

    executive_summary.to_excel(
        OUTPUT_FILE,
        index=False
    )

    print("\nExecutive Summary\n")
    print(executive_summary)

    print("\nSaved:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()