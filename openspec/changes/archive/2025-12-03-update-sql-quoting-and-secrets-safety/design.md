# Design: SQL Quoting and Secret SQL Generation

## Goals

- Provide a small, well-defined API for constructing SQL safely from configuration data.
- Eliminate remaining SQL injection vectors in view SQL, attachment SQL, and secret SQL.
- Make it obvious to contributors how to construct SQL from config values without re-inventing quoting.

## Canonical SQL helpers

We define two core functions as the canonical building blocks for SQL construction:

```python
def quote_ident(identifier: str) -> str:
    """Quote a SQL identifier using double quotes."""

def quote_literal(value: str) -> str:
    """Quote a SQL string literal using single quotes."""
```

Key design points:

- Both helpers return fully-quoted values. Callers must pass raw strings and MUST NOT add their own quotes.
- Escaping rules:
  - `quote_ident` doubles any embedded `"` characters (`"foo""bar"`).
  - `quote_literal` doubles any embedded `'` characters (`'foo''bar'`).
- `normalize_path_for_sql` should focus on path normalization (via `pathlib.Path`) and then delegate to `quote_literal` to handle quoting, rather than implementing its own quoting rules.

Location:

- We keep the canonical helpers in `sql_generation.py` (where they already exist) or move them into a small `sql_utils.py` module under `duckalog` and re-export them from `sql_generation.py` for backwards compatibility.
- Path-related helpers in `path_resolution.py` call into these helpers instead of duplicating quoting logic.

## Applying quoting consistently

### View SQL

For `ViewConfig` with `source in {"duckdb", "sqlite", "postgres"}`:

- Instead of interpolating `view.database` and `view.table` directly into the SQL, we build:

```sql
SELECT * FROM {quote_ident(view.database)}.{quote_ident(view.table)}
```

- This ensures that:
  - Identifiers containing spaces, reserved words, or special characters still work.
  - Arbitrary SQL fragments embedded in `database` or `table` values cannot break out of the identifier context.

### Attachments and catalogs

In `engine.py`, any SQL that builds `ATTACH DATABASE` or similar statements MUST:

- Pass database aliases and catalog identifiers through `quote_ident`.
- Pass database paths and other string literals through either `quote_literal` or `normalize_path_for_sql` (which, in turn, uses `quote_literal`).

The design goal is that no configuration-derived identifier or string literal should appear in SQL without going through one of these helpers.

## Secret SQL generation

The `generate_secret_sql(secret: SecretConfig) -> str` function is responsible for generating `CREATE [PERSISTENT] SECRET` statements that DuckDB will execute.

Design rules:

- String-valued fields (for example, `key_id`, `secret`, `connection_string`, `host`, `database`, `user`, `password`, `scope`, `endpoint`, `region`) MUST use `quote_literal`.
- Numeric fields (`port`, numeric tunables) are emitted as-is (no quotes).
- Boolean-like fields are emitted as `TRUE` / `FALSE`.
- `secret.options`:
  - Allowed value types: `bool`, `int`, `float`, `str`.
  - Unsupported value types cause a `TypeError` with a clear message including the option key and type.
  - String values use `quote_literal`; numeric/boolean values follow the rules above.

Option keys:

- The spec will state that option keys are treated as identifiers/keywords and are uppercased in the emitted SQL (for example, `use_ssl` → `USE_SSL`).
- Option keys are expected to be simple alphanumeric/underscore names; if we later need to add validation, this can be layered on top.

## Dry-run behavior

Dry-run modes (for example, SQL generation commands or `include_secrets=True` in `generate_all_views_sql`) MUST:

- Produce the exact same `CREATE SECRET` statements that would be executed in a real build.
- Use the same quoting helpers (`quote_ident`, `quote_literal`) and option rendering logic as the engine path.

This ensures that users can inspect the generated SQL and reason about safety without worrying about discrepancies between dry-run and execution.

## Backward compatibility

- Configurations that already use only `bool`, `int`, `float`, and `str` for secret options will continue to work as before, with improved safety.
- Configurations that relied on unsupported types in `secret.options` will start raising `TypeError`. This is an intentional tightening to avoid unsafe SQL interpolation.
- The surface of the public Python API does not change; implementations become stricter and safer.

