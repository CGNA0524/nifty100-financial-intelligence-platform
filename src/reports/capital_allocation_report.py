from pathlib import Path
import pandas as pd

# =====================================================
# Project Paths
# =====================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = PROJECT_ROOT / "output" / "capital_allocation.csv"

OUTPUT_DIR = PROJECT_ROOT / "output"

DISTRIBUTION_FILE = OUTPUT_DIR / "capital_allocation_distribution.xlsx"


# =====================================================
# Load Data
# =====================================================

def load_data():

    return pd.read_csv(INPUT_FILE)


# =====================================================
# Main
# =====================================================

def main():

    print("=" * 60)
    print("Sprint 5 - Day 32")
    print("Capital Allocation Distribution")
    print("=" * 60)

    df = load_data()

    print("\nRows Loaded :", len(df))

    # Extract numeric year (e.g. "Mar 2024" -> 2024)
    df["year_num"] = (
        df["year"]
        .astype(str)
        .str.extract(r"(\d{4})")
        .astype(int)
    )

    latest_year = df["year_num"].max()

    print("Latest Calendar Year :", latest_year)

    latest_df = df[df["year_num"] == latest_year].copy()

    print("Companies In Latest Year :", latest_df["company_id"].nunique())

    distribution = (
        latest_df.groupby("capital_allocation_pattern")
        .agg(
            companies=("company_id", "nunique")
        )
        .reset_index()
        .sort_values(
            by="companies",
            ascending=False
        )
    )

    distribution.to_excel(
        DISTRIBUTION_FILE,
        index=False
    )

    print("\nDistribution Summary\n")
    print(distribution)

    print("\nSaved:")
    print(DISTRIBUTION_FILE)


if __name__ == "__main__":
    main()