import sqlite3
import pandas as pd

conn = sqlite3.connect("db/nifty100.db")

query = """
SELECT

fr.company_id,
fr.year,

fr.return_on_equity_pct,
fr.debt_to_equity,
fr.interest_coverage,
fr.asset_turnover,
fr.free_cash_flow_cr,
fr.revenue_cagr_5yr,
fr.pat_cagr_5yr,
fr.eps_cagr_5yr,
fr.composite_quality_score,

c.roce_percentage,

mc.market_cap_crore,
mc.pe_ratio,
mc.pb_ratio,
mc.dividend_yield_pct,

pl.sales,
pl.net_profit,
pl.opm_percentage

FROM financial_ratios fr

LEFT JOIN companies c
ON fr.company_id = c.id

LEFT JOIN market_cap mc
ON fr.company_id = mc.company_id
AND substr(fr.year,-4)=CAST(mc.year AS TEXT)

LEFT JOIN profitandloss pl
ON fr.company_id = pl.company_id
AND fr.year = pl.year

WHERE fr.year = (

SELECT MAX(f2.year)

FROM financial_ratios f2

WHERE f2.company_id = fr.company_id

)

"""

df = pd.read_sql(query, conn)

print(df.head())

print("\nColumns:\n")

print(df.columns.tolist())

conn.close()