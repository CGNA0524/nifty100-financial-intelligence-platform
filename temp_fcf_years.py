import sqlite3
import pandas as pd

conn = sqlite3.connect("db/nifty100.db")

df = pd.read_sql("""
SELECT
    company_id,
    COUNT(*) AS total_years
FROM financial_ratios
GROUP BY company_id
ORDER BY total_years ASC
""", conn)

conn.close()

print(df.head(20))

print("\nMinimum Years :", df["total_years"].min())
print("Maximum Years :", df["total_years"].max())