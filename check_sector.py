import sqlite3
import pandas as pd

conn = sqlite3.connect("db/nifty100.db")

df = pd.read_sql("""
SELECT DISTINCT broad_sector
FROM sectors
ORDER BY broad_sector
""", conn)

print(df)

conn.close()