## 1. Implementation
- [x] Fix Parquet export to build tables from list-of-dicts without TypeError and to preserve column schema for empty datasets
- [x] Ensure CSV/Excel/Parquet responses always set `Content-Type` and `Content-Disposition` with a filename, even when the result is empty
- [x] Cover empty and non-empty exports with unit tests across all formats

## 2. Validation
- [x] `openspec validate fix-export-formats --strict`
- [x] Tests for `/api/export` pass for csv/parquet/excel with empty rows
