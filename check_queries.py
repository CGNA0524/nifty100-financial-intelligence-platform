import sqlite3

conn = sqlite3.connect("db/nifty100.db")
cursor = conn.cursor()

print("===== ROW COUNT =====")
cursor.execute("SELECT COUNT(*) FROM financial_ratios")
print(cursor.fetchone())

print("\n===== CAGR =====")
cursor.execute("""
SELECT company_id, year,
revenue_cagr_5yr,
pat_cagr_5yr,
eps_cagr_5yr
FROM financial_ratios
WHERE revenue_cagr_5yr IS NOT NULL
LIMIT 10
""")

for row in cursor.fetchall():
    print(row)

print("\n===== TOP COMPOSITE SCORE =====")
cursor.execute("""
SELECT company_id, year, composite_quality_score
FROM financial_ratios
ORDER BY composite_quality_score DESC
LIMIT 10
""")

for row in cursor.fetchall():
    print(row)

print("\n===== DUPLICATES =====")
cursor.execute("""
SELECT company_id, year, COUNT(*)
FROM financial_ratios
GROUP BY company_id, year
HAVING COUNT(*) > 1
""")

rows = cursor.fetchall()

if rows:
    for row in rows:
        print(row)
else:
    print("No duplicates found")

conn.close()