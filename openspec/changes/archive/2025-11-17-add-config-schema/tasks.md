## 1. Config schema and env interpolation

- [x] 1.1 Implement `load_config(path: str) -> Config` that parses YAML/JSON, interpolates `${env:VAR}` placeholders, and returns a validated Pydantic `Config` instance.
- [x] 1.2 Define Pydantic models for `DuckDBConfig`, `AttachmentsConfig`, `IcebergCatalogConfig`, `ViewConfig`, and the root `Config` with validation matching the spec requirements.
- [x] 1.3 Add tests for:
  - YAML and JSON parsing.
  - Environment interpolation success and failure cases.
  - Unique view name enforcement.
  - Validation of required fields for views, attachments, and Iceberg catalogs.
