# Critical Security Contracts Design Spec

Converted from `.execflow/plans/refactor-critical-security-contracts/spec.md` and `.execflow/plans/refactor-critical-security-contracts/execplan.md` using the Superpowers brainstorming/spec style.

## Goal

Harden DuckDB secret SQL generation and attachment path security.

## User-visible outcome

After this change, Duckalog users can trust that configuration files cannot smuggle arbitrary SQL through secret names and cannot use attachment paths to escape the intended local root. A maintainer can see the work by running focused SQL-security and path-security tests that fail before the change and pass after it. The observable behavior is simple: malicious secret names do not execute extra statements, scoped secrets create successfully, and traversal attachment paths are rejected with the same clarity as traversal view paths.

## Current context

Duckalog reads YAML or JSON config files and generates DuckDB SQL. Secret configs are represented by Pydantic models in `src/duckalog/config/models.py` and rendered in `src/duckalog/sql_generation.py`. Path resolution currently happens mostly in `src/duckalog/config/validators.py`, delegating to `src/duckalog/config/security/path.py`. The critical review found three concrete issues: secret names are unquoted SQL identifiers, secret `scope` is appended after a semicolon where DuckDB rejects it, and attachment paths are resolved without the explicit root-boundary validation used for view URIs.

## Architecture

First, add regression tests. In `tests/test_sql_security.py`, create a DuckDB table, generate and execute a secret with a malicious name, and assert the table still exists. In `tests/test_sql_generation.py`, add a scoped secret case that asserts `SCOPE` is inside the `CREATE SECRET` option list and executes in DuckDB. In the path-security test file that already covers traversal behavior, add cases for `attachments.duckdb[].path`, `attachments.sqlite[].path`, and `attachments.duckalog[].config_path` or `database`.

Second, update `src/duckalog/sql_generation.py`. The generated secret identifier must be safe. The likely minimal fix is to pass `secret.name or secret.type` through `quote_ident()` and to render `SCOPE <literal>` as one of the options inside the parenthesized `CREATE SECRET` parameter list. Preserve existing option rendering and credential redaction behavior.

Third, update path resolution. In `src/duckalog/config/validators.py`, do not rely on `resolve_relative_path()` for security. Apply the same explicit validation used for view URIs to local attachment paths after resolution and before mutating the config object. Remote URIs must remain remote and not be forced into local-root checks.

## Files and responsibilities

- `tests/test_sql_security.py`
- `tests/test_sql_generation.py`
- `.execflow/PLANS.md`
- `src/duckalog/sql_generation.py`
- `src/duckalog/config/validators.py`
- `src/duckalog/config/security/path.py`
- `src/duckalog/sql_generation.py:242`
- `src/duckalog/sql_generation.py:277`
- `src/duckalog/config/security/path.py:237-252`
- `src/duckalog/config/models.py`
- `sql_remote_review.md`
- `config_review.md`
- `src/duckalog/sql_utils.py`

## Acceptance criteria

- AC1: Secret names are safely quoted or rejected before SQL execution, and a malicious secret name cannot execute a second statement.
- AC2: Secrets with `scope` generate valid DuckDB `CREATE SECRET` SQL and execute successfully in DuckDB.
- AC3: DuckDB, SQLite, and nested Duckalog attachment paths receive the same root-boundary security validation as view URIs.
- AC4: Regression tests fail on the current tree and pass after the change.

## Constraints

- Constraint 1: Preserve existing public config schema unless a value is demonstrably unsafe.
- Constraint 2: Do not log unredacted secret values, connection strings, or credential-bearing SQL.
- Constraint 3: Keep SQL generation pure and independently testable.

## Non-goals

- Non-goal 1: Redesign the entire secret model.
- Non-goal 2: Rewrite the import resolver or remote config loader.
- Non-goal 3: Change DuckDB credential semantics beyond producing safe SQL.

## Error handling and safety

Use the existing domain error type already used by the surrounding module. Security-sensitive paths must fail closed. CLI and dashboard tests must assert concrete error messages or event payloads instead of swallowing broad exceptions. Remote/cloud behavior must be tested with fakes or mocks, not live services.

## Testing strategy

Use TDD. First add the focused tests named in the original spec. Run them and confirm the current tree fails for the expected reason. Implement the smallest repair at the owning boundary. Then run the focused pytest command, `uv run ruff check src/duckalog tests`, and the targeted mypy command when the original spec names one.

## Implementation handoff

Implement with the paired Superpowers plan at `docs/superpowers/plans/2026-07-01-refactor-critical-security-contracts.md`. Do not start implementation from the old `.execflow` plan unless this Superpowers spec and plan are intentionally updated too.
