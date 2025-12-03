# Change: Refactor Secret Models and Usage

## Why

Duckalog’s secret configuration currently mixes two modeling approaches:

- A generic `SecretConfig` model used throughout the config and engine layers.
- Per-backend secret models (`S3SecretConfig`, `AzureSecretConfig`, `GCSSecretConfig`, `HTTPSecretConfig`, `PostgresSecretConfig`, `MySQLSecretConfig`) that exist in `secret_types.py` and were historically duplicated in `config.py`.

This duplication has led to:

- Two potential sources of truth for secret fields and validation.
- Increased risk of drift when adding or changing secret attributes.
- Confusion for contributors about which model is canonical and how `generate_secret_sql` interprets secrets.

Recent work has implemented real DuckDB `CREATE SECRET` statements and hardened SQL generation. To keep this maintainable, we need a single, clearly specified secret model surface that all code and docs agree on.

This change refines and simplifies the behavior introduced by archived changes `2025-11-17-add-duckdb-secrets` and `2025-12-02-implement-secrets-creation`, making `SecretConfig` the canonical configuration model that those behaviors rely on.

## What Changes

- **Choose a single canonical secret model**
  - Define `SecretConfig` as the canonical config-level model for DuckDB secrets.
  - Ensure `SecretConfig`:
    - Uses a `type` discriminator (for example, `"s3"`, `"azure"`, `"gcs"`, `"http"`, `"postgres"`, `"mysql"`).
    - Exposes fields that map directly to DuckDB `CREATE SECRET` parameters for each backend.
  - Clarify in the spec that any backend-specific helper models (for example, in `secret_types.py`) are internal implementation details, not part of the public configuration surface.

- **Eliminate duplicate secret model definitions**
  - Remove any duplicated per-backend secret classes from `config.py`.
  - If backend-specific models remain useful internally, keep them only in a single module (`secret_types.py`) and make them implementation details behind `SecretConfig`.

- **Align `generate_secret_sql` with the canonical model**
  - Specify exactly how `SecretConfig` fields map to DuckDB `CREATE SECRET` parameters for each `type`.
  - Ensure the SQL generation logic:
    - Covers all documented fields.
    - Does not reference attributes that are not part of `SecretConfig`.
    - Produces the same SQL for a given `SecretConfig` instance regardless of whether backend-specific helper models exist.

- **Clarify secret documentation**
  - Update config/docs specs to:
    - Show `SecretConfig`-based examples as the primary way to configure secrets.
    - Clearly document which fields are valid for each `type`.
    - Explain `options` usage consistently across backends and references to the hardened behavior from `update-sql-quoting-and-secrets-safety`.

## Impact

- **Specs updated**
  - `specs/config/spec.md`:
    - Secret section updated to describe `SecretConfig` as the canonical schema.
    - Per-backend fields and their mapping to DuckDB `CREATE SECRET` parameters spelled out.
  - `specs/docs/spec.md` and/or secrets-related docs:
    - Examples updated to only show the canonical config model.

- **Implementation**
  - `src/duckalog/config.py`:
    - Remove any duplicate secret class definitions and rely on `SecretConfig` plus internal helpers.
  - `src/duckalog/secret_types.py`:
    - Keep or adjust backend-specific models as internal implementation helpers only, if still useful.
  - `src/duckalog/sql_generation.py`:
    - Ensure `generate_secret_sql` matches the canonical spec for all supported secret types.

- **Non-goals**
  - No new secret backends are introduced.
  - No new runtime APIs for secrets are added; this change focuses on consolidation and clarity.

## Risks and Trade-offs

- Configurations that accidentally relied on undocumented fields or on internal helper models may need adjustment once the canonical model is enforced.
- Tightening the mapping between `SecretConfig` and DuckDB `CREATE SECRET` may surface inconsistencies between earlier documentation and actual behavior; this is acceptable and should be resolved in favor of the spec.
