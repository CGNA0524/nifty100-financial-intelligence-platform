import sqlite3

conn = sqlite3.connect(r"db\nifty100.db")
cursor = conn.cursor()

new_columns = [
    ("revenue_cagr_5yr", "REAL"),
    ("pat_cagr_5yr", "REAL"),
    ("eps_cagr_5yr", "REAL"),
    ("composite_quality_score", "REAL")
]

for column_name, column_type in new_columns:
    try:
        cursor.execute(
            f"ALTER TABLE financial_ratios ADD COLUMN {column_name} {column_type}"
        )
        print(f"✅ Added: {column_name}")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print(f"⚠ Already exists: {column_name}")
        else:
            raise

conn.commit()
conn.close()

print("\nSchema Updated Successfully!")