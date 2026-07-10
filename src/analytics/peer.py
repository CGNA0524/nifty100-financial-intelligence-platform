import sqlite3
import pandas as pd

DB_PATH = "db/nifty100.db"


def load_peer_data():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql("""

    SELECT

        pg.peer_group_name,
        pg.company_id,
        pg.is_benchmark,

        fr.year,
        fr.return_on_equity_pct,
        c.roce_percentage,
        fr.net_profit_margin_pct,
        fr.debt_to_equity,
        fr.free_cash_flow_cr,
        fr.pat_cagr_5yr,
        fr.revenue_cagr_5yr,
        fr.eps_cagr_5yr,
        fr.interest_coverage,
        fr.asset_turnover,
        fr.composite_quality_score

    FROM peer_groups pg

    LEFT JOIN financial_ratios fr
    ON pg.company_id = fr.company_id

    LEFT JOIN companies c
    ON pg.company_id = c.id

    WHERE fr.year = (

        SELECT MAX(f2.year)

        FROM financial_ratios f2

        WHERE f2.company_id = fr.company_id

    )

    """, conn)

    conn.close()

    return df


def percentile(series):

    return (
        series
        .rank(
            pct=True,
            na_option="keep"
        ) * 100
    )


def calculate_peer_percentiles(df):

    all_groups = []

    metrics = [

        "return_on_equity_pct",
        "roce_percentage",
        "net_profit_margin_pct",
        "debt_to_equity",
        "free_cash_flow_cr",
        "pat_cagr_5yr",
        "revenue_cagr_5yr",
        "eps_cagr_5yr",
        "interest_coverage",
        "asset_turnover"

    ]

    for group in df["peer_group_name"].unique():

        group_df = df[
            df["peer_group_name"] == group
        ].copy()

        for metric in metrics:

            if metric == "debt_to_equity":

                group_df["debt_to_equity_percentile"] = (
                    100 - percentile(group_df[metric])
                )

            else:

                group_df[f"{metric}_percentile"] = percentile(
                    group_df[metric]
                )

        all_groups.append(group_df)

    result = pd.concat(
        all_groups,
        ignore_index=True
    )

    return result
def save_peer_percentiles(df):

    conn = sqlite3.connect(DB_PATH)

    export_rows = []

    metrics = [

        "return_on_equity_pct",
        "roce_percentage",
        "net_profit_margin_pct",
        "debt_to_equity",
        "free_cash_flow_cr",
        "pat_cagr_5yr",
        "revenue_cagr_5yr",
        "eps_cagr_5yr",
        "interest_coverage",
        "asset_turnover"

    ]

    for _, row in df.iterrows():

        for metric in metrics:

            percentile_column = (
                "debt_to_equity_percentile"
                if metric == "debt_to_equity"
                else f"{metric}_percentile"
            )

            export_rows.append({

                "company_id": row["company_id"],
                "peer_group_name": row["peer_group_name"],
                "metric": metric,
                "value": row[metric],
                "percentile_rank": row[percentile_column],
                "year": row["year"]

            })

    export_df = pd.DataFrame(export_rows)

    export_df.to_sql(
        "peer_percentiles",
        conn,
        if_exists="replace",
        index=False
    )

    conn.close()

    print("✅ peer_percentiles table created successfully")

    return export_df


def export_peer_excel(df):

    output = "output/peer_comparison.xlsx"

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        for group in df["peer_group_name"].unique():

            sheet = df[
                df["peer_group_name"] == group
            ]

            sheet.to_excel(
                writer,
                sheet_name=group[:31],
                index=False
            )

    print("✅ peer_comparison.xlsx generated")


def main():

    print("=" * 60)
    print("Loading Peer Data...")
    print("=" * 60)

    df = load_peer_data()
    print(f"\nLoaded {len(df)} companies.")

    # Companies without peer group
    no_peer = df[df["peer_group_name"].isna()]

    if not no_peer.empty:

        print("\nNo peer group assigned:")

        print(
            no_peer["company_id"].tolist()
        )

    # Remove companies without peer group
    df = df.dropna(
        subset=["peer_group_name"]
    )

    print("\nLoaded Peer Data\n")
    print(df.head())

    # Calculate Percentiles
    df = calculate_peer_percentiles(df)

    # Save into SQLite
    export_df = save_peer_percentiles(df)
    print(f"✅ Rows written to SQLite : {len(export_df)}")


    # Export Excel
    export_peer_excel(df)

    print("\n✅ Peer Percentiles Generated Successfully!")

    print("\nLoaded Peer Data (First 5 Rows)\n")
    print(df.head())


if __name__ == "__main__":
    main()