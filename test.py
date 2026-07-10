import sqlite3
import pandas as pd

conn = sqlite3.connect("db/nifty100.db")

print(pd.read_sql("""
SELECT peer_group_name,
COUNT(DISTINCT company_id) AS companies
FROM peer_percentiles
GROUP BY peer_group_name
ORDER BY peer_group_name
""", conn))

conn.close()