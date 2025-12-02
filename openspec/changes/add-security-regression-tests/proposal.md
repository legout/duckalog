# Change: Add Security Regression Tests for SQL and Paths

## Why

Recent reviews identified and fixed several security issues (SQL injection vectors, unsafe secret SQL generation, and weak path traversal checks). To prevent regressions and make future refactors safer, we need explicit, stable regression tests that exercise these attack surfaces.

Currently, most tests focus on nominal behavior and config correctness. We want a small, focused suite of tests that intentionally feed in “hostile” config values and assert that:

- Generated SQL remains syntactically valid and cannot be trivially broken by crafted identifiers or literals.
- Secret SQL generation correctly quotes all sensitive values and rejects unsupported option types.
- Path resolution rejects attempts to escape allowed roots and produces clear errors.

These tests should become part of the project’s standard test suite and be referenced from the specs so contributors know they must remain green when touching these areas.

## What Changes

- **Define a “security regression tests” section in specs**
  - Extend the relevant specs (config and catalog-build) with a short section describing required security-focused tests:
    - SQL injection attempts via view names, database/table identifiers, and secret values.
    - Unsafe value types passed into secret options.
    - Path traversal attempts using `..`, mixed separators, and symlinks.

- **Add targeted tests for SQL injection resilience**
  - Add tests that create `Config` / `ViewConfig` instances with database/table names containing:
    - Quotes, semicolons, comment markers, and SQL keywords.
    - Strings that would inject extra clauses if not quoted (for example, `malicious; DROP TABLE users; --`).
  - Assert that:
    - `generate_view_sql` and `generate_all_views_sql` return syntactically valid SQL.
    - The generated SQL keeps these values inside identifiers or literals and does not introduce extra statements.

- **Add tests for secret SQL generation**
  - Test `generate_secret_sql` with secrets whose values and options contain:
    - Quotes, backslashes, and other special characters.
    - Unsupported option types (for example, lists or dicts) and assert that `TypeError` is raised with a useful message.
  - Verify that dry-run paths that include secrets use the same quoting logic as the execution path.

- **Add tests for path traversal protection**
  - Add tests that:
    - Provide relative paths that resolve under the config directory and confirm they are accepted.
    - Provide relative or absolute paths that attempt to escape the allowed roots (for example, `../../etc/passwd`) and assert that a clear configuration error is raised.
  - Cover both Unix- and Windows-style path forms where feasible in the test environment.

## Impact

- **Specs updated**
  - `specs/config/spec.md` and `specs/catalog-build/spec.md` gain a “Security Regression Tests” subsection describing the intent and minimum coverage for SQL and path-related tests.

- **Implementation**
  - New tests are added under `tests/`, likely in:
    - `tests/test_sql_generation_security.py` or a similar dedicated module.
    - `tests/test_path_resolution_security.py` or added sections in existing path/config tests.
  - Existing tests for SQL generation and path resolution may be refactored slightly to share fixtures with the new regression tests.

- **Non-goals**
  - No runtime behavior changes are introduced by this change; it only codifies and tests behaviors that other changes define (for example, hardened quoting and root-based path security).
  - This change does not introduce fuzzing or property-based testing by default; it lays out a minimal but robust regression test surface.

