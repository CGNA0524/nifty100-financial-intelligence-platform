import sqlite3
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

DB_PATH = "db/nifty100.db"
OUTPUT_FOLDER = "reports/radar_charts"

os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)
def load_radar_data():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql("""

    SELECT

        pg.peer_group_name,
        pg.company_id,
        c.company_name,

        fr.return_on_equity_pct,
        c.roce_percentage,
        fr.net_profit_margin_pct,
        fr.debt_to_equity,
        fr.free_cash_flow_cr,
        fr.pat_cagr_5yr,
        fr.revenue_cagr_5yr,
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
METRICS = [

    "return_on_equity_pct",
    "roce_percentage",
    "net_profit_margin_pct",
    "debt_to_equity",
    "free_cash_flow_cr",
    "pat_cagr_5yr",
    "revenue_cagr_5yr",
    "composite_quality_score"

]
def create_standalone_chart(company_row, nifty_average):

    labels = ["Composite"]

    company_value = [
        company_row["composite_quality_score"]
        if pd.notna(company_row["composite_quality_score"])
        else 0
    ]

    nifty_value = [
        nifty_average
    ]

    angles = [0, 2 * np.pi]

    company_plot = company_value * 2
    nifty_plot = nifty_value * 2

    fig = plt.figure(figsize=(5,5))

    ax = plt.subplot(
        111,
        polar=True
    )

    ax.plot(
        angles,
        company_plot,
        linewidth=2,
        label=company_row["company_id"]
    )

    ax.fill(
        angles,
        company_plot,
        alpha=0.25
    )

    ax.plot(
        angles,
        nifty_plot,
        linewidth=2,
        linestyle="--",
        label="Nifty100 Avg"
    )

    ax.set_xticks([0])
    ax.set_xticklabels(["Composite"])

    plt.legend()

    filename = os.path.join(
        OUTPUT_FOLDER,
        f"{company_row['company_id']}_standalone.png"
    )

    plt.savefig(
        filename,
        dpi=200
    )

    plt.close()

def create_radar_chart(company_row, peer_average):

    labels = [
        "ROE",
        "ROCE",
        "NPM",
        "D/E",
        "FCF",
        "PAT CAGR",
        "Revenue CAGR",
        "Composite"
    ]

    company_values = []

    average_values = []

    for metric in METRICS:

        company_values.append(
            0 if pd.isna(company_row[metric]) else company_row[metric]
        )

        average_values.append(
            0 if pd.isna(peer_average[metric]) else peer_average[metric]
        )

    # Lower D/E is better
    company_values[3] = max(
        0,
        100 - company_values[3]
    )

    average_values[3] = max(
        0,
        100 - average_values[3]
    )

    angles = np.linspace(
        0,
        2 * np.pi,
        len(labels),
        endpoint=False
    ).tolist()

    company_values += company_values[:1]
    average_values += average_values[:1]
    angles += angles[:1]

    fig = plt.figure(figsize=(6, 6))

    ax = plt.subplot(
        111,
        polar=True
    )

    ax.plot(
        angles,
        company_values,
        linewidth=2,
        label=company_row["company_id"]
    )

    ax.fill(
        angles,
        company_values,
        alpha=0.25
    )

    ax.plot(
        angles,
        average_values,
        linewidth=2,
        linestyle="--",
        label="Peer Average"
    )

    ax.set_xticks(
        angles[:-1]
    )

    ax.set_xticklabels(
        labels
    )

    ax.set_title(
        company_row["company_id"]
    )

    ax.legend(
        loc="upper right"
    )

    plt.tight_layout()

    filename = os.path.join(
        OUTPUT_FOLDER,
        f"{company_row['company_id']}_radar.png"
    )

    plt.savefig(
        filename,
        dpi=200
    )

    plt.close()
def generate_all_radar_charts(df):

    print("\nGenerating Radar Charts...\n")

    os.makedirs(
        OUTPUT_FOLDER,
        exist_ok=True
    )

    nifty_average = df["composite_quality_score"].mean()

    # Peer group companies
    for group in df["peer_group_name"].dropna().unique():

        group_df = df[
            df["peer_group_name"] == group
        ]

        peer_average = group_df[
            METRICS
        ].mean(
            numeric_only=True
        )

        for _, row in group_df.iterrows():

            create_radar_chart(
                row,
                peer_average
            )

def main():

    print("=" * 60)
    print("Loading Radar Chart Data...")
    print("=" * 60)

    df = load_radar_data()

    print(f"\nLoaded {len(df)} companies.")

    generate_all_radar_charts(df)

    print("\n✅ Day 19 Completed Successfully!")
    print(f"Radar Charts saved in : {OUTPUT_FOLDER}")


if __name__ == "__main__":
    main()