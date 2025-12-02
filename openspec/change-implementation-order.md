# Duckalog Change Implementation Order

This file lists a recommended implementation order for all active OpenSpec changes under `openspec/changes/`. It assumes UI work can be deferred and prioritizes security, correctness, and foundational refactors first.

## Phase 0 – Already Largely Done / Baseline

These changes are effectively in place or mostly realized in the current codebase, but should be formally confirmed and closed before starting new work:

1. `modernize-python-typing`
   - Baseline typing style (PEP 604 unions, built-in generics) is already used across core modules.
   - Action: confirm code and tests fully match the spec and then mark the change complete.

## Phase 1 – Security and Correctness Hardening (Highest Priority)

  2. `update-sql-quoting-and-secrets-safety`
   - Close remaining SQL injection vectors in view SQL, attachments, and secret SQL.
   - Dependencies: none (uses existing `sql_generation` and engine structure).

3. `update-path-security-boundaries`
   - Replace heuristic `../` counting with root-based path security so resolved paths cannot escape allowed roots.
   - Dependencies: none, but coordinates with existing path resolution behavior.

4. `refactor-secret-models-and-usage`
   - Make `SecretConfig` the canonical secret model and remove duplicated backend-specific secret classes from config.
   - Dependencies: `update-sql-quoting-and-secrets-safety` (so secret SQL is already hardened when the model is simplified).

5. `implement-secrets-creation`
   - Ensure secrets are actually created in DuckDB with `CREATE [PERSISTENT] SECRET` using `generate_secret_sql`.
   - Dependencies: `refactor-secret-models-and-usage` + `update-sql-quoting-and-secrets-safety` (to avoid implementing on top of a moving schema/SQL surface).

## PROCEED HERE ###
6. `add-security-regression-tests`
   - Add focused tests for SQL injection and path traversal based on the hardened behavior above.
   - Dependencies: `update-sql-quoting-and-secrets-safety`, `update-path-security-boundaries`, `refactor-secret-models-and-usage`, `implement-secrets-creation` (so tests target the final behavior).

7. `refactor-simplify-exceptions`
   - Introduce `DuckalogError` hierarchy and normalize error handling and logging, improving debuggability of the preceding security work.
   - Dependencies: none strict, but benefits from the security changes being in place.

## Phase 2 – API Surface and Metadata Clarity

8. `clarify-python-version-support`
   - Align `pyproject.toml`, classifiers, docs, and project conventions on the actual supported Python versions (e.g. 3.12+).
   - Dependencies: `modernize-python-typing` confirmed and closed.

9. `update-remote-config-api-contract`
   - Clarify and implement the contract for `load_config`, `_load_config_from_local_file`, and `load_config_from_uri` and their filesystem semantics.
   - Dependencies: Phase 1 security changes (to avoid reworking loader behavior later), no hard coupling to config refactors.

## Phase 3 – Config Layer Structure

10. `refactor-consolidate-config-layer`
    - Ensure the state of the config layer matches the consolidation spec (path resolution and SQL file loading behavior aligned with `config.py`).
    - Dependencies: complete Phase 1 security changes so path/SQL behavior is stable before locking in consolidation.

11. `refactor-config-package-structure`
    - Split monolithic `config.py` into a `duckalog.config` package (`models.py`, `loader.py`, `interpolation.py`, `validators.py`, `sql_integration.py`) while keeping the public API stable.
    - Dependencies: `refactor-consolidate-config-layer`, `update-remote-config-api-contract` (so we move a known-good loader contract into the new structure).

## Phase 4 – Engine and CLI Maintainability

12. `refactor-simplify-engine`
    - Introduce `CatalogBuilder` and simplify config dependency resolution (DFS-based) without changing external behavior.
    - Dependencies: Phase 1 security work and Phase 3 config refactors, so the engine wraps stable config and SQL behavior.

13. `refactor-cli-filesystem-options`
    - Consolidate duplicated filesystem options across `build`, `generate-sql`, and `validate` into a shared Typer helper.
    - Dependencies: `update-remote-config-api-contract` (clear filesystem semantics) and `refactor-simplify-engine` (ensuring CLI and engine agree on filesystem usage).

## Phase 5 – UX and Documentation Improvements

14. `add-s3-options-secrets-example`
    - Add examples demonstrating S3 secret options usage (e.g. `use_ssl`, `url_style`).
    - Dependencies: `refactor-secret-models-and-usage`, `update-sql-quoting-and-secrets-safety` (examples should reflect the canonical secret model and safe SQL).

15. `improve-secrets-options-documentation`
    - Expand documentation for secret `options` across all backends and align with the hardened behavior.
    - Dependencies: same as `add-s3-options-secrets-example`.

16. `add-config-init`
    - Implement `duckalog init` / `create_config_template()` now that the config schema and version support are clearly defined.
    - Dependencies: Phase 2 (version/typing clarified) and Phase 3 (config structure stabilized).

17. `add-duckdb-connection-api`
    - Implement the Python connection helpers (e.g. `connect_to_catalog`, `connect_and_build_catalog`) on top of the refactored engine and config loader.
    - Dependencies: `refactor-simplify-engine`, `update-remote-config-api-contract`, `clarify-python-version-support`.

## Phase 6 – UI and Dashboard (Defer Until Core Is Stable)

18. `add-dashboard-starui`
    - Implement the starui-based dashboard once core engine/config/security are stable and Python/API surface is settled.
    - Dependencies: all prior phases; especially engine refactor and remote-config contract, since the UI will sit on top of those.

