## Why

The project needs a clear, versioned configuration schema for DuckDB catalogs so that YAML/JSON configs, environment-variable interpolation, attachments, Iceberg catalogs, and multi-source view definitions behave consistently across the Python API and CLI.

Today this behavior is only described in `docs/PRD_Spec.md`, which makes it harder to evolve the config model, reason about breaking changes, and keep implementation and tests aligned with the intended contract.

## What Changes

- Introduce a `config` capability spec that defines:
  - Accepted config formats (YAML/JSON) and a required `version` field.
  - The structure of `duckdb`, `attachments`, `iceberg_catalogs`, and `views` blocks.
  - Supported view `source` types (`parquet`, `delta`, `iceberg`, `duckdb`, `sqlite`, `postgres`) and their required fields.
- Specify environment variable interpolation semantics for `${env:VAR}` placeholders, including failure behavior when variables are missing.
- Define validation rules for:
  - Unique view names within a config.
  - Mutual exclusivity between `sql` and `source`-based view definitions.
  - Required fields per attachment and catalog type.
- Make the Pydantic models (`Config`, `DuckDBConfig`, `AttachmentsConfig`, `ViewConfig`, `IcebergCatalogConfig`) the normative representation of the config schema.

## Impact

- Establishes a single source of truth for catalog config behavior, independent of implementation details.
- Reduces the risk of breaking changes to config files by requiring updates to the `config` spec and associated OpenSpec changes.
- Provides a stable foundation for subsequent changes that implement the engine and CLI behavior (`build`, `generate-sql`, `validate`) against this schema.

