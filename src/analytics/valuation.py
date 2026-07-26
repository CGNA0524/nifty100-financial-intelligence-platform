"""
Sprint-4

Valuation Module
"""

import sqlite3
import pandas as pd
from pathlib import Path


# ==========================================
# Database Path
# ==========================================

BASE_DIR = Path(__file__).resolve().parents[2]

DB_PATH = BASE_DIR / "db" / "nifty100.db"

OUTPUT_DIR = BASE_DIR / "output"


# ==========================================
# Database Connection
# ==========================================

def get_connection():

    """
    Returns SQLite database connection.
    """

    return sqlite3.connect(DB_PATH)

# ==========================================
# Load Market Cap Data
# ==========================================

def load_market_cap():

    """
    Loads market_cap table from SQLite database.
    """

    conn = get_connection()

    query = """
    SELECT *

    FROM market_cap

    ORDER BY
        company_id,
        year
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df

# ==========================================
# Load Financial Ratios
# ==========================================

def load_financial_ratios():

    """
    Loads financial_ratios table from SQLite database.
    """

    conn = get_connection()

    query = """
    SELECT *

    FROM financial_ratios

    ORDER BY
        company_id,
        year
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df

# ==========================================
# Load Sectors Data
# ==========================================

def load_sectors():

    """
    Loads sectors table from SQLite database.
    """

    conn = get_connection()

    query = """
    SELECT *

    FROM sectors

    ORDER BY
        company_id
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df

# ==========================================
# Load Companies Data
# ==========================================

def load_companies():

    """
    Loads companies table from SQLite database.
    """

    conn = get_connection()

    query = """
    SELECT *

    FROM companies

    ORDER BY
        company_name
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df

# ==========================================
# Load Latest Market Cap Data
# ==========================================

def get_latest_market_cap():

    """
    Returns only the latest available year
    for every company from market_cap table.
    """

    market_cap = load_market_cap()

    latest_market_cap = (
        market_cap
        .sort_values("year")
        .groupby("company_id")
        .tail(1)
        .reset_index(drop=True)
    )

    return latest_market_cap

# ==========================================
# Load Latest Financial Ratios
# ==========================================

def get_latest_financial_ratios():

    """
    Returns only the latest available year
    for every company from financial_ratios table.
    """

    financial_ratios = load_financial_ratios()

    latest_ratios = (
        financial_ratios
        .sort_values("year")
        .groupby("company_id")
        .tail(1)
        .reset_index(drop=True)
    )

    return latest_ratios

# ==========================================
# Calculate FCF Yield
# ==========================================

def calculate_fcf_yield():

    """
    Calculates Free Cash Flow Yield.

    Formula:

    (FCF / Market Cap) * 100
    """

    market_cap = get_latest_market_cap()

    financial_ratios = get_latest_financial_ratios()

    merged_df = pd.merge(
        financial_ratios,
        market_cap,
        on="company_id",
        how="inner"
    )

    merged_df["fcf_yield_pct"] = (
        merged_df["free_cash_flow_cr"]
        /
        merged_df["market_cap_crore"]
    ) * 100

    return merged_df

# ==========================================
# Calculate Sector Median PE Ratio
# ==========================================

def calculate_sector_median_pe():

    """
    Calculates sector wise median PE ratio.
    """

    market_cap = get_latest_market_cap()

    sectors = load_sectors()

    merged_df = pd.merge(
        market_cap,
        sectors,
        on="company_id",
        how="left"
    )

    sector_median_pe = (

        merged_df
        .groupby("broad_sector")["pe_ratio"]
        .median()
        .reset_index()

    )

    sector_median_pe.rename(

        columns={
            "pe_ratio": "sector_median_pe"
        },

        inplace=True

    )

    return sector_median_pe

# ==========================================
# Apply Valuation Flags
# ==========================================

