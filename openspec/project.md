# Project Context

## Purpose
duckalog is a Python library and CLI for building DuckDB catalogs (views) from declarative YAML/JSON configuration files.

- Define DuckDB databases, attachments, Iceberg catalogs, and views as code.
- Build or update `.duckdb` catalogs reproducibly across machines and environments.
- Support multi-source views over S3 Parquet, Delta Lake, Iceberg, and attached DuckDB/SQLite/Postgres databases.
- Treat DuckDB catalogs as versioned, testable, and shareable artifacts.

## Tech Stack
- Language: Python (>= 3.9).
- Packaging: `setuptools` with `src/` layout (`src/duckalog`).
- Core runtime libraries:
  - `duckdb` – embedded analytical database engine.
  - `pyyaml` – YAML parsing for configuration files.
  - `pydantic>=2` – configuration models and validation.
  - `typer` (built atop `click`) – CLI command definitions and argument parsing.
- CLI entry point: `duckalog` (mapped to `duckalog.cli:app`).
- Specs / planning: OpenSpec files under `openspec/` and product spec in `docs/PRD_Spec.md`.

## Project Conventions

### Code Style
- Follow standard Python style (PEP 8) with type hints on public functions and classes.
- Prefer small, focused modules (e.g. `config`, `engine`, `cli`) over large monoliths.
- Use Pydantic models as the single source of truth for config schemas.
- Keep I/O (file/DB access, environment lookups) at module boundaries; keep core logic pure and testable.
- Use descriptive, domain-aligned names (e.g. `AttachmentConfig`, `ViewConfig`, `IcebergCatalogConfig`).

### Architecture Patterns
- Separate responsibilities:
  - Config layer: read YAML/JSON, interpolate environment variables, validate via Pydantic models.
  - SQL generation layer: build `CREATE VIEW` statements from typed config objects.
  - Engine layer: open DuckDB connections, attach external systems, and apply SQL.
- CLI layer: Typer commands delegating to library functions.
- Treat DuckDB as a side-effect boundary; keep connection handling centralized.
- Prefer pure functions for SQL generation and config transformations to simplify testing.
- Extend behavior by adding new config types + SQL generation paths rather than special-casing in the engine.

### Testing Strategy
- Use pytest-style tests (default location: `tests/`) for both unit and integration coverage.
- Unit tests:
  - Config parsing and validation for YAML/JSON (including env interpolation).
  - SQL generation for different source types (S3 Parquet, Delta, Iceberg, attached DBs, raw SQL).
- Integration tests:
  - Use temporary DuckDB files to verify that views are created as expected.
  - Smoke tests for attachments (DuckDB/SQLite/Postgres) using minimal fixtures.
- Prefer deterministic tests (no network dependency unless explicitly required for a given backend).
- Add tests for new behaviors before or alongside implementation; keep PRD and specs in sync with behavior.

### Git Workflow
- Use small, focused branches per change; name branches with the related OpenSpec `change-id` when applicable (e.g. `add-s3-parquet-support`).
- Reference relevant OpenSpec change IDs in PR titles and/or first commit messages.
- Keep spec changes (`openspec/`, `docs/`) and implementation changes (`src/`, `tests/`) clear in commit messages.
- Prefer incremental, reviewable PRs over large multi-feature changes.

## Domain Context
- The core domain is DuckDB catalogs: reproducible sets of views defined over multiple underlying data systems.
- Configuration files describe:
  - DuckDB database path and session settings (pragmas).
  - Attachments (other DuckDB files, SQLite DBs, Postgres DBs, etc.).
  - Iceberg catalogs and table references.
  - Views backed by:
    - S3 Parquet datasets.
    - Delta Lake tables.
    - Iceberg tables.
    - Attached DuckDB/SQLite/Postgres tables.
    - Arbitrary SQL queries.
- Credentials are typically not stored directly in configs; configs may reference environment variables (e.g. `${env:AWS_ACCESS_KEY_ID}`).
- See `docs/PRD_Spec.md` for the authoritative product and technical spec, including detailed config examples and use cases.

## Important Constraints
- Idempotency: running the build command multiple times with the same config should produce the same catalog.
- Safety: avoid logging secrets or full connection strings; any logs must redact or omit sensitive values.
- Config-first: the YAML/JSON config is the primary source of truth; manual catalog edits are discouraged.
- Offline-friendly: SQL generation and config validation should work without live connections when possible (e.g. `dry_run` modes).
- Backward compatibility: avoid breaking existing config schemas without an explicit OpenSpec change and migration path.
- Minimal dependencies: keep the runtime dependency set small and focused (no heavy frameworks).
- CLI usability: commands should fail fast with clear, actionable error messages.

## External Dependencies
- DuckDB engine (embedded library) used for executing SQL and creating views.
- Object storage / filesystems (e.g. S3 or compatible endpoints) for Parquet datasets.
- Lakehouse and table formats supported via DuckDB:
  - Delta Lake tables.
  - Iceberg tables and Iceberg catalogs.
- Relational databases used as attachments:
  - Postgres (via DuckDB connectors).
  - SQLite databases.
  - Other DuckDB databases.
- Environment configuration:
  - Environment variables for credentials and connection details.
  - Optional `.env`/secrets management handled by the surrounding environment (not by this library itself).
- Tooling dependencies for project workflow (not runtime): OpenSpec CLI (`openspec`) for managing specs and change proposals.
