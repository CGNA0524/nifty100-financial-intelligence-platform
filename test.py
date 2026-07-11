import sqlite3
import pandas as pd

conn = sqlite3.connect("db/nifty100.db")

print(pd.read_sql("""

SELECT COUNT(*)
AS total_rows

FROM peer_percentiles

""", conn))

conn.close()