# Day 43 Performance Notes

## Load Test
- 10 concurrent screener API requests executed.
- All requests completed within the required 10 second limit.
- Result: PASS

## Dashboard Performance
Company profiles tested:
- TCS
- INFY
- RELIANCE
- HDFCBANK
- SUNPHARMA

All profile loads completed under 3 seconds.

Result: PASS

## End-to-End Integration
- FastAPI running on port 8000.
- Streamlit running on port 8501.
- No port conflicts detected.
- Dashboard successfully loaded API data.

Result: PASS

## SQLite Optimization
Added indexes:

- balancesheet(company_id, year)
- profitandloss(company_id, year)
- cashflow(company_id, year)
- financial_ratios(company_id, year)
- market_cap(company_id, year)
- stock_prices(company_id, date)

## Bottlenecks
No major performance bottlenecks identified.
SQLite performance is acceptable for the current dataset size.