# Sprint 1 Retrospective

## What Went Well

* Successfully ingested and processed all project datasets.
* Built a reusable ETL pipeline for loading Excel data into SQLite.
* Implemented normalization and validation checks.
* Verified data quality through manual and automated reviews.
* Achieved 45/45 passing unit tests.
* Loaded and verified all 12 required database tables.

## Challenges Encountered

* Some Excel files contained non-standard header rows.
* Supporting datasets (market_cap and peer_groups) were initially missing from the loader configuration.
* Pytest failed due to package import path issues.
* SQLite reload attempts caused duplicate record conflicts because of unique constraints.

## Lessons Learned

* Always verify source file structure before ingestion.
* Validate database contents after every major load operation.
* Use automated tests early to catch integration issues.
* Include supporting datasets in ETL verification checklists.

## Action Items for Future Sprints

* Add automated schema validation.
* Improve ETL error logging and exception reporting.
* Add database health-check scripts.
* Expand test coverage for data loading workflows.

## Sprint Outcome

Sprint 1 objectives were completed successfully. All required datasets were loaded, validated, tested, and verified. No open blockers remain.
