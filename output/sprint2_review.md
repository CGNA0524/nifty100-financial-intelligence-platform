# Sprint 2 Review

## Sprint Goal
Complete Day 13 and Day 14 validation for the Nifty100 Financial Intelligence Platform.

## Completed Features
- Financial sector leverage carve-out validated.
- ROE and ROCE cross-checks completed.
- Edge-case logging implemented with timestamped append-only output.
- KPI tests created and executed.
- Screeners, demo output, and review report generated.
- Database integrity checks completed.

## Implemented KPIs
- net_profit_margin_pct
- operating_profit_margin_pct
- return_on_equity_pct
- debt_to_equity
- interest_coverage
- asset_turnover
- free_cash_flow_cr
- capex_cr
- earnings_per_share
- book_value_per_share
- dividend_payout_ratio_pct
- total_debt_cr
- cash_from_operations_cr
- revenue_cagr_5yr
- pat_cagr_5yr
- eps_cagr_5yr
- composite_quality_score

## Financial Sector Carve-Out
- Financial sector leverage warnings suppressed for banking / NBFC / insurance companies.
- Validation result: PASS.

## CAGR Engine
- 5-year Revenue CAGR, PAT CAGR, and EPS CAGR validated against the database.
- Manual spot check summary: PASS.

## Cash Flow KPIs
- Free cash flow and capital allocation pattern outputs are generated.
- `output/capital_allocation.csv` has been created.

## Composite Quality Score
- Composite score is a blended metric using profitability, growth, cash conversion, leverage, and CFO quality components.

## Database Population
- Financial ratios row count: 1041
- Duplicate company-year rows: 0

## Validation Summary
- Total ROCE anomalies: 571
- Total ROE anomalies: 522
- Formula differences: 1092
- Data source issues: 0
- Version differences: 1
- Unit tests passed: 20
- Unit tests failed: 0

## Edge Cases
- ROE anomalies logged when source values differ materially.
- ROCE anomalies logged when calculated and source values diverge materially.
- Each anomaly entry includes company, metric, difference, category, and explanation.

## Formula Decisions
- ROE uses the calculated engine value for analytics and keeps source ROE for display.
- ROCE uses operating profit as EBIT for cross-checking against the source company metric.
- Book value per share uses the companies table `book_value` when available; otherwise NULL.

## Known Data Source Issues
- Some company source ROE values are stored on a different scale than the calculated values.
- Where a source value appears to be stored as a decimal instead of a percentage, it is classified as a version difference.

## Manual Spot Check Results
- ABB, TCS, and RELIANCE all passed the manual ROE and Revenue CAGR comparison.

## Deliverables
- financial_ratios table: FOUND
- output/capital_allocation.csv: FOUND
- output/ratio_edge_cases.log: FOUND
- output/spot_check.xlsx: FOUND
- output/sprint2_review.md: FOUND
- src/analytics/ratios.py: FOUND
- src/analytics/cagr.py: FOUND
- src/analytics/cashflow_kpis.py: FOUND
- tests/kpi/: FOUND


## Screeners
- ROE > 15 and Debt-to-Equity < 1 result count: 36

## Conclusion
Sprint 2 Day 13 and Day 14 validation is complete and the project is ready for team review.
