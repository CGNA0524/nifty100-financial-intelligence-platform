from loader import load_all_files


def validate_datasets():
    datasets = load_all_files()

    print("\nDataset Validation Report")
    print("=" * 60)

    for name, df in datasets.items():

        print(f"\n{name}")

        print("-" * 40)

        print(f"Rows: {df.shape[0]}")
        print(f"Columns: {df.shape[1]}")

        print(f"Missing Values: {df.isnull().sum().sum()}")


if __name__ == "__main__":
    validate_datasets()