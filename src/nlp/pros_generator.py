from pathlib import Path
import sqlite3
import pandas as pd

# ======================================================
# Project Paths
# ======================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"
OUTPUT_DIR = PROJECT_ROOT / "output"

OUTPUT_FILE = OUTPUT_DIR / "pros_cons_generated.csv"


def load_financial_ratios():
    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT
        company_id,
        year,
        return_on_equity_pct,
        debt_to_equity,
        interest_coverage,
        dividend_payout_ratio_pct,
        revenue_cagr_5yr,
        pat_cagr_5yr
    FROM financial_ratios
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df


def main():

    print("=" * 60)
    print("Sprint 5 - Day 30")
    print("Pros & Cons Generator")
    print("=" * 60)

    ratios = load_financial_ratios()

    # Keep latest record for each company
    ratios = (
        ratios
        .sort_values("year")
        .groupby("company_id", as_index=False)
        .last()
    )

    generated_rows = []

    for _, row in ratios.iterrows():

        pros = []
        cons = []

        # ==========================
        # Pros Rules
        # ==========================

        if pd.notna(row["return_on_equity_pct"]) and row["return_on_equity_pct"] >= 20:
            pros.append("High Return on Equity")

        if pd.notna(row["debt_to_equity"]) and row["debt_to_equity"] <= 0.5:
            pros.append("Low Debt")

        if pd.notna(row["interest_coverage"]) and row["interest_coverage"] >= 5:
            pros.append("Strong Interest Coverage")

        if pd.notna(row["revenue_cagr_5yr"]) and row["revenue_cagr_5yr"] >= 15:
            pros.append("Strong Revenue Growth")

        if pd.notna(row["pat_cagr_5yr"]) and row["pat_cagr_5yr"] >= 15:
            pros.append("Strong Profit Growth")

        # ==========================
        # Cons Rules
        # ==========================

        if pd.notna(row["return_on_equity_pct"]) and row["return_on_equity_pct"] < 10:
            cons.append("Low Return on Equity")

        if pd.notna(row["debt_to_equity"]) and row["debt_to_equity"] > 1:
            cons.append("High Debt")

        if pd.notna(row["interest_coverage"]) and row["interest_coverage"] < 2:
            cons.append("Weak Interest Coverage")

        if pd.notna(row["dividend_payout_ratio_pct"]) and row["dividend_payout_ratio_pct"] < 15:
            cons.append("Low Dividend Payout")

        generated_rows.append({
            "company_id": row["company_id"],
            "pros": "; ".join(pros) if pros else "No significant strengths identified",
            "cons": "; ".join(cons) if cons else "No significant concerns identified"
            }
        )

    output_df = pd.DataFrame(generated_rows)

    output_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nGenerated Companies :", len(output_df))

    print("\nPreview:\n")
    print(output_df.head())

    print("\nSaved:")
    print(OUTPUT_FILE)

    # ==========================================
    # Check Missing Companies
    # ==========================================

    conn = sqlite3.connect(DB_PATH)

    companies = pd.read_sql(
    "SELECT id FROM companies",
    conn
)

    conn.close()

    generated = set(output_df["company_id"])

    expected = set(companies["id"])

    missing = sorted(expected - generated)

    print("\nExpected Companies :", len(expected))
    print("Generated Companies:", len(generated))
    print("Missing Companies :", len(missing))

    if missing:
        print("\nMissing List:")
        print(missing)


    # ==========================================
    # Check Missing Company Data
    # ==========================================

    print("\nChecking Missing Companies...\n")

    for company in missing:

        temp = ratios[ratios["company_id"] == company]

        print("=" * 50)
        print(company)
        print("=" * 50)

        if temp.empty:
            print("No records found in financial_ratios table.\n")
        else:
            print(temp)
            print()

if __name__ == "__main__":
    main()