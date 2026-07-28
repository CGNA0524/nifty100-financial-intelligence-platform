from pathlib import Path

import pandas as pd

# =====================================================
# Project Paths
# =====================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = PROJECT_ROOT / "output" / "capital_allocation.csv"

OUTPUT_DIR = PROJECT_ROOT / "output"

OUTPUT_FILE = OUTPUT_DIR / "pattern_changes.csv"


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
    print("Capital Allocation Pattern Changes")
    print("=" * 60)

    df = load_data()

    print("\nRows Loaded :", len(df))

    # Extract calendar year
    df["year_num"] = df["year"].astype(str).str.extract(r"(\d{4})").astype(int)

    df = df.sort_values(by=["company_id", "year_num"])

    records = []

    for company_id, group in df.groupby("company_id"):

        group = group.sort_values("year_num")

        if len(group) < 2:
            continue

        previous = group.iloc[-2]
        latest = group.iloc[-1]

        if (
            previous["capital_allocation_pattern"]
            != latest["capital_allocation_pattern"]
        ):

            records.append(
                {
                    "company_id": company_id,
                    "previous_year": previous["year"],
                    "latest_year": latest["year"],
                    "previous_pattern": previous["capital_allocation_pattern"],
                    "latest_pattern": latest["capital_allocation_pattern"],
                }
            )

    changes = pd.DataFrame(records)

    changes.to_csv(OUTPUT_FILE, index=False)

    print("\nCompanies With Pattern Changes :", len(changes))

    print("\nPreview:\n")
    print(changes.head())

    print("\nSaved:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