def apply_valuation_flags():

    """
    Applies Discount, Fair and
    Caution valuation flags.
    """

    valuation_df = calculate_fcf_yield()

    sector_pe = calculate_sector_median_pe()

    sectors = load_sectors()

    # Add sector information
    valuation_df = pd.merge(
        valuation_df,
        sectors,
        on="company_id",
        how="left"
    )

    # Add sector median PE
    valuation_df = pd.merge(
        valuation_df,
        sector_pe,
        on="broad_sector",
        how="left"
    )


    def get_flag(row):

        pe_ratio = row["pe_ratio"]

        sector_median = row["sector_median_pe"]

        if pd.isna(pe_ratio) or pd.isna(sector_median):
            return "N/A"

        if pe_ratio > (sector_median * 1.5):
            return "Caution"

        elif pe_ratio < (sector_median * 0.7):
            return "Discount"

        return "Fair"


    valuation_df["flag"] = (
        valuation_df
        .apply(get_flag, axis=1)
    )


    return valuation_df

# ==========================================
# Prepare Final Valuation Data
# ==========================================

def prepare_valuation_summary():

    """
    Prepares the final valuation dataframe
    required for Sprint-4 deliverables.
    """

    valuation_df = apply_valuation_flags()

    # Get company names only
    company_names = (
        load_companies()
        .set_index("id")["company_name"]
    )

    # Map company names
    valuation_df["company_name"] = (
        valuation_df["company_id"]
        .map(company_names)
    )

    # PE vs Sector Median %
    valuation_df["pe_vs_sector_median_pct"] = (
        (
            valuation_df["pe_ratio"]
            /
            valuation_df["sector_median_pe"]
        ) * 100
    )

    # Handle missing and infinite values
    valuation_df["pe_vs_sector_median_pct"] = (
        valuation_df["pe_vs_sector_median_pct"]
        .replace([float("inf"), float("-inf")], pd.NA)
        .round(2)
    )

    # Round important valuation columns
    valuation_df["fcf_yield_pct"] = (
        valuation_df["fcf_yield_pct"]
        .round(2)
    )

    valuation_df["sector_median_pe"] = (
        valuation_df["sector_median_pe"]
        .round(2)
    )

    valuation_df["pe_ratio"] = (
        valuation_df["pe_ratio"]
        .round(2)
    )

    valuation_df["pb_ratio"] = (
        valuation_df["pb_ratio"]
        .round(2)
    )

    valuation_df["ev_ebitda"] = (
        valuation_df["ev_ebitda"]
        .round(2)
    )

    # Select Sprint-4 required columns
    valuation_df = valuation_df[
        [
            "company_id",
            "company_name",
            "broad_sector",
            "pe_ratio",
            "pb_ratio",
            "ev_ebitda",
            "fcf_yield_pct",
            "sector_median_pe",
            "pe_vs_sector_median_pct",
            "flag"
        ]
    ]

    return valuation_df

# ==========================================
# Generate valuation_summary.xlsx
# ==========================================

def save_valuation_summary():

    """
    Saves valuation summary Excel file.
    """

    valuation_df = prepare_valuation_summary()

    # Create output folder if required
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = (
        OUTPUT_DIR
        /
        "valuation_summary.xlsx"
    )

    valuation_df.to_excel(
        output_path,
        index=False
    )

    print(
        "\nvaluation_summary.xlsx generated successfully."
    )

    return valuation_df


# ==========================================
# Generate valuation_flags.csv
# ==========================================

def save_valuation_flags():

    """
    Saves only Discount and Caution
    companies in CSV format.
    """

    valuation_df = prepare_valuation_summary()

    flags_df = valuation_df[

        valuation_df["flag"].isin(
            [
                "Discount",
                "Caution"
            ]
        )

    ]

    # Create output folder if required
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = (
        OUTPUT_DIR
        /
        "valuation_flags.csv"
    )

    flags_df.to_csv(
        output_path,
        index=False
    )

    print(
        "\nvaluation_flags.csv generated successfully."
    )

    return flags_df


# ==========================================
# Main Function
# ==========================================

def main():

    """
    Generates all Sprint-4
    valuation deliverables.
    """

    print("\nGenerating valuation outputs...\n")

    save_valuation_summary()

    save_valuation_flags()

    print(
        "\nSprint-4 Valuation Module Completed Successfully."
    )


if __name__ == "__main__":

    main()