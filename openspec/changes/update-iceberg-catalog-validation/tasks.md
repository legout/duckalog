## 1. Iceberg catalog reference validation

- [ ] 1.1 Add spec deltas under `config` or `catalog-build` describing required validation of `view.catalog` against `iceberg_catalogs`.
- [ ] 1.2 Implement cross-reference checks so that missing catalogs cause a clear error before any DuckDB queries are executed.
- [ ] 1.3 Add tests covering valid and invalid Iceberg catalog references in both pure config validation and full catalog builds.

