import pandas as pd
import sqlite3
import re
from pathlib import Path

RAW_PATH = Path("data/raw")
DB_PATH = "db/nifty100.db"
OUTPUT_PATH = Path("data/output")

validation_errors = []


##def load_excel(filename):
   ## return pd.read_excel(RAW_PATH / filename, header=1)
def load_table(table_name):

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        f"SELECT * FROM {table_name}",
        conn
    )

    conn.close()

    return df

# ==========================
# DQ-01 : PK Uniqueness
# ==========================
def check_pk_uniqueness(df, table_name):

    duplicates = df[df["id"].duplicated()]

    if not duplicates.empty:
        for _, row in duplicates.iterrows():

            validation_errors.append({
                "dq_rule": "DQ-01",
                "severity": "CRITICAL",
                "table": table_name,
                "record_id": row["id"],
                "issue": "Duplicate Primary Key"
            })


# ==========================
# DQ-02 : (company_id, year)
# Uniqueness
# ==========================
def check_company_year_uniqueness(df, table_name):

    duplicates = df[
        df.duplicated(
            subset=["company_id", "year"],
            keep=False
        )
    ]

    if not duplicates.empty:
        for _, row in duplicates.iterrows():

            validation_errors.append({
                "dq_rule": "DQ-02",
                "severity": "CRITICAL",
                "table": table_name,
                "record_id": row["company_id"],
                "issue": f"Duplicate company_id-year ({row['year']})"
            })


# ==========================
# DQ-03 : FK Integrity
# ==========================
def check_fk_integrity(df, companies_df, table_name):

    valid_company_ids = set(companies_df["id"])

    invalid_rows = df[
        ~df["company_id"].isin(valid_company_ids)
    ]

    if not invalid_rows.empty:
        for _, row in invalid_rows.iterrows():

            validation_errors.append({
                "dq_rule": "DQ-03",
                "severity": "CRITICAL",
                "table": table_name,
                "record_id": row["company_id"],
                "issue": "Foreign Key Not Found"
            })


# ==========================
# DQ-04 : Balance Sheet Balance
# Assets ≈ Liabilities (<1%)
# ==========================
def check_balance_sheet_balance(df):

    for _, row in df.iterrows():

        liabilities = row["total_liabilities"]
        assets = row["total_assets"]

        if pd.isna(liabilities) or pd.isna(assets):
            continue

        if liabilities == 0:
            continue

        diff_pct = abs(liabilities - assets) / liabilities

        if diff_pct > 0.01:

            validation_errors.append({
                "dq_rule": "DQ-04",
                "severity": "WARNING",
                "table": "balancesheet",
                "record_id": row["id"],
                "issue": "Assets and Liabilities mismatch > 1%"
            })

# ==========================
# DQ-05 : OPM Cross Check
# ==========================
def check_opm_cross_check(df):

    for _, row in df.iterrows():

        sales = row["sales"]

        if pd.isna(sales) or sales == 0:
            continue

        calculated_opm = (
            row["operating_profit"] / sales
        ) * 100

        if abs(calculated_opm - row["opm_percentage"]) > 1:

            validation_errors.append({
                "dq_rule": "DQ-05",
                "severity": "WARNING",
                "table": "profitandloss",
                "record_id": row["company_id"],
                "issue": "OPM mismatch"
            })


# ==========================
# DQ-06 : Positive Sales
# ==========================
def check_positive_sales(df):

    invalid = df[df["sales"] <= 0]

    for _, row in invalid.iterrows():

        validation_errors.append({
            "dq_rule": "DQ-06",
            "severity": "WARNING",
            "table": "profitandloss",
            "record_id": row["company_id"],
            "issue": "Sales <= 0"
        })


