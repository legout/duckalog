# Change: Harden SQL Quoting and Secret SQL Generation

## Why

Recent consolidated reviews identified remaining SQL injection risks and inconsistent secret handling in Duckalog:

- `generate_view_sql` still emits unquoted identifiers for some sources (`duckdb`, `sqlite`, `postgres`), allowing crafted database/table names to break SQL or inject arbitrary statements.
- `generate_secret_sql` interpolates sensitive fields (keys, secrets, connection strings, hosts, databases, etc.) directly into SQL using inline single quotes, and its `options` handling previously relied on unsafe fallbacks for unsupported types.
- SQL and quoting helpers (`quote_ident`, `_quote_literal`, `normalize_path_for_sql`) are spread across multiple modules without a clearly defined, canonical API, increasing the risk that new code bypasses the safe helpers.

Duckalog is intended for use in serious data platforms where configuration may be partially untrusted (or shared between teams). We need a clear specification for safe SQL construction and secret SQL generation, and we need the implementation to match it.

This change builds on archived change `2025-12-02-implement-secrets-creation`, which introduced `generate_secret_sql` and actual `CREATE SECRET` execution; it hardens that behavior and makes the SQL construction rules explicit.

## What Changes

- **Define a canonical SQL quoting surface**
  - Specify a small set of helpers as the single source of truth for SQL construction:
    - `quote_ident(identifier: str) -> str` for identifiers (views, schemas, databases, tables, aliases).
    - `quote_literal(value: str) -> str` for string literals (paths, keys, secrets, connection strings).
  - Clarify behavior:
    - Escaping rules (double quotes inside identifiers, single quotes inside literals).
    - That callers must never add their own surrounding quotes when using these helpers.
  - Specify how `normalize_path_for_sql` relates to `quote_literal` (for example, using `Path` normalization followed by literal quoting under the hood).

- **Apply identifier quoting consistently**
  - Update the catalog-build spec to require that any database, schema, table, view, or alias that originates from configuration MUST be passed through `quote_ident` (or an equivalent safe helper), including:
    - `generate_view_sql` for `duckdb` / `sqlite` / `postgres` sources.
    - Attachment aliases and any catalog identifiers in `engine.py`.
  - Document how non-identifier, trusted fragments (for example, hard-coded SQL keywords) are handled, and that user-provided fragments MUST NOT be concatenated into those contexts without going through safe helpers.

- **Harden `generate_secret_sql`**
  - Specify that all string values in `CREATE SECRET` parameters (including `key_id`, `secret`, `connection_string`, `host`, `database`, `user`, `password`, scope, and related fields) MUST be emitted using `quote_literal`.
  - Define the allowed types for `SecretConfig.options` values in the spec:
    - Allowed: `bool`, `int`, `float`, `str`.
    - For any other type, the implementation MUST raise `TypeError` (rather than trying to interpolate a string representation).
  - Clarify that options keys are treated as identifiers or keywords (depending on DuckDB’s syntax) and must be uppercased and/or validated, but MUST NOT be taken from untrusted input without validation.

- **Clarify dry-run behavior**
  - Update catalog-build spec so that `include_secrets=True` in SQL generation and dry-run modes produces the same `CREATE SECRET` SQL that will be executed in real builds, with identical quoting semantics.

## Impact

- **Specs updated**
  - `specs/catalog-build/spec.md`:
    - Add or modify requirements describing safe SQL construction for views, attachments, and secrets.
    - Define the required use of `quote_ident` / `quote_literal` (or equivalents) for all configuration-derived identifiers and string literals.
  - `specs/config/spec.md`:
    - Clarify `SecretConfig` option types and how they are rendered into SQL.
    - Document the constraints on secret names, scope, and option keys.
- **Implementation**
  - `src/duckalog/sql_generation.py`: centralize quoting helpers and update `generate_view_sql`, `generate_secret_sql`, and any helper that builds SQL fragments.
  - `src/duckalog/path_resolution.py`: ensure any path-to-SQL helper (`normalize_path_for_sql`) composes with the canonical quoting helpers instead of reimplementing them.
  - `src/duckalog/engine.py`: use `quote_ident` for aliases and catalog identifiers when constructing SQL strings.
- **Non-goals**
  - No new UI, servers, or HTTP interfaces are introduced or changed.
  - No changes to the public Python API signatures (only stricter behavior and clearer guarantees around SQL construction).

## Risks and Trade-offs

- Stricter enforcement of option types for secrets could surface `TypeError` in configurations that previously “worked by accident” with unsafe interpolation. The change is intentionally conservative and improves safety, but we should call it out in the changelog.
- Centralizing quoting may require adjusting a few internal call sites, but this reduces long-term risk and complexity.
