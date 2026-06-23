-- Q1 Total Companies
SELECT COUNT(*) AS total_companies
FROM companies;

-- Q2 Companies By Sector
SELECT
    broad_sector,
    COUNT(*) AS company_count
FROM sectors
GROUP BY broad_sector
ORDER BY company_count DESC;

-- Q3 Top 10 Market Cap Companies
SELECT
    c.company_name,
    m.market_cap_crore
FROM market_cap m
JOIN companies c
ON m.company_id = c.id
ORDER BY m.market_cap_crore DESC
LIMIT 10;

-- Q4 Top 10 Revenue Companies
SELECT
    c.company_name,
    p.sales
FROM profitandloss p
JOIN companies c
ON p.company_id = c.id
ORDER BY p.sales DESC
LIMIT 10;

-- Q5 Top 10 Net Profit Companies
SELECT
    c.company_name,
    p.net_profit
FROM profitandloss p
JOIN companies c
ON p.company_id = c.id
ORDER BY p.net_profit DESC
LIMIT 10;

-- Q6 Highest ROE
SELECT
    company_id,
    year,
    return_on_equity_pct
FROM financial_ratios
ORDER BY return_on_equity_pct DESC
LIMIT 10;

-- Q7 Debt Free Companies
SELECT
    company_id,
    year
FROM financial_ratios
WHERE debt_to_equity = 0;

-- Q8 Strong Cash Flow Companies
SELECT
    company_id,
    year,
    cash_from_operations_cr
FROM financial_ratios
ORDER BY cash_from_operations_cr DESC
LIMIT 10;

-- Q9 Highest Dividend Yield
SELECT
    company_id,
    year,
    dividend_yield_pct
FROM market_cap
ORDER BY dividend_yield_pct DESC
LIMIT 10;

-- Q10 Company Coverage Check
SELECT
    company_id,
    COUNT(*) AS years_available
FROM profitandloss
GROUP BY company_id
ORDER BY years_available ASC;