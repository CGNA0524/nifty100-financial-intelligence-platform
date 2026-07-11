import sqlite3
import pandas as pd

conn = sqlite3.connect("db/nifty100.db")

print(
    pd.read_sql(
        "PRAGMA table_info(companies)",
        conn
    )
)

conn.close()