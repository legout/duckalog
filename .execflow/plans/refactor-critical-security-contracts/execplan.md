# Harden secret SQL generation and attachment path security

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document must be maintained in accordance with `.execflow/PLANS.md`.

## Purpose / Big Picture

After this change, Duckalog users can trust that configuration files cannot smuggle arbitrary SQL through secret names and cannot use attachment paths to escape the intended local root. A maintainer can see the work by running focused SQL-security and path-security tests that fail before the change and pass after it. The observable behavior is simple: malicious secret names do not execute extra statements, scoped secrets create successfully, and traversal attachment paths are rejected with the same clarity as traversal view paths.

## Progress

- [x] Create failing regression tests for secret-name injection, scoped-secret execution, and attachment path traversal.
- [x] Fix `src/duckalog/sql_generation.py` so generated secret SQL is safe and valid.
- [x] Fix `src/duckalog/config/validators.py` / `src/duckalog/config/security/path.py` so attachment paths are security-validated.
- [x] Run targeted and broad validation commands.

## Surprises & Discoveries

- Observation: `generate_secret_sql()` interpolates `secret.name` directly into `CREATE SECRET`.
  Evidence: `src/duckalog/sql_generation.py:242` and `src/duckalog/sql_generation.py:277` from the review.
- Observation: `resolve_relative_path()` only normalizes; it does not validate allowed roots.
  Evidence: `src/duckalog/config/security/path.py:237-252`.

## Decision Log

- Decision: Treat this as the first refactoring workstream because it addresses security and invalid SQL before structural simplification.
  Rationale: Later cleanup should not move unsafe code around before the unsafe behavior is pinned by tests.
  Date/Author: 2026-07-01 / pi

- Decision: Leave the failing `tests/test_root_based_security.py` suite for `refactor-test-dead-code-hygiene` instead of fixing it here.
  Rationale: That suite encodes an older path-security model superseded by Task 3; the new contract is verified by `tests/test_path_security.py` (21 passed). In-scope removal would expand this security plan into test-suite archaeology and risk weakening the new boundary. The hygiene plan (roadmap #6) is the designated home for superseded-test cleanup.
  Date/Author: 2026-07-01 / pi

## Outcomes & Retrospective

**Completed 2026-07-01.** All three security contracts are implemented and committed (3 commits ahead of `origin/main`):

- `9d8f826` fix: quote duckdb secret identifiers (Task 1) — secret names now pass through `quote_ident()`.
- `bc21d97` fix: render scoped secrets inside CREATE SECRET option list (Task 2) — `SCOPE <literal>` rendered within the parenthesized options.
- `6f4d253` fix: validate attachment path boundaries (Task 3) — local attachment paths now go through the same root-boundary check as view URIs.

Acceptance tests pass: `tests/test_sql_security.py` (26 passed), `tests/test_path_security.py` (21 passed).

Gap: the pre-existing `tests/test_root_based_security.py` suite (from `ecdb4dc`, an older path-security model) now reports 7 failures because it asserts the superseded contract (e.g. it expects `/etc/passwd` to be accepted). The new path model is correct and verified by `test_path_security.py`; the stale suite is left for `refactor-test-dead-code-hygiene` (roadmap #6) rather than weakening the new boundary.

Lesson: when a contract change supersedes an older test suite, the replacing plan should either delete or explicitly annotate the superseded suite in the same change, so green CI does not depend on a later cleanup plan.

## Context and Orientation

Duckalog reads YAML or JSON config files and generates DuckDB SQL. Secret configs are represented by Pydantic models in `src/duckalog/config/models.py` and rendered in `src/duckalog/sql_generation.py`. Path resolution currently happens mostly in `src/duckalog/config/validators.py`, delegating to `src/duckalog/config/security/path.py`. The critical review found three concrete issues: secret names are unquoted SQL identifiers, secret `scope` is appended after a semicolon where DuckDB rejects it, and attachment paths are resolved without the explicit root-boundary validation used for view URIs.

## Plan of Work

First, add regression tests. In `tests/test_sql_security.py`, create a DuckDB table, generate and execute a secret with a malicious name, and assert the table still exists. In `tests/test_sql_generation.py`, add a scoped secret case that asserts `SCOPE` is inside the `CREATE SECRET` option list and executes in DuckDB. In the path-security test file that already covers traversal behavior, add cases for `attachments.duckdb[].path`, `attachments.sqlite[].path`, and `attachments.duckalog[].config_path` or `database`.

Second, update `src/duckalog/sql_generation.py`. The generated secret identifier must be safe. The likely minimal fix is to pass `secret.name or secret.type` through `quote_ident()` and to render `SCOPE <literal>` as one of the options inside the parenthesized `CREATE SECRET` parameter list. Preserve existing option rendering and credential redaction behavior.

Third, update path resolution. In `src/duckalog/config/validators.py`, do not rely on `resolve_relative_path()` for security. Apply the same explicit validation used for view URIs to local attachment paths after resolution and before mutating the config object. Remote URIs must remain remote and not be forced into local-root checks.

## Concrete Steps

Run from `/Users/volker/coding/libs/duckalog`.

1. Add tests and confirm they fail on the current tree:

    uv run pytest tests/test_sql_security.py tests/test_sql_generation.py tests/test_path_security.py -q

2. Implement the SQL and path fixes in the files named above.

3. Re-run focused tests:

    uv run pytest tests/test_sql_security.py tests/test_sql_generation.py tests/test_path_security.py tests/test_root_based_security.py -q

4. Run broad lightweight validation:

    uv run ruff check src/duckalog tests
    uv run mypy src/duckalog/sql_generation.py src/duckalog/config/validators.py src/duckalog/config/security/path.py

## Validation and Acceptance

Acceptance requires all focused tests above to pass. The malicious-secret regression must prove that a table created before executing generated secret SQL still exists afterward. The scoped-secret regression must execute the generated SQL in DuckDB without `ParserException`. The attachment traversal regression must fail before implementation and pass afterward by raising the existing config/path security error.

## Idempotence and Recovery

The work is safe to retry because it only changes pure SQL rendering and config validation. If a broader test suite exposes compatibility concerns around unusual secret names, prefer adding compatibility tests and narrowing validation rather than loosening SQL escaping.

## Artifacts and Notes

Source findings came from `sql_remote_review.md`, `config_review.md`, and the synthesized review summary in the current session.

## Interfaces and Dependencies

Use existing helpers from `src/duckalog/sql_utils.py`: `quote_ident()` for identifiers and `quote_literal()` for string values. Do not introduce new runtime dependencies. Keep public function names stable: `duckalog.sql_generation.generate_secret_sql()` remains the central rendering function.
