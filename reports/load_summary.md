# Load Audit Summary

## Dataset Loading Results

| Dataset          | Rows Loaded |
| ---------------- | ----------- |
| Companies        | 92          |
| Balance Sheet    | 1312        |
| Profit & Loss    | 1276        |
| Cash Flow        | 1187        |
| Analysis         | 20          |
| Documents        | 1585        |
| Pros & Cons      | 16          |
| Stock Prices     | 5520        |
| Financial Ratios | 1184        |
| Market Cap       | 552         |
| Peer Groups      | 56          |
| Sectors          | 92          |

## Observations

* All 12 source files loaded successfully.
* Sector mappings are complete for the 92 companies in the company master.
* Clean tables remove duplicate or placeholder annual records before ratio generation.
* Analysis and Pros/Cons datasets contain summarized information and therefore have lower record counts.

## Status

Load audit passed.

## Validation Checks

- Duplicate records: None
- Missing company IDs: None
- Foreign key validation: Passed
- Row count verification: Passed

## Generated On

YYYY-MM-DD HH:MM
