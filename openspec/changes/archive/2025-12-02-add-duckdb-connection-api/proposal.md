# Change: Add DuckDB Connection API Functions

## Why
Users currently need to perform two separate steps to work with Duckalog catalogs: 1) build/rebuild the catalog using `build_catalog()`, and 2) create a manual DuckDB connection using `duckdb.connect()`. This separation requires users to manage two different interfaces and track database paths manually. The current workflow is cumbersome and error-prone, especially for new users who just want to connect to their catalog database and start querying.

## What Changes
- **Add `connect_to_catalog()` Python API**: Function that connects to an existing DuckDB database created by Duckalog and returns a DuckDB connection
- **Add `connect_and_build_catalog()` Python API**: Function that builds/rebuilds the catalog from a config and returns a DuckDB connection to the resulting database
- **Streamlined workflow**: Enable users to go from configuration to active database connection in a single function call
- **Connection management**: Include proper connection lifecycle guidance and best practices

## Impact
- **Affected specs**: python-api (enhanced capability)
- **Affected code**: `src/duckalog/python_api.py`, potentially `src/duckalog/__init__.py` for exports
- **User Experience**: Significantly reduces friction for users who want to start querying catalogs immediately
- **Breaking Changes**: None - this is additive functionality that builds on existing capabilities
- **Dependencies**: Uses existing `build_catalog()` engine + DuckDB connection management

## Alternative Approaches Considered
1. **Extend build_catalog()**: Could have build_catalog() return a connection instead of None (but this would be a breaking change)
2. **Add connection classes**: Could create duckalog-specific connection wrapper classes (overkill for current need)
3. **Modify approach**: Could make build_catalog() more flexible (but current approach is clean separation of concerns)

The chosen approach adds convenience functions without breaking the existing separation between catalog building and connection management.