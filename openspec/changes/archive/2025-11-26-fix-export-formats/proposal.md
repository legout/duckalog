# Change: Fix export format correctness

## Why
The UI’s export endpoints are broken for Parquet (TypeError on list-of-dicts), lose schema for empty datasets, and return inconsistent headers/filenames for empty CSVs. These defects violate the export requirement and make downloads unreliable even for small, local usage.

## What Changes
- Correct Parquet serialization to preserve columns and succeed for empty and non-empty results
- Ensure CSV/Excel/Parquet responses always include stable `Content-Type` and `Content-Disposition` headers, even when zero rows are returned
- Add regression tests around empty and non-empty exports for all supported formats

## Impact
- Affected specs: web-ui
- Affected code: `src/duckalog/ui.py` export handlers and helpers
- No API changes; fixes behavior to meet existing contract
