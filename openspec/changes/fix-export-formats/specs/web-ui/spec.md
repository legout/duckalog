## ADDED Requirements

### Requirement: Export format correctness
Exports MUST succeed and preserve schema information for all supported formats, even when no rows are returned.

#### Scenario: Parquet export retains columns for empty and non-empty results
- **GIVEN** a query that returns zero rows and another that returns data
- **WHEN** the user exports as Parquet
- **THEN** the download succeeds without server errors, maintains the column schema for empty results, and contains the expected rows for non-empty results
- **AND** the response includes `Content-Type` and `Content-Disposition` headers with a deterministic filename.

#### Scenario: CSV and Excel exports are consistent on empty results
- **WHEN** a query/export produces zero rows
- **THEN** CSV and Excel responses include headers with the expected columns and set `Content-Type` and `Content-Disposition` with a filename
- **AND** the same behaviors hold for non-empty results.