# ==========================
# DQ-07 : Year Format
# ==========================
def check_year_format(df, table_name):

    valid_patterns = [
        r"^\d{4}-\d{2}$",                 # 2024-03
        r"^[A-Za-z]{3}\s\d{4}$",          # Mar 2024
        r"^[A-Za-z]{3}\s\d{4}\s\d+[a-zA-Z]*$",  # Mar 2016 9m
        r"^TTM$"
    ]

    for _, row in df.iterrows():

        year = str(row["year"]).strip()

        is_valid = any(
            re.match(pattern, year)
            for pattern in valid_patterns
        )

        if not is_valid:

            validation_errors.append({
                "dq_rule": "DQ-07",
                "severity": "CRITICAL",
                "table": table_name,
                "record_id": row["company_id"],
                "issue": f"Invalid year format: {year}"
            })


# ==========================
# DQ-08 : Ticker Format
# ==========================
def check_ticker_format(df, table_name):

    for _, row in df.iterrows():

        ticker = str(row["company_id"]).strip()

        if len(ticker) < 2 or len(ticker) > 15:

            validation_errors.append({
                "dq_rule": "DQ-08",
                "severity": "CRITICAL",
                "table": table_name,
                "record_id": ticker,
                "issue": "Invalid ticker format"
            })


# ==========================
# DQ-09 : Net Cash Check
# ==========================
def check_net_cash(df):

    for _, row in df.iterrows():

        calculated = (
            row["operating_activity"]
            + row["investing_activity"]
            + row["financing_activity"]
        )

        if abs(calculated - row["net_cash_flow"]) > 10:

            validation_errors.append({
                "dq_rule": "DQ-09",
                "severity": "WARNING",
                "table": "cashflow",
                "record_id": row["company_id"],
                "issue": "Net cash mismatch"
            })


# ==========================
# DQ-10 : Fixed Assets
# ==========================
def check_fixed_assets(df):

    invalid = df[df["fixed_assets"] < 0]

    for _, row in invalid.iterrows():

        validation_errors.append({
            "dq_rule": "DQ-10",
            "severity": "WARNING",
            "table": "balancesheet",
            "record_id": row["company_id"],
            "issue": "Negative fixed assets"
        })


# ==========================
# DQ-11 : Tax Range
# ==========================
def check_tax_range(df):

    invalid = df[
        (df["tax_percentage"] < 0)
        |
        (df["tax_percentage"] > 60)
    ]

    for _, row in invalid.iterrows():

        validation_errors.append({
            "dq_rule": "DQ-11",
            "severity": "WARNING",
            "table": "profitandloss",
            "record_id": row["company_id"],
            "issue": "Invalid tax percentage"
        })


# ==========================
# DQ-12 : Dividend Cap
# ==========================
def check_dividend_cap(df):

    invalid = df[df["dividend_payout"] > 200]

    for _, row in invalid.iterrows():

        validation_errors.append({
            "dq_rule": "DQ-12",
            "severity": "WARNING",
            "table": "profitandloss",
            "record_id": row["company_id"],
            "issue": "Dividend payout > 200%"
        })


# ==========================
# DQ-13 : URL Validity
# ==========================
def check_urls(companies, documents):

    url_cols = [
        "website",
        "nse_profile",
        "bse_profile",
        "chart_link"
    ]

    for col in url_cols:

        for _, row in companies.iterrows():

            value = str(row[col])

            if not value.startswith("http"):

                validation_errors.append({
                    "dq_rule": "DQ-13",
                    "severity": "WARNING",
                    "table": "companies",
                    "record_id": row["id"],
                    "issue": f"Invalid {col}"
                })

    for _, row in documents.iterrows():

        value = str(row["Annual_Report"])

        if not value.startswith("http"):

            validation_errors.append({
                "dq_rule": "DQ-13",
                "severity": "WARNING",
                "table": "documents",
                "record_id": row["company_id"],
                "issue": "Invalid Annual Report URL"
            })


# ==========================
# DQ-14 : EPS Sign
# ==========================
def check_eps_sign(df):

    invalid = df[
        (df["net_profit"] > 0)
        &
        (df["eps"] <= 0)
    ]

    for _, row in invalid.iterrows():

        validation_errors.append({
            "dq_rule": "DQ-14",
            "severity": "WARNING",
            "table": "profitandloss",
            "record_id": row["company_id"],
            "issue": "EPS sign inconsistent"
        })


