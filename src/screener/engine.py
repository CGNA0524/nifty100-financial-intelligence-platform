import sqlite3
import yaml
import pandas as pd

DB_PATH = "db/nifty100.db"


def load_financial_ratios():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql("""
    SELECT
        fr.company_id,
        fr.year,

        fr.return_on_equity_pct,
        fr.debt_to_equity,
        fr.interest_coverage,
        fr.asset_turnover,
        fr.free_cash_flow_cr,
        fr.revenue_cagr_5yr,
        fr.pat_cagr_5yr,
        fr.eps_cagr_5yr,
        fr.composite_quality_score,

        c.roce_percentage,

        mc.market_cap_crore,
        mc.pe_ratio,
        mc.pb_ratio,
        mc.dividend_yield_pct,

        pl.sales,
        pl.net_profit,
        pl.opm_percentage,
        s.broad_sector,
                     
        fr.dividend_payout_ratio_pct

    FROM financial_ratios fr

    LEFT JOIN companies c
    ON fr.company_id = c.id

    LEFT JOIN market_cap mc
    ON fr.company_id = mc.company_id
    AND substr(fr.year, -4) = CAST(mc.year AS TEXT)

    LEFT JOIN profitandloss pl
    ON fr.company_id = pl.company_id
    AND fr.year = pl.year
                     
                     LEFT JOIN sectors s
ON fr.company_id = s.company_id

    WHERE fr.year = (
        SELECT MAX(f2.year)
        FROM financial_ratios f2
        WHERE f2.company_id = fr.company_id
    )
    """, conn)

    conn.close()

    return df

def load_config():
    with open("config/screener_config.yaml", "r") as file:
        config = yaml.safe_load(file)
        return config

def get_revenue_cagr_3yr():

    conn = sqlite3.connect(DB_PATH)

    sales = pd.read_sql("""
        SELECT
            company_id,
            year,
            sales
        FROM profitandloss
    """, conn)

    conn.close()

    # Keep only rows having a 4-digit year
    sales["year_num"] = sales["year"].str.extract(r'(\d{4})')[0]
    sales = sales.dropna(subset=["year_num"])
    sales["year_num"] = sales["year_num"].astype(int)

    sales = sales.sort_values(
        ["company_id", "year_num"]
    )

    cagr = {}

    for company in sales["company_id"].unique():

        company_df = sales[
            sales["company_id"] == company
        ]

        if len(company_df) < 4:
            continue

        latest = pd.to_numeric(company_df.iloc[-1]["sales"], errors="coerce")
        old = pd.to_numeric(company_df.iloc[-4]["sales"], errors="coerce")

        if pd.isna(latest) or pd.isna(old) or old <= 0:
            continue

        value = (((latest / old) ** (1 / 3)) - 1) * 100

        cagr[company] = value

    return cagr
    
def get_debt_declining_companies():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql("""
        SELECT
            company_id,
            year,
            debt_to_equity
        FROM financial_ratios
    """, conn)

    conn.close()

    df["year_num"] = df["year"].str.extract(r'(\d{4})')[0]
    df = df.dropna(subset=["year_num"])
    df["year_num"] = df["year_num"].astype(int)

    df = df.sort_values(
        ["company_id", "year_num"]
    )

    declining = []

    for company in df["company_id"].unique():

        company_df = df[df["company_id"] == company]

        if len(company_df) < 2:
            continue

        latest = pd.to_numeric(
            company_df.iloc[-1]["debt_to_equity"],
            errors="coerce"
        )

        previous = pd.to_numeric(
            company_df.iloc[-2]["debt_to_equity"],
            errors="coerce"
        )

        if pd.isna(latest) or pd.isna(previous):
            continue

        if latest < previous:
            declining.append(company)

    return declining

def apply_screener(df, filters):

    result = df.copy()

    # Debt-free companies => Interest Coverage = Infinity
    result.loc[
        result["debt_to_equity"] == 0,
        "interest_coverage"
    ] = float("inf")

    for column, rule in filters.items():

        # Financial sector ke liye D/E filter skip
        if column == "debt_to_equity":

            financial_df = result[result["broad_sector"] == "Financials"]

            non_financial_df = result[result["broad_sector"] != "Financials"]

            if "max" in rule:
                non_financial_df = non_financial_df[
                    non_financial_df[column] <= rule["max"]
                ]

            result = pd.concat(
                [financial_df, non_financial_df],
                ignore_index=True
            )

            continue

        if "min" in rule:
            result = result[result[column] >= rule["min"]]

        if "max" in rule:
            result = result[result[column] <= rule["max"]]

    result = result.sort_values(
        by="composite_quality_score",
        ascending=False
    )

    return result

def main():

    df = load_financial_ratios()

    revenue_cagr = get_revenue_cagr_3yr()
    df["revenue_cagr_3yr"] = df["company_id"].map(revenue_cagr)

    debt_declining = get_debt_declining_companies()

    config = load_config()

    for screener_name, filters in config.items():

        result = apply_screener(df, filters)
        
        if screener_name == "turnaround_watch":
            result = result[
                result["company_id"].isin(debt_declining)
                ]

        print("=" * 50)
        print("Screener :", screener_name)
        print("Companies Found :", len(result))

        if result.empty:
            print("⚠ No companies matched this screener.")
        else:
            print(result[[
                "company_id",
                "return_on_equity_pct",
                "debt_to_equity",
                "composite_quality_score"
            ]].head())

        # Excel Export
        result.to_excel(
            f"output/{screener_name}.xlsx",
            index=False
        )

        print(f"✅ {screener_name}.xlsx generated")

    print("\n✅ All Screeners Generated Successfully!")
if __name__ == "__main__":
    main()