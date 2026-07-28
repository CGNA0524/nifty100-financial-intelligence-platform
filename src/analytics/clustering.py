import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# ==========================================================
# Paths
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"

OUTPUT_DIR = PROJECT_ROOT / "output"

REPORT_DIR = PROJECT_ROOT / "reports"

OUTPUT_DIR.mkdir(exist_ok=True)

REPORT_DIR.mkdir(exist_ok=True)

CLUSTER_OUTPUT = OUTPUT_DIR / "cluster_labels.csv"

ELBOW_PLOT = REPORT_DIR / "elbow_plot.png"


# ==========================================================
# Clustering Configuration
# ==========================================================

N_CLUSTERS = 5

RANDOM_STATE = 42


FEATURE_COLUMNS = [
    "return_on_equity_pct",
    "debt_to_equity",
    "revenue_cagr_5yr",
    "free_cash_flow_cr",
    "operating_profit_margin_pct",
]

# ==========================================================
# Database Connection
# ==========================================================


def get_connection():
    """
    Return SQLite database connection.
    """

    return sqlite3.connect(DB_PATH)


# ==========================================================
# Load Latest Financial Data
# ==========================================================


def load_clustering_data():
    """
    Load latest financial ratios and sector information
    required for KMeans clustering.
    """

    conn = get_connection()

    query = """
    SELECT

        fr.company_id,

        fr.year,

        fr.return_on_equity_pct,

        fr.debt_to_equity,

        fr.revenue_cagr_5yr,

        fr.free_cash_flow_cr,

        fr.operating_profit_margin_pct,

        s.broad_sector,

        c.company_name

    FROM financial_ratios fr

    LEFT JOIN companies c
        ON fr.company_id = c.id

    LEFT JOIN sectors s
        ON fr.company_id = s.company_id

    WHERE fr.year = (

        SELECT MAX(f2.year)

        FROM financial_ratios f2

        WHERE f2.company_id = fr.company_id

    )

    ORDER BY c.company_name

    """

    df = pd.read_sql(query, conn)

    conn.close()

    print("=" * 60)
    print("Sprint 6 - Day 36")
    print("Loading Clustering Dataset")
    print("=" * 60)

    print(f"\nCompanies Loaded : {len(df)}")

    return df


# ==========================================================
# Sector Median Imputation
# ==========================================================


def impute_missing_values(df):
    """
    Fill missing values using sector-wise median.
    """

    df = df.copy()

    for column in FEATURE_COLUMNS:

        df[column] = df.groupby("broad_sector")[column].transform(
            lambda x: x.fillna(x.median())
        )

        median = df[column].median()

        df[column] = df[column].fillna(median)

    print("\n✓ Missing values imputed.")

    return df


# ==========================================================
# Feature Scaling
# ==========================================================


def scale_features(df):
    """
    Scale clustering features using StandardScaler.
    """

    scaler = StandardScaler()

    scaled_features = scaler.fit_transform(df[FEATURE_COLUMNS])

    scaled_df = pd.DataFrame(scaled_features, columns=FEATURE_COLUMNS, index=df.index)

    print("\n✓ Feature scaling completed.")

    return scaled_df, scaler


# ==========================================================
# Elbow Curve
# ==========================================================


def generate_elbow_plot(scaled_df):
    """
    Generate elbow plot for KMeans.
    """

    inertia = []

    for k in range(2, 11):

        model = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=10)

        model.fit(scaled_df)

        inertia.append(model.inertia_)

    plt.figure(figsize=(8, 5))

    plt.plot(range(2, 11), inertia, marker="o")

    plt.title("KMeans Elbow Curve")

    plt.xlabel("Number of Clusters (k)")

    plt.ylabel("Inertia")

    plt.grid(True)

    plt.tight_layout()

    plt.savefig(ELBOW_PLOT, dpi=300)

    plt.close()

    print(f"\n✓ Elbow plot saved : {ELBOW_PLOT}")


# ==========================================================
# Run KMeans
# ==========================================================


def run_kmeans(df, scaled_df):
    """
    Train KMeans model and assign cluster IDs.
    """

    model = KMeans(n_clusters=N_CLUSTERS, random_state=RANDOM_STATE, n_init=10)

    labels = model.fit_predict(scaled_df)

    distances = model.transform(scaled_df)

    df = df.copy()

    df["cluster_id"] = labels

    df["distance_from_centroid"] = [
        distances[i][label] for i, label in enumerate(labels)
    ]

    print("\n✓ KMeans clustering completed.")

    return df, model


# ==========================================================
# Assign Cluster Names
# ==========================================================


def assign_cluster_names(df):
    """
    Assign descriptive names to each cluster based on
    average financial quality.
    """

    cluster_profile = df.groupby("cluster_id")[FEATURE_COLUMNS].mean().reset_index()

    cluster_profile["score"] = (
        cluster_profile["return_on_equity_pct"] * 0.30
        + cluster_profile["revenue_cagr_5yr"] * 0.25
        + cluster_profile["operating_profit_margin_pct"] * 0.20
        + cluster_profile["free_cash_flow_cr"] * 0.15
        - cluster_profile["debt_to_equity"] * 0.10
    )

    cluster_profile = cluster_profile.sort_values("score", ascending=False).reset_index(
        drop=True
    )

    names = {
        cluster_profile.loc[0, "cluster_id"]: "High Quality Compounders",
        cluster_profile.loc[1, "cluster_id"]: "Defensive Leaders",
        cluster_profile.loc[2, "cluster_id"]: "Emerging Growth",
        cluster_profile.loc[3, "cluster_id"]: "Value Cyclicals",
        cluster_profile.loc[4, "cluster_id"]: "Turnaround Candidates",
    }

    df["cluster_name"] = df["cluster_id"].map(names)

    print("\n✓ Cluster names assigned.")

    return df


# ==========================================================
# Export Results
# ==========================================================


def export_clusters(df):
    """
    Export clustering output.
    """

    output = df[
        [
            "company_id",
            "company_name",
            "broad_sector",
            "cluster_id",
            "cluster_name",
            "distance_from_centroid",
        ]
    ].copy()

    output["distance_from_centroid"] = output["distance_from_centroid"].round(4)

    output.to_csv(CLUSTER_OUTPUT, index=False)

    print("\n✓ Cluster labels exported.")

    print(f"\nSaved To:\n{CLUSTER_OUTPUT}")


# ==========================================================
# Main
# ==========================================================


def main():

    df = load_clustering_data()

    df = impute_missing_values(df)

    scaled_df, scaler = scale_features(df)

    generate_elbow_plot(scaled_df)

    df, model = run_kmeans(df, scaled_df)

    df = assign_cluster_names(df)

    export_clusters(df)

    print("\n" + "=" * 60)
    print("Sprint 6 - Day 36 Completed")
    print("=" * 60)

    print(f"\nCompanies Clustered : {len(df)}")

    print(f"Clusters Created : {N_CLUSTERS}")


if __name__ == "__main__":
    main()
