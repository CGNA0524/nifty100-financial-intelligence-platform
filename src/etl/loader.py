import pandas as pd
from pathlib import Path


RAW_DATA_PATH = Path("data/raw")


def load_excel(filename):
    """
    Load Excel file using header row 1
    (Row 0 contains metadata/title)
    """
    filepath = RAW_DATA_PATH / filename

    df = pd.read_excel(filepath, header=1)

    return df


def load_all_files():
    """
    Load all project datasets
    """

    files = [
        "companies.xlsx",
        "profitandloss.xlsx",
        "balancesheet.xlsx",
        "cashflow.xlsx",
        "analysis.xlsx",
        "documents.xlsx",
        "prosandcons.xlsx",
        "sectors.xlsx",
        "stock_prices.xlsx",
        "market_cap.xlsx",
        "financial_ratios.xlsx",
        "peer_groups.xlsx"
    ]

    datasets = {}

    print("\nLoading Datasets...")
    print("=" * 60)

    for file in files:
        try:
            df = load_excel(file)

            datasets[file] = df

            print(
                f"SUCCESS | {file:<25} Rows: {df.shape[0]:<6} Columns: {df.shape[1]}"
            )

        except Exception as e:
            print(f"ERROR   | {file} -> {e}")

    return datasets


if __name__ == "__main__":

    datasets = load_all_files()

    print("\nCompanies Dataset Preview")
    print("=" * 60)

    companies = datasets["companies.xlsx"]

    print("Shape:", companies.shape)

    print("\nColumns:")
    print(companies.columns.tolist())

    print("\nFirst 5 Rows:")
    print(companies.head())