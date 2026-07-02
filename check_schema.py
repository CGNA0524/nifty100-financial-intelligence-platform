import sqlite3

conn = sqlite3.connect(r"db\nifty100.db")
cursor = conn.cursor()

for table in ["profitandloss", "balancesheet", "cashflow"]:
    print(f"\n===== {table.upper()} =====")
    cursor.execute(f"PRAGMA table_info({table})")
    for row in cursor.fetchall():
        print(row)

conn.close()


import sqlite3

conn = sqlite3.connect("db/nifty100.db")
cursor = conn.cursor()

print("===== FINANCIAL RATIOS =====")

cursor.execute("PRAGMA table_info(financial_ratios)")

for row in cursor.fetchall():
    print(row)

conn.close()