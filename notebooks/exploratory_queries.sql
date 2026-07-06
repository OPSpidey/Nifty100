-- 1. Count companies
SELECT COUNT(*) AS company_count
FROM companies;

-- 2. Count profit and loss records
SELECT COUNT(*) AS pnl_rows
FROM profitandloss;

-- 3. Count balance sheet records
SELECT COUNT(*) AS balance_sheet_rows
FROM balancesheet;

-- 4. Count cash flow records
SELECT COUNT(*) AS cashflow_rows
FROM cashflow;

-- 5. Count stock price records
SELECT COUNT(*) AS stock_price_rows
FROM stock_prices;

-- 6. Companies per broad sector
SELECT broad_sector, COUNT(*) AS company_count
FROM sectors
GROUP BY broad_sector
ORDER BY company_count DESC;

-- 7. Top 10 companies by latest market cap
SELECT company_id, year, market_cap_crore
FROM market_cap
ORDER BY year DESC, market_cap_crore DESC
LIMIT 10;

-- 8. Year coverage by company in profit and loss
SELECT company_id, COUNT(DISTINCT year) AS years_available
FROM profitandloss_clean
GROUP BY company_id
ORDER BY years_available DESC, company_id;

-- 9. Top 10 companies by latest ROE
SELECT company_id, year, return_on_equity_pct
FROM financial_ratios
WHERE return_on_equity_pct IS NOT NULL
ORDER BY year DESC, return_on_equity_pct DESC
LIMIT 10;

-- 10. Companies with high leverage outside Financials
SELECT fr.company_id,
    fr.year,
    s.broad_sector,
    fr.debt_to_equity
FROM financial_ratios fr
LEFT JOIN sectors s
    ON fr.company_id = s.company_id
WHERE fr.high_leverage_flag = 1
ORDER BY fr.debt_to_equity DESC;
