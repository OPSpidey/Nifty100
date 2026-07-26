# Validation Summary

## Validation Results

Total validation records: 97

### Tax Percentage Warnings

68 records

Reason:
Tax rate outside expected business range.

Status:
Accepted as business-rule exceptions.

| Validation | Count | Status |
|------------|------:|--------|
| Tax warnings | 68 | Accepted |
| Dividend warnings | 25 | Accepted |
| EPS exceptions | 1 | Reviewed |
| URL issues | 3 | Non-critical |
| Critical failures | 0 | Passed |

### Tax Percentage Warnings

68 records

### Dividend Payout Warnings

25 records

Reason:
Dividend payout exceeded 100%.

Status:
Accepted as valid business cases.

### EPS Validation

1 record

Company:
TATAPOWER

Issue:
Positive profit with negative EPS.

Status:
Reviewed and retained as a source-data exception.

### URL Validation

3 records

Company:
TVS Motor Company Ltd

Issue:
Invalid URL format.

Status:
Non-critical metadata issue.

### URL Validation

3 records

Company:
TVS Motor Company Ltd

Issue:
Invalid URL format.

Status:
Non-critical metadata issue.

## Validated Data Sources

- companies
- profitandloss
- balancesheet
- cashflow
- sectors

## Conclusion

No unresolved CRITICAL ETL failures remain.

Dataset approved for downstream ratio and screener work.