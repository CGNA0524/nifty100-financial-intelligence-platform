import sqlite3
import pandas as pd

DB_PATH = "db/nifty100.db"

conn = sqlite3.connect(DB_PATH)

tables = [
    "financial_ratios",
    "cashflow",
    "profitandloss"
]

for table in tables:
    print("\n" + "=" * 60)
    print("TABLE :", table)
    print("=" * 60)

    columns = pd.read_sql(
        f"PRAGMA table_info({table})",
        conn
    )

    print(columns["name"].tolist())

conn.close()