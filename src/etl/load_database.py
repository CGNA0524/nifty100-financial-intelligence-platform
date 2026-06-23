import sqlite3
from pathlib import Path
import pandas as pd
from normaliser import (
    normalize_ticker,
    normalize_year
)
DB_PATH = Path("db/nifty100.db")
RAW_PATH = Path("data/raw")
OUTPUT_PATH = Path("data/output")

load_audit = []


def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def log_load(table_name, rows_loaded):
    load_audit.append({
        "table_name": table_name,
        "rows_loaded": rows_loaded
    })


def get_valid_company_ids():
    companies = pd.read_excel(
        RAW_PATH / "companies.xlsx",
        header=1
    )

    return set(
        companies["id"].astype(str)
    )


def filter_valid_company_ids(df):
    valid_ids = get_valid_company_ids()

    return df[
        df["company_id"].astype(str).isin(valid_ids)
    ]


def load_companies(conn):

    print("\nLoading companies...")

    df = pd.read_excel(
        RAW_PATH / "companies.xlsx",
        header=1
    )

    df.to_sql(
        "companies",
        conn,
        if_exists="append",
        index=False
    )

    log_load("companies", len(df))

    print(f"Loaded {len(df)} rows into companies")


def load_profitandloss(conn):

    print("\nLoading profitandloss...")

    df = pd.read_excel(
        RAW_PATH / "profitandloss.xlsx",
        header=1
    )

    df = filter_valid_company_ids(df)
    df = df.drop_duplicates(
    subset=["company_id", "year"],
    keep="first"
    )
    df["company_id"] = df["company_id"].apply(normalize_ticker)
    if "year" in df.columns:
        df["year"] = df["year"].apply(normalize_year)

    df.to_sql(
        "profitandloss",
        conn,
        if_exists="append",
        index=False
    )

    log_load("profitandloss", len(df))

    print(f"Loaded {len(df)} rows into profitandloss")


def load_balancesheet(conn):

    print("\nLoading balancesheet...")

    df = pd.read_excel(
        RAW_PATH / "balancesheet.xlsx",
        header=1
    )

    df = filter_valid_company_ids(df)
    df = df.drop_duplicates(
    subset=["company_id", "year"],
    keep="first"
    )
    df["company_id"] = df["company_id"].apply(normalize_ticker)
    if "year" in df.columns:
        df["year"] = df["year"].apply(normalize_year)

    df.to_sql(
        "balancesheet",
        conn,
        if_exists="append",
        index=False
    )

    log_load("balancesheet", len(df))

    print(f"Loaded {len(df)} rows into balancesheet")


def load_cashflow(conn):

    print("\nLoading cashflow...")

    df = pd.read_excel(
        RAW_PATH / "cashflow.xlsx",
        header=1
    )

    df = filter_valid_company_ids(df)
    df = df.drop_duplicates(
    subset=["company_id", "year"],
    keep="first"
    )
    df["company_id"] = df["company_id"].apply(normalize_ticker)
    if "year" in df.columns:
        df["year"] = df["year"].apply(normalize_year)

    df.to_sql(
        "cashflow",
        conn,
        if_exists="append",
        index=False
    )

    log_load("cashflow", len(df))

    print(f"Loaded {len(df)} rows into cashflow")


def load_analysis(conn):

    print("\nLoading analysis...")

    df = pd.read_excel(
        RAW_PATH / "analysis.xlsx",
        header=1
    )

    df = filter_valid_company_ids(df)
    df["company_id"] = df["company_id"].apply(normalize_ticker)

    df.to_sql(
        "analysis",
        conn,
        if_exists="append",
        index=False
    )

    log_load("analysis", len(df))

    print(f"Loaded {len(df)} rows into analysis")


def load_documents(conn):

    print("\nLoading documents...")

    df = pd.read_excel(
        RAW_PATH / "documents.xlsx",
        header=1
    )

    df = filter_valid_company_ids(df)
    df["company_id"] = df["company_id"].apply(normalize_ticker)
    df.to_sql(
        "documents",
        conn,
        if_exists="append",
        index=False
    )

    log_load("documents", len(df))

    print(f"Loaded {len(df)} rows into documents")


def load_prosandcons(conn):

    print("\nLoading prosandcons...")

    df = pd.read_excel(
        RAW_PATH / "prosandcons.xlsx",
        header=1
    )

    df = filter_valid_company_ids(df)
    df["company_id"] = df["company_id"].apply(normalize_ticker)

    df.to_sql(
        "prosandcons",
        conn,
        if_exists="append",
        index=False
    )

    log_load("prosandcons", len(df))

    print(f"Loaded {len(df)} rows into prosandcons")

def load_sectors(conn):

    print("\nLoading sectors...")

    df = pd.read_excel(
        RAW_PATH / "sectors.xlsx",
        header=0
    )

    df.to_sql(
        "sectors",
        conn,
        if_exists="append",
        index=False
    )

    log_load("sectors", len(df))

    print(f"Loaded {len(df)} rows into sectors")


def load_stock_prices(conn):

    print("\nLoading stock_prices...")

    df = pd.read_excel(
        RAW_PATH / "stock_prices.xlsx",
        header=0
    )

    df.to_sql(
        "stock_prices",
        conn,
        if_exists="append",
        index=False
    )

    log_load("stock_prices", len(df))

    print(f"Loaded {len(df)} rows into stock_prices")


def load_market_cap(conn):

    print("\nLoading market_cap...")

    df = pd.read_excel(
        RAW_PATH / "market_cap.xlsx",
        header=0
    )

    df.to_sql(
        "market_cap",
        conn,
        if_exists="append",
        index=False
    )

    log_load("market_cap", len(df))

    print(f"Loaded {len(df)} rows into market_cap")


def load_financial_ratios(conn):

    print("\nLoading financial_ratios...")

    df = pd.read_excel(
        RAW_PATH / "financial_ratios.xlsx",
        header=0
    )

    df = filter_valid_company_ids(df)
    df = df.drop_duplicates(
    subset=["company_id", "year"],
    keep="first"
    )
    df["company_id"] = df["company_id"].apply(normalize_ticker)
    if "year" in df.columns:
        df["year"] = df["year"].apply(normalize_year)
    df.to_sql(
        "financial_ratios",
        conn,
        if_exists="append",
        index=False
    )

    log_load("financial_ratios", len(df))

    print(f"Loaded {len(df)} rows into financial_ratios")


def load_peer_groups(conn):

    print("\nLoading peer_groups...")

    df = pd.read_excel(
        RAW_PATH / "peer_groups.xlsx",
        header=0
    )

    df = filter_valid_company_ids(df)
    df["company_id"] = df["company_id"].apply(normalize_ticker)
    df.to_sql(
        "peer_groups",
        conn,
        if_exists="append",
        index=False
    )

    log_load("peer_groups", len(df))

    print(f"Loaded {len(df)} rows into peer_groups")

def save_audit():

    OUTPUT_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    audit_df = pd.DataFrame(load_audit)

    audit_df.to_csv(
        OUTPUT_PATH / "load_audit.csv",
        index=False
    )

    print("\nload_audit.csv created")


if __name__ == "__main__":

    conn = connect_db()

    print("Database Connected")

    load_companies(conn)
    load_profitandloss(conn)
    load_balancesheet(conn)
    load_cashflow(conn)
    load_analysis(conn)
    load_documents(conn)
    load_prosandcons(conn)
    load_sectors(conn)
    load_stock_prices(conn)
    load_market_cap(conn)
    load_financial_ratios(conn)
    load_peer_groups(conn)
    save_audit()
    conn.close()

    print("\nData Load Complete")