# ==========================
# DQ-15 : BSE Balance
# ==========================
def check_bse_balance(df):

    for _, row in df.iterrows():

        if row["total_assets"] != row["total_liabilities"]:

            validation_errors.append({
                "dq_rule": "DQ-15",
                "severity": "INFO",
                "table": "balancesheet",
                "record_id": row["company_id"],
                "issue": "Assets != Liabilities"
            })


# ==========================
# DQ-16 : Coverage Check
# ==========================
def check_coverage(df):

    counts = df.groupby("company_id").size()

    for company, count in counts.items():

        if count < 5:

            validation_errors.append({
                "dq_rule": "DQ-16",
                "severity": "WARNING",
                "table": "profitandloss",
                "record_id": company,
                "issue": "Less than 5 years coverage"
            })



# ==========================
# MAIN
# ==========================
if __name__ == "__main__":

    print("\nRunning Data Quality Checks...")
    print("=" * 60)

    companies = load_table("companies")
    profitandloss = load_table("profitandloss")
    balancesheet = load_table("balancesheet")
    cashflow = load_table("cashflow")
    documents = load_table("documents")
    financial_ratios = load_table("financial_ratios")

    # -----------------------
    # DQ-01
    # -----------------------
    check_pk_uniqueness(companies, "companies")
    check_pk_uniqueness(profitandloss, "profitandloss")
    check_pk_uniqueness(balancesheet, "balancesheet")
    check_pk_uniqueness(cashflow, "cashflow")
    check_pk_uniqueness(financial_ratios, "financial_ratios")

    # -----------------------
    # DQ-02
    # -----------------------
    check_company_year_uniqueness(
        profitandloss,
        "profitandloss"
    )

    check_company_year_uniqueness(
        balancesheet,
        "balancesheet"
    )

    check_company_year_uniqueness(
        cashflow,
        "cashflow"
    )

    check_company_year_uniqueness(
        financial_ratios,
        "financial_ratios"
    )   

    # -----------------------
    # DQ-03
    # -----------------------
    check_fk_integrity(
        profitandloss,
        companies,
        "profitandloss"
    )

    check_fk_integrity(
        balancesheet,
        companies,
        "balancesheet"
    )

    check_fk_integrity(
        cashflow,
        companies,
        "cashflow"
    )

    check_fk_integrity(
        financial_ratios,
        companies,
        "financial_ratios"
    )

    # -----------------------
    # DQ-04
    # -----------------------
    check_balance_sheet_balance(
        balancesheet
    )

    # -----------------------
    # DQ-05 to DQ-16
    # -----------------------
    check_opm_cross_check(profitandloss)
    check_positive_sales(profitandloss)

    check_year_format(
        profitandloss,
        "profitandloss"
    )

    check_year_format(
        balancesheet,
        "balancesheet"
    )

    check_year_format(
        cashflow,
        "cashflow"
    )

    check_ticker_format(
        profitandloss,
        "profitandloss"
    )

    check_ticker_format(
        balancesheet,
        "balancesheet"
    )

    check_ticker_format(
        cashflow,
        "cashflow"
    )

    check_net_cash(cashflow)

    check_fixed_assets(
        balancesheet
    )

    check_tax_range(
        profitandloss
    )

    check_dividend_cap(
        profitandloss
    )

    check_urls(
        companies,
        documents
    )

    check_eps_sign(
        profitandloss
    )

    check_bse_balance(
        balancesheet
    )

    check_coverage(
        profitandloss
    )

    # -----------------------
    # Save Report
    # -----------------------
    OUTPUT_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    report = pd.DataFrame(
        validation_errors
    )

    report.to_csv(
        OUTPUT_PATH /
        "validation_failures.csv",
        index=False
    )

    print("\nValidation completed.")
    print(
        f"Total Issues Found: {len(report)}"
    )

    print("\nReport saved to:")
    print(
        "data/output/validation_failures.csv"
    )   