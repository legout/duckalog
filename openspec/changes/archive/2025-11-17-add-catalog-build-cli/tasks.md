## 1. Catalog build engine and CLI

- [x] 1.1 Implement `build_catalog(config_path: str, db_path: Optional[str] = None, dry_run: bool = False, verbose: bool = False)` according to the `catalog-build` spec.
- [x] 1.2 Implement CLI commands `build`, `generate-sql`, and `validate` using Click, delegating to the config and engine layers.
- [x] 1.3 Add tests for:
  - Idempotent catalog builds (re-running produces the same views).
  - SQL generation without DB connections (`generate-sql`).
  - Validation behavior and exit codes for `validate`.
  - Error handling when attachments, Iceberg catalogs, or view creation fail.
