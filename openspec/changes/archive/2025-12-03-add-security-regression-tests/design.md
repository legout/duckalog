# Design: Security Regression Test Suite

## Goals

- Provide a focused set of tests that guard against regressions in security-sensitive areas:
  - SQL construction from config values (views, attachments, secrets).
  - Path resolution and traversal protection.
- Keep the test surface small and easy to understand so contributors run and extend it with confidence.

## Test structure

We group tests into two main areas:

1. **SQL security tests** (SQL injection resilience)
2. **Path security tests** (path traversal resilience)

Each area focuses on “hostile” inputs that previously exposed weaknesses.

## SQL security tests

Location: `tests/test_sql_security.py` (name illustrative; exact filename can be chosen to match existing conventions).

Key test patterns:

- **View identifier injection attempts**
  - Construct `ViewConfig` instances with names, databases, and tables that include:
    - Embedded quotes (`"`, `'`).
    - Semicolons, comments (`--`, `/* */`).
    - SQL keywords and extra tokens (`"users; DROP TABLE users; --"`).
  - Use `generate_view_sql` / `generate_all_views_sql` and assert:
    - Generated SQL is syntactically valid (at least string-level sanity checks; optional execution in DuckDB for smoke-testing).
    - The malicious content remains within quoted identifiers or literals and does not create additional statements.

- **Secret SQL generation**
  - Construct `SecretConfig` with values and options containing special characters, and assert:
    - Generated SQL includes properly quoted literals (no unescaped quotes).
    - Option keys are rendered as expected and do not break SQL.
  - Provide options with unsupported value types (for example, `{"foo": ["bar"]}`) and assert:
    - `generate_secret_sql` raises `TypeError` with a message that includes the option key and the type.

- **Dry-run parity**
  - Where dry-run APIs expose generated SQL (for example, CLI `generate-sql` or internal helpers), add tests that ensure the SQL used in dry-run and execution paths is identical for a given config.

## Path security tests

Location: `tests/test_path_security.py` or existing path-related test modules.

Key test patterns:

- **Accepted paths**
  - Paths relative to the config directory (for example, `data/users.parquet`, `./data/events.parquet`) that resolve under the config directory should be accepted and normalized correctly.

- **Rejected paths**
  - Relative paths that attempt to escape one or more levels above the config directory and then target a sibling or external directory (for example, `../../etc/passwd`, `../outside/data.parquet`).
  - Absolute paths pointing to typical system locations (for example, `/etc/passwd`, `C:\\Windows\\system32\\drivers\\etc\\hosts`) should be rejected if outside allowed roots.
  - Tests assert that the relevant API raises a configuration-level error (for example, `ConfigError` or `PathResolutionError`) and that the message is informative.

- **Cross-platform considerations**
  - Where the test environment allows, include:
    - Unix-style paths (`/var/data/file.parquet`, `../shared/file.parquet`).
    - Windows-like paths (`C:\\data\\file.parquet`, UNC paths if practical).
  - Tests should not rely on the actual existence of system directories; they can focus on the path security logic itself.

## Maintenance and evolution

- These tests are intended as regression tests: once added, they should not be removed lightly.
- When new security-relevant behavior is introduced (for example, new secret types, new attachment kinds, or new path resolution rules), contributors should:
  - Extend the existing security test modules with new cases.
  - Update the “Security Regression Tests” section in the specs to describe the new coverage.

## Relationship to other changes

- This test suite complements:
  - The SQL quoting and secret-hardening change (ensuring no regressions to injection protections).
  - The root-based path security change (ensuring no regressions to traversal protections).
- It does not replace the need for thorough functional tests or fuzzing; instead, it captures a small, high-value set of scenarios that previously caused issues and that are likely to be affected by future refactors.

