## 1. Implementation
- [x] 1.1 Design CLI `query` command interface and argument behavior
- [x] 1.2 Implement `duckalog query` command in `src/duckalog/cli.py`
- [x] 1.3 Implement catalog discovery when no explicit path is provided (e.g., `catalog.duckdb` in CWD)
- [x] 1.4 Implement result rendering to stdout in a simple tabular format
- [x] 1.5 Implement clear error messages and exit codes for missing catalog files and SQL errors

## 2. Testing
- [x] 2.1 Add unit/integration tests for `duckalog query` against a small test catalog
- [x] 2.2 Test querying with explicit catalog path
- [x] 2.3 Test querying with implicit/default catalog discovery
- [x] 2.4 Test behavior when the catalog file does not exist
- [x] 2.5 Test behavior when the SQL is invalid or references missing views

## 3. Documentation
- [x] 3.1 Update CLI documentation to describe `duckalog query` usage and options
- [x] 3.2 Ensure examples and getting-started guides that reference `duckalog query` match the implemented behavior
- [x] 3.3 Add brief usage notes to `README.md` or relevant docs pages for quick reference

## 4. CLI Argument Fix
- [x] 4.1 Fix CLI argument ambiguity by changing from positional catalog argument to --catalog flag
- [x] 4.2 Update all test cases to use new --catalog flag syntax
- [x] 4.3 Update documentation examples to show flag-based usage
- [x] 4.4 Update CLI specification to reflect new argument structure

