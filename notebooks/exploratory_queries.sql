-- Count companies
SELECT COUNT(*) FROM companies;

-- Count stock price records
SELECT COUNT(*) FROM stock_prices;

-- Count sectors
SELECT COUNT(*) FROM sectors;

-- Top 10 companies by market cap
SELECT company_id, market_cap
FROM market_cap
ORDER BY market_cap DESC
LIMIT 10;

-- Companies per sector
SELECT broad_sector, COUNT(*)
FROM sectors
GROUP BY broad_sector;

-- Available years in stock prices
SELECT
MIN(date),
MAX(date)
FROM stock_prices;