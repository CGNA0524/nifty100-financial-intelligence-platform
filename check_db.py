import sqlite3
import pandas as pd

conn = sqlite3.connect("db/nifty100.db")

print("financial_ratios")
print(pd.read_sql("""
SELECT company_id, year
FROM financial_ratios
LIMIT 5
""", conn))

print("\nmarket_cap")
print(pd.read_sql("""
SELECT company_id, year
FROM market_cap
LIMIT 5
""", conn))

print("\nprofitandloss")
print(pd.read_sql("""
SELECT company_id, year
FROM profitandloss
LIMIT 5
""", conn))

print("\ncompanies")
print(pd.read_sql("""
SELECT id, company_name
FROM companies
LIMIT 5
""", conn))

conn.close()