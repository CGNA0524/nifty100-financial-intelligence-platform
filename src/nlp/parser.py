import re
import sqlite3
from pathlib import Path

import pandas as pd

# ======================================================
# Project Paths
# ======================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"
DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"

ANALYSIS_FILE = DATA_DIR / "raw" / "analysis.xlsx"

PARSED_OUTPUT = OUTPUT_DIR / "analysis_parsed.csv"
FAILURE_OUTPUT = OUTPUT_DIR / "parse_failures.csv"



def load_ratio_engine_data():
    """
    Load CAGR values from the financial_ratios table.
    """

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT
        company_id,
        revenue_cagr_5yr,
        pat_cagr_5yr,
        eps_cagr_5yr
    FROM financial_ratios
    """

    ratio_df = pd.read_sql(query, conn)

    conn.close()

    return ratio_df


def map_metric_to_ratio_column(metric_type):
    """
    Map parsed metric names to Ratio Engine columns.
    """

    mapping = {
        "compounded_sales_growth": "revenue_cagr_5yr",
        "compounded_profit_growth": "pat_cagr_5yr",
        "stock_price_cagr": None,          # No matching DB column
        "roe": None                        # Parsed ROE is different from CAGR
    }

    return mapping.get(metric_type)


# ======================================================
# Main
# ======================================================

def main():

    print("=" * 60)
    print("Sprint 5 - Day 29")
    print("Analysis Text Parser")
    print("=" * 60)

    print(f"Reading : {ANALYSIS_FILE}")

    df = pd.read_excel(
        ANALYSIS_FILE,
        header=1
    )

    print("\nColumns:\n")
    print(df.columns.tolist())

    print("\nShape:")
    print(df.shape)

    print("\nFirst 5 Rows:\n")
    print(df.head())

    # ======================================================
    # Regex Pattern
    # ======================================================

    pattern = re.compile(
        r"(\d+)\s*Years?:?\s*(-?[\d.]+)%"
    )

    parsed_rows = []
    failed_rows = []

    target_columns = [
        "compounded_sales_growth",
        "compounded_profit_growth",
        "stock_price_cagr",
        "roe"
    ]

    # ======================================================
    # Parse
    # ======================================================

    for _, row in df.iterrows():

        company_id = row["company_id"]

        for metric in target_columns:

            text = str(row[metric]).strip()

            match = pattern.search(text)

            if match:

                parsed_rows.append({

                    "company_id": company_id,
                    "metric_type": metric,
                    "period_years": int(match.group(1)),
                    "value_pct": float(match.group(2))

                })

            else:

                failed_rows.append({

                    "company_id": company_id,
                    "metric_type": metric,
                    "raw_text": text

                })

    # ======================================================
    # Save Outputs
    # ======================================================

    parsed_df = pd.DataFrame(parsed_rows)
    failed_df = pd.DataFrame(failed_rows)

    parsed_df.to_csv(
        PARSED_OUTPUT,
        index=False
    )

    failed_df.to_csv(
        FAILURE_OUTPUT,
        index=False
    )

    print("\nParsed Records :", len(parsed_df))
    print("Failed Records :", len(failed_df))

    print("\nSaved :")
    print(PARSED_OUTPUT)
    print(FAILURE_OUTPUT)

    # ==========================================
    # Load Ratio Engine Data
    # ==========================================

    ratio_df = load_ratio_engine_data()

    print("\nRatio Engine Preview:\n")
    print(ratio_df.head())

    print("\nRatio Engine Shape:", ratio_df.shape)

    # ==========================================
    # Remove rows where all CAGR values are missing
    # ==========================================

    ratio_df = ratio_df.dropna(
        subset=[
            "revenue_cagr_5yr",
            "pat_cagr_5yr",
            "eps_cagr_5yr"
        ],
        how="all"
    )

    print("\nRatio Engine After Cleaning:")
    print(ratio_df.head())

    print("\nClean Shape:", ratio_df.shape)

    # ==========================================
    # Prepare parsed data for validation
    # ==========================================

    validation_df = parsed_df.copy()

    validation_df["ratio_column"] = validation_df["metric_type"].apply(
        map_metric_to_ratio_column
    )

    # Only keep metrics that have a matching Ratio Engine column
    validation_df = validation_df[
        validation_df["ratio_column"].notna()
    ]

    print("\nValidation Preview:\n")
    print(validation_df.head())

    print("\nValidation Shape:", validation_df.shape)

    # ==========================================
    # Compare Parsed Values vs Ratio Engine
    # ==========================================

    comparison_rows = []

    for _, row in validation_df.iterrows():

        company = row["company_id"]
        metric = row["metric_type"]
        parsed_value = row["value_pct"]
        ratio_column = row["ratio_column"]

        company_data = ratio_df[
            ratio_df["company_id"] == company
        ]

        if company_data.empty:
            continue

        db_value = company_data[ratio_column].dropna()

        if db_value.empty:
            continue

        calculated_value = db_value.iloc[-1]

        difference = abs(parsed_value - calculated_value)

        comparison_rows.append({
            "company_id": company,
            "metric_type": metric,
            "parsed_value": parsed_value,
            "calculated_value": calculated_value,
            "difference_pct": round(difference, 2),
            "status": "REVIEW" if difference > 5 else "PASS"
        })

    comparison_df = pd.DataFrame(comparison_rows)

    comparison_output = OUTPUT_DIR / "cagr_validation.csv"

    comparison_df.to_csv(
        comparison_output,
        index=False
    )

    print("\nValidation Completed")

    print("\nValidation Preview:\n")
    print(comparison_df.head())

    print("\nValidation Shape:", comparison_df.shape)

    print("\nSaved:")
    print(comparison_output)

    print("\nSummary:")
    print(comparison_df["status"].value_counts())

# ======================================================
# Run
# ======================================================

if __name__ == "__main__":
    main()