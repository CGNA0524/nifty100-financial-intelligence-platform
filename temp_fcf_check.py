import sqlite3
import pandas as pd

conn = sqlite3.connect("db/nifty100.db")

df = pd.read_sql("""
SELECT
    company_id,
    year,
    free_cash_flow_cr
FROM financial_ratios
ORDER BY company_id, year
""", conn)

conn.close()

print(df.head(30))