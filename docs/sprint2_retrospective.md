Sprint 2 Retrospective

Completed
- Implemented financial ratio engine.
- Added ROE, ROCE, D/E, Asset Turnover, Interest Coverage and Free Cash Flow calculations.
- Populated financial_ratios SQLite table.
- Added validation against source ROE and ROCE values.
- Implemented Financial sector leverage carve-out.
- Generated ratio_edge_cases.log.

Key Formula Decisions
- ROE calculated using Net Profit / (Equity Capital + Reserves).
- ROCE calculated using EBIT / (Equity + Reserves + Borrowings).
- Debt-to-Equity suppressed for Financial sector companies.

Edge Cases
- Duplicate financial records removed.
- Cash flow duplicates resolved using highest absolute CFO.
- Source ROE and ROCE differences logged separately.
- Missing values handled gracefully.

Lessons Learned
- Source datasets may contain inconsistent historical values.
- Financial sector requires different leverage interpretation.
- Validation logging improves data quality auditing.

Future Improvements
- Add CAGR metrics.
- Composite Quality Score.
- Automated anomaly classification.