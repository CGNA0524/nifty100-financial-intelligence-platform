import sqlite3
from pathlib import Path

import pandas as pd

# =====================================================
# Project Paths
# =====================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"
OUTPUT_DIR = PROJECT_ROOT / "output"

OUTPUT_FILE = OUTPUT_DIR / "cashflow_intelligence.xlsx"


def load_cashflow():

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT
        company_id,
        year,
        operating_activity,
        investing_activity,
        financing_activity,
        net_cash_flow
    FROM cashflow
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df


def main():

    print("=" * 60)
    print("Sprint 5 - Day 31")
    print("Cash Flow Intelligence")
    print("=" * 60)

    # ==========================================
    # Load Cashflow Data
    # ==========================================

    df = load_cashflow()

    print("\nRows Loaded :", len(df))

    # Keep latest record for each company
    latest = df.sort_values("year").groupby("company_id", as_index=False).last()

    print("Latest Company Records :", len(latest))

    # ==========================================
    # Generate Cashflow Insights
    # ==========================================

    generated_rows = []

    for _, row in latest.iterrows():

        insights = []

        # Operating Cash Flow
        if pd.notna(row["operating_activity"]):
            if row["operating_activity"] > 0:
                insights.append("Positive Operating Cash Flow")
            else:
                insights.append("Negative Operating Cash Flow")

        # Investing Cash Flow
        if pd.notna(row["investing_activity"]):
            if row["investing_activity"] < 0:
                insights.append("Investing in Business")
            else:
                insights.append("Reduced Capital Investment")

        # Financing Cash Flow
        if pd.notna(row["financing_activity"]):
            if row["financing_activity"] > 0:
                insights.append("Raised Capital")
            else:
                insights.append("Capital Returned / Debt Repaid")

        # Net Cash Flow
        if pd.notna(row["net_cash_flow"]):
            if row["net_cash_flow"] > 0:
                insights.append("Cash Balance Increased")
            else:
                insights.append("Cash Balance Declined")

        generated_rows.append(
            {
                "company_id": row["company_id"],
                "year": row["year"],
                "cashflow_insights": "; ".join(insights),
            }
        )

    # ==========================================
    # Save Output
    # ==========================================

    output_df = pd.DataFrame(generated_rows)

    output_df.to_excel(OUTPUT_FILE, index=False)

    print("\nGenerated Companies :", len(output_df))

    print("\nPreview:\n")
    print(output_df.head())

    print("\nSaved:")
    print(OUTPUT_FILE)

    # ==========================================
    # QA Validation
    # ==========================================

    conn = sqlite3.connect(DB_PATH)

    companies = pd.read_sql("SELECT id FROM companies", conn)

    conn.close()

    generated = set(output_df["company_id"])
    expected = set(companies["id"])

    missing = sorted(expected - generated)

    print("\nExpected Companies :", len(expected))
    print("Generated Companies :", len(generated))
    print("Missing Companies :", len(missing))

    if missing:

        print("\nMissing List:")
        print(missing)

        print("\nChecking Missing Company Data...\n")

        for company in missing:

            temp = df[df["company_id"] == company]

            print("=" * 50)
            print(company)
            print("=" * 50)

            if temp.empty:
                print("No records found in cashflow table.\n")
            else:
                print(temp)
                print()


if __name__ == "__main__":
    main()
