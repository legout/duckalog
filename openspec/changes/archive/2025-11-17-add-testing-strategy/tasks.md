## 1. Testing strategy implementation

- [x] 1.1 Add or update pytest suites to cover:
  - Config parsing and validation (YAML/JSON, env interpolation, unique view names).
  - SQL generation for all supported source types and options.
  - Engine behavior for building catalogs using temporary DuckDB files and simple attachment fixtures.
- [x] 1.2 Add tests for CLI commands to verify exit codes and key behaviors (build, generate-sql, validate).
- [x] 1.3 Ensure the default test suite runs without external network dependencies and uses only local resources.
