# Simplification & Refactoring: Remove Dead Code, Consolidate Duplication, Shrink the Codebase

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document must be maintained in accordance with `.ticket-flow/PLANS.md`.

## Purpose / Big Picture

Duckalog's codebase has accumulated dead code and duplication from a major refactoring that migrated config loading from a single `config/loader.py` into a structured `config/` subpackage. The old module was left in place with a deprecation warning but never removed. Several thin wrapper modules, duplicated utility functions, and deprecated public APIs remain, adding cognitive load for contributors and confusion for users about which API path is canonical.

After this work, a contributor reading the source tree will find one clear loading path (`config/api.py` → `config/resolution/imports.py`), one canonical `_is_remote_uri` helper, and a single blessed Python/CLI workflow. The codebase shrinks by roughly 2,550 lines (~20%) with zero behavioral change for non-deprecated APIs. The deprecated `build_catalog()` function and `build` CLI command are removed, completing a deprecation cycle that was started but never finished.

## Progress

- [ ] Milestone 1: Delete deprecated config/loader.py and update its sole remaining consumer (CLI show-imports)
- [ ] Milestone 2: Delete dead stub files and deprecated re-export modules (logging_utils.py, interpolation.py, secret_types.py, loading/file.py, loading/remote.py, unused ABCs in loading/base.py, old dist/ artifacts)
- [ ] Milestone 3: Consolidate duplicated _is_remote_uri into one canonical location and update all importers
- [ ] Milestone 4: Remove deprecated public API surface (build_catalog, connect_and_build_catalog, build CLI command, _load_config_from_local_file)
- [ ] Milestone 5: Merge overlapping CLI commands (show-paths + validate-paths) and remove the init-env command

## Surprises & Discoveries

(To be filled during implementation.)

## Decision Log

- Decision: Execute removals in dependency order — delete the largest dead module first (loader.py), then stubs, then consolidation, then deprecated API surface, then CLI cleanup.
  Rationale: Removing the biggest dead weight first makes every subsequent step easier to reason about (fewer files to grep, fewer import paths to trace).
  Date: 2026-04-14

- Decision: Keep `config/loading/sql.py` in place (it has real logic and real consumers: `remote_config.py`, `config/resolution/imports.py`, `config/interpolation.py`). Only delete the empty stubs around it and the unused ABC classes in `loading/base.py`.
  Rationale: Moving `sql.py` would touch too many import paths for no complexity reduction — the module is already focused and self-contained.
  Date: 2026-04-14

- Decision: Remove `build_catalog()` from the public API but keep the function in `engine.py` as an internal helper without renaming it. The plan excludes `src/duckalog/dashboard/`, so the safest simplification is to stop exporting the function rather than forcing downstream import changes outside the plan's scope.
  Rationale: The function itself is useful internally; only the public export and the deprecation noise should go, and renaming it would create avoidable change amplification outside the scope of this plan.
  Date: 2026-04-14

- Decision: Remove the `build` CLI command entirely rather than keeping it with a deprecation warning. The `run` command has been the recommended path and supports all `build` functionality.
  Rationale: Keeping deprecated CLI commands indefinitely adds cognitive load without helping users. A clean break is simpler.
  Date: 2026-04-14

## Outcomes & Retrospective

(To be filled after completion.)

## Context and Orientation

Duckalog is a Python library and CLI (`duckalog`) for building DuckDB catalogs from declarative YAML/JSON configs. It lives in `src/duckalog/`. The dashboard subpackage (`src/duckalog/dashboard/`) is excluded from this plan.

Key modules and their roles:

- `config/models.py` — Pydantic models for the config schema (Config, ViewConfig, SecretConfig, etc.)
- `config/api.py` — Current public entry point for `load_config()`. Delegates to `config/resolution/imports.py`.
- `config/loader.py` — **Deprecated predecessor** to `api.py`. 1,569 lines. Has a module-level deprecation warning. Only consumed by CLI's `show-imports` command (which uses three private helpers).
- `config/resolution/imports.py` — Current import-chain resolver. Where the real loading logic lives.
- `config/resolution/env.py` — `.env` file discovery and `${env:VAR}` interpolation.
- `config/security/path.py` — Root-based path security (traversal prevention).
- `config/validators.py` — A delegation layer: 9 path functions wrap `security/path.py`, plus 4 logging functions and `_resolve_paths_in_config`.
- `config/loading/` — A subpackage with one real file (`sql.py`), two empty stubs (`file.py`, `remote.py`), and unused abstract base classes (`base.py`).
- `config/interpolation.py` — Deprecated proxy for legacy env interpolation and SQL-file loading APIs. Only used by deprecation-warning tests; no production code imports it.
- `config/__init__.py` — Re-exports public API surface. Contains `_call_with_monkeypatched_callable` (a test helper) and re-exports deprecated `_load_config_from_local_file`.
- `engine.py` — Catalog builder. Contains deprecated `build_catalog()` and `CatalogBuilder`.
- `python_api.py` — High-level Python API. Contains deprecated `connect_and_build_catalog()`.
- `cli.py` — Typer CLI (~2,000 lines). Commands `build` (deprecated), `run` (canonical), `show-imports` (uses private loader helpers), `show-paths`, `validate-paths`, `init-env`, and others.
- `logging_utils.py` — 9-line re-export shim that just re-exports from `config/validators.py`.
- `secret_types.py` — 61 lines of backend-specific secret models superseded by `SecretConfig` in `models.py`. Zero importers.
- `remote_config.py` — Remote config loading via fsspec. Imports from `logging_utils.py` and `config/loading/sql.py`.
- `sql_file_loader.py` — The real `SQLFileLoader` class. Imports from `logging_utils.py`.
- `config_init.py` — Template generator for `duckalog init`. Imports from `logging_utils.py`.

The `_is_remote_uri` helper is independently defined in four locations:
  1. `remote_config.py` line 70 — `is_remote_uri()` (public, canonical)
  2. `config/resolution/imports.py` line 104 — `_is_remote_uri()` (private copy)
  3. `config/resolution/env.py` line 96 — `_is_remote_uri()` (private copy)
  4. `config/loading/sql.py` line 46 — `_is_remote_uri()` (private copy)

## Plan of Work

### Milestone 1: Delete deprecated config/loader.py

This is a cleanup milestone. It removes the single largest block of dead code.

The file `src/duckalog/config/loader.py` (1,569 lines) was superseded by `config/api.py` and `config/resolution/imports.py` during a prior refactoring. It has a module-level `DeprecationWarning` and is only imported by one production path in the CLI (`show-imports`) plus one test file (`tests/test_deprecation_warnings.py`) that explicitly checks the warning behavior.

The CLI's `show-imports` command (`src/duckalog/cli.py` around line 977 and line 1294) imports three private helpers from `config.loader`:

    from .config.loader import (
        _is_remote_uri,
        _normalize_uri,
        _resolve_import_path,
    )

All three helpers also exist in `config/resolution/imports.py` under the same names. The import in `cli.py` must be updated to point there before the file can be deleted.

Steps:

1. In `src/duckalog/cli.py`, find the two `from .config.loader import` statements (around lines 977 and 1294) and change them to `from .config.resolution.imports import`. The three functions (`_is_remote_uri`, `_normalize_uri`, `_resolve_import_path`) exist at the same names in that module.

2. Delete `src/duckalog/config/loader.py`.

3. Run the test suite subset:
       uv run pytest tests/test_config.py tests/test_config_imports.py tests/test_engine_cli.py tests/test_cli_remote.py tests/test_cli_filesystem.py -q

After this milestone, `config/loader.py` is gone and the CLI's `show-imports` command still works by importing from the canonical resolution module.

Prerequisites: None. This is a safe starting point.

Conflict boundary: `config/loader.py` is a standalone file with no dependents beyond the CLI import being redirected.

### Milestone 2: Delete dead stubs and deprecated re-export modules

This is a cleanup milestone. It removes files that contain zero meaningful logic.

Files to delete:

- `src/duckalog/logging_utils.py` (9 lines) — A pure re-export shim:
      from .config.validators import get_logger, log_info, log_debug, log_error
  Three files import from it. Update each to import directly from `config.validators`:
  - `src/duckalog/config_init.py` line 12: change `from .logging_utils import log_info` to `from .config.validators import log_info`
  - `src/duckalog/sql_file_loader.py` line 18: change `from .logging_utils import log_debug, log_info` to `from .config.validators import log_debug, log_info`
  - `src/duckalog/remote_config.py` line 15: change `from .logging_utils import log_debug, log_info` to `from .config.validators import log_debug, log_info`

- `src/duckalog/config/interpolation.py` (41 lines) — Deprecated proxy module for legacy env interpolation and SQL-file loading. It has no production importers; only `tests/test_deprecation_warnings.py` reloads it to assert that the deprecation warning fires. Delete the module and remove or rewrite the corresponding warning test.

- `src/duckalog/secret_types.py` (61 lines) — Backend-specific secret models superseded by `SecretConfig`. Zero importers in `src/`. Safe to delete outright.

- `src/duckalog/config/loading/file.py` (0 lines) — Completely empty.

- `src/duckalog/config/loading/remote.py` (0 lines) — Completely empty.

- `src/duckalog/config/loading/base.py` (23 lines) — Contains two abstract base classes (`ConfigLoader`, `SQLFileLoader`) that are never used outside `config/loading/__init__.py`. Delete this file and update `config/loading/__init__.py` to stop importing from it.

- `src/duckalog/config/loading/__init__.py` — After deleting `base.py`, simplify this to:
      from .sql import load_sql_files_from_config
      __all__ = ["load_sql_files_from_config"]

- `dist/duckalog-0.1.0-py3-none-any.whl` and `dist/duckalog-0.1.0.tar.gz` — Ancient build artifacts from version 0.1.0. Delete both.

Also remove `_call_with_monkeypatched_callable` from `src/duckalog/config/__init__.py`. This function (around line 84) was a test helper that only existed to support monkeypatched mock callables. With `config/loader.py` gone, it has no remaining callers. The function body at `config/loader.py` line 49 will already be deleted; remove the identical copy in `__init__.py`.

Steps:

1. Update the three `logging_utils` importers listed above.
2. Delete `logging_utils.py`.
3. Delete `secret_types.py`.
4. Delete `config/loading/file.py` and `config/loading/remote.py`.
5. Delete `config/loading/base.py` and simplify `config/loading/__init__.py`.
6. Delete `dist/duckalog-0.1.0*`.
7. Remove `_call_with_monkeypatched_callable` from `config/__init__.py` (the function definition around line 84).
8. Run tests:
       uv run pytest tests/test_config.py tests/test_sql_file_loading.py tests/test_remote_config.py tests/test_sql_generation.py -q

   This subset intentionally omits `tests/test_deprecation_warnings.py`, because that file still references the deleted proxy modules until Milestone 4 rewrites it.

Prerequisites: Milestone 1 (ensures `config/loader.py` is already gone so `_call_with_monkeypatched_callable` has no remaining copy).

Related non-blocking: Milestone 3 can proceed in parallel since it touches different files.

### Milestone 3: Consolidate _is_remote_uri into one canonical location

This is a cleanup milestone. It removes a concept that was duplicated four times.

Today `_is_remote_uri` is independently defined in four files. The canonical public version lives in `remote_config.py` as `is_remote_uri()`. All three private copies should import from there.

Steps:

1. In `src/duckalog/config/resolution/imports.py`, remove the local `_is_remote_uri` function definition (lines 104-119). This function wraps `remote_config.is_remote_uri` with a try/except fallback to a hardcoded scheme list. Replace with a top-level import — the file already has `from duckalog.remote_config import is_remote_uri as check_remote_uri` inside `_normalize_import_path` at line 216; consolidate into one top-level import:
       from duckalog.remote_config import is_remote_uri as _is_remote_uri
   Also update the existing `check_remote_uri` reference at line 216 to use `_is_remote_uri` instead, or remove that local import.

2. In `src/duckalog/config/resolution/env.py`, remove the local `_is_remote_uri` function definition (lines 96-113). This has the same try/except-fallback pattern. Replace with a top-level import:
       from duckalog.remote_config import is_remote_uri as _is_remote_uri

3. In `src/duckalog/config/loading/sql.py`, note that `_is_remote_uri` is a **nested function inside `process_sql_file_references()`** (starting at line 46), not a module-level definition. Remove the nested function (lines 46-60) and add a module-level import near the other top-level imports:
       from duckalog.remote_config import is_remote_uri as _is_remote_uri
   The nested function uses `urlparse`+`startswith` on a hardcoded scheme list. The canonical `remote_config.is_remote_uri` uses the same `urlparse` approach with a more complete scheme map, so behavior is equivalent or improved. Verify the two callers inside `process_sql_file_references` (around lines 83 and 135) resolve `_is_remote_uri` correctly as a module-level name.

4. In `src/duckalog/config/api.py`, the line:
       from .resolution.imports import _is_remote_uri
   can stay as-is since it now transitively points to the canonical version. Alternatively, update it to import directly from `remote_config` — either is fine.

5. Run tests:
       uv run pytest tests/test_config.py tests/test_config_imports.py tests/test_remote_config.py tests/test_path_resolution.py -q

Prerequisites: None. This can proceed in parallel with Milestone 2.

Conflict boundary: The three files being changed are all in the config resolution chain. Do not modify them concurrently with other milestones that touch the same files.

### Milestone 4: Remove deprecated public API surface

This is a vertical milestone. It completes the deprecation cycle by removing the old `build` workflow and the deprecated Python API functions, leaving `duckalog run` and `connect_to_catalog()` as the single blessed path.

What changes:

1. In `src/duckalog/python_api.py`:
   - Delete the `connect_and_build_catalog()` function (lines ~150–220).
   - Remove it from `__all__`.
   - Remove the now-unused `from .engine import build_catalog` import at line 12.

2. In `src/duckalog/engine.py`:
   - Remove the deprecation warning from `build_catalog()` (the `warnings.warn(...)` block around line 603).
   - Keep `build_catalog()` in place as an internal helper for `duckalog run --dry-run` and other internal callers. Do **not** rename it, because this plan explicitly excludes `src/duckalog/dashboard/` and we are not changing downstream import sites outside this plan.
   - Remove `build_catalog` from `__all__` at the bottom of the file (line ~1040) so it is no longer a public export of the `engine` module.
   - Update the docstring examples inside `build_catalog()` that show `from duckalog import build_catalog` — change them to `from duckalog.engine import build_catalog` or remove the examples entirely, since the function is no longer a public API.

3. In `src/duckalog/__init__.py`:
   - Remove `build_catalog` and `connect_and_build_catalog` from imports and `__all__`.
   - The public API now exports only `connect_to_catalog`, `connect_to_catalog_cm`, `generate_sql`, `validate_config`, and the config/SQL utility surface.

4. In `src/duckalog/config/api.py`:
   - Delete the deprecated `_load_config_from_local_file()` function (lines ~60–79).
   - Rename `_load_config_from_local_file_impl` to `_load_config_from_local_file` so the canonical internal name is simpler and the deprecated wrapper is gone.
   - Remove `_load_config_from_local_file` from `__all__`.
   - Update `config/__init__.py` to import the renamed internal function instead of the deprecated wrapper.

5. In `src/duckalog/cli.py`:
   - Delete the entire `build` command function and its `@app.command(...)` decorator (roughly lines 370–530).
   - Remove the `_interactive_loop` helper's reference to `build_catalog` — it only uses `connect_to_catalog`, which is fine.
   - In the `run` command, keep the existing `build_catalog(...)` dry-run call; after Milestone 4 it is no longer exported publicly, but the internal helper still exists.
   - Remove the `--use-connection` flag from any remaining code.

6. Update surviving tests that import `build_catalog` from the public API (`duckalog`) so they import from `duckalog.engine` instead:
   - `tests/test_engine_cli.py` line 15: change `from duckalog import (... build_catalog, ...)` to `from duckalog.engine import build_catalog`
   - `tests/test_connection_api.py` lines 54, 111, 169, 190: change the local `from duckalog import build_catalog` lines to `from duckalog.engine import build_catalog`

7. Delete tests that exclusively cover removed deprecations or public compatibility shims:
   - `tests/test_connection_api.py` — remove `TestConnectAndBuildCatalog` class (lines 230–366)
   - `tests/test_engine_cli.py` — remove tests that exercise the CLI `build` command (`test_cli_build_reports_engine_error` at line 286, `test_cli_build_dry_run_outputs_sql` at line 311)
   - `tests/test_deprecation_warnings.py` — remove the `loader` and `interpolation` warning checks, and keep only warnings that still correspond to surviving deprecated surfaces during this change

Steps:

1. Keep `build_catalog()` in `src/duckalog/engine.py` as an internal helper. Remove only its deprecation warning, its `__all__` entry, and fix its docstring examples.
2. Update `src/duckalog/__init__.py` to remove `build_catalog` and `connect_and_build_catalog` from imports and `__all__`.
3. Delete `connect_and_build_catalog` from `python_api.py`, remove it from `__all__`, and remove the now-unused `from .engine import build_catalog` import.
4. In `config/api.py`, delete `_load_config_from_local_file()`, rename `_load_config_from_local_file_impl` to `_load_config_from_local_file`, and update `config/__init__.py` to import the renamed function.
5. Delete the `build` CLI command from `cli.py`.
6. Update surviving tests that imported `build_catalog` from `duckalog` to import from `duckalog.engine` instead.
7. Delete or rewrite the deprecated-coverage tests listed above.
8. Run tests:
       uv run pytest tests/test_connection_api.py tests/test_engine_cli.py tests/test_deprecation_warnings.py tests/test_cli_query.py tests/test_cli_filesystem.py -q

Prerequisites: Milestone 1 (loader.py deleted), Milestone 2 (logging_utils/interpolation/dead stubs deleted), and Milestone 3 (duplicate URI helper consolidation) should be complete before this milestone so the public API surface changes land on a cleaner base.

Conflict boundary: `__init__.py` is the public API surface — only one milestone should modify it at a time. `cli.py` is large and shared — serialize changes to it.

Serialization point: This milestone removes exports from `__init__.py`. No other milestone should touch `__init__.py` concurrently.

### Milestone 5: Merge overlapping CLI commands and remove init-env

This is a vertical milestone. It simplifies the CLI surface that users see.

What changes:

1. Merge `show-paths` and `validate-paths` into a single `show-paths` command. The `validate-paths` command is essentially `show-paths --check` plus config validation. The merged command should:
   - Always validate the config first (like `validate-paths` did)
   - Show resolved paths (like `show-paths` did)
   - Accept a `--check` flag for accessibility checking (like `show-paths --check`)
   - Remove the `validate-paths` command registration

2. Remove the `init-env` command. This ~150-line command generates static `.env` template strings inline — it is not core catalog functionality. Users can create `.env` files themselves or use any template system. Delete the entire `init_env` function and its `@app.command(...)` decorator from `cli.py`.

3. Remove the `--use-connection` flag from any remaining references (should already be gone after Milestone 4, but double-check).

4. Update tests:
   - Merge/adjust tests for `show-paths` and `validate-paths` into a single test class
   - Delete any `init-env` tests (if they exist in `tests/test_cli_filesystem.py` or similar)
   - Update `tests/test_cli_remote.py` so its remote-URI assertions reflect the merged `show-paths --check` behavior and the removal of `validate-paths`

Steps:

1. In `cli.py`, modify the `show_paths` command to include the `--check` flag behavior from `validate_paths`. Add config validation at the top (load config, raise on error). Delete the `validate_paths` command function.

2. Delete the `init_env` command function and all its inline template strings.

3. Update `examples/README.md` if it references `validate-paths` or `init-env` commands.

4. Run tests:
       uv run pytest tests/test_cli_filesystem.py tests/test_cli_query.py tests/test_cli_remote.py -q

Prerequisites: Milestone 4 (build command removed, CLI already partially simplified).

Conflict boundary: `cli.py` is the sole file being modified. Serialize with any other CLI changes.

## Concrete Steps

All commands run from the repository root (`duckalog/`).

After each milestone, run the relevant test subset listed in that milestone's validation section. The full test command for a final check:

    uv run pytest tests/ -q --ignore=tests/test_dashboard.py --ignore=tests/test_dependency_injection_filesystems.py --ignore=tests/test_engine_hierarchical.py

The three ignored test files require optional dependencies (`litestar`, `fsspec`) that are not installed in the default dev environment. They should be run separately in an environment with `pip install duckalog[ui,remote]`.

## Validation and Acceptance

The overall acceptance criteria for this plan:

1. The deprecated `config/loader.py` no longer exists.
2. The files `logging_utils.py`, `config/interpolation.py`, `secret_types.py`, `config/loading/file.py`, `config/loading/remote.py`, and `dist/duckalog-0.1.0*` no longer exist.
3. `_is_remote_uri` has exactly one implementation source path, and all internal callers import from the canonical remote-URI helper instead of maintaining their own copies.
4. `build_catalog` and `connect_and_build_catalog` are not exported from `__init__.py`.
5. The `build` CLI command does not exist. Running `duckalog --help` lists `run` but not `build`.
6. The `validate-paths` and `init-env` CLI commands do not exist. `show-paths --check` provides the combined functionality.
7. Running `duckalog run <config.yaml>` on a valid config produces the same behavior as before, including `--dry-run` output.
8. Running `duckalog validate <config.yaml>` on a valid config prints "Config is valid."
9. `tests/test_deprecation_warnings.py` no longer relies on deleted modules such as `duckalog.config.loader` or `duckalog.config.interpolation`; it only covers surviving deprecation behavior, if any remains.
10. Running `uv run pytest tests/ -q --ignore=...` (excluding dashboard/optional-dep tests) passes with 0 failures.
11. The line count of `src/duckalog/` (excluding `dashboard/`) has decreased by approximately 2,500 lines compared to the starting state.

To verify #10, run before and after:

    find src/duckalog -name '*.py' ! -path '*/dashboard/*' -exec cat {} + | wc -l

## Idempotence and Recovery

All changes in this plan are deletions and import-path redirects. If a milestone fails partway:

- The file deletions are atomic (delete or keep).
- The import redirects can be verified by running the test suite immediately after.
- No database migrations, no config schema changes, no runtime state changes.
- If needed, any deleted file can be restored from git: `git checkout HEAD -- <path>`.

## Artifacts and Notes

Starting line counts for verification (Python files in `src/duckalog/`, excluding `dashboard/`):

    cli.py                    2002 lines
    config/loader.py          1569 lines
    config/resolution/imports.py 1052 lines
    engine.py                 1040 lines
    config/models.py          1081 lines
    python_api.py              242 lines
    remote_config.py           467 lines
    config/validators.py       353 lines
    config_init.py             229 lines
    config/interpolation.py     41 lines
    config/loading/sql.py      265 lines
    sql_file_loader.py         191 lines
    sql_generation.py          269 lines
    connection.py              350 lines
    config/security/path.py    460 lines
    config/resolution/env.py   379 lines
    logging_utils.py             9 lines
    secret_types.py             61 lines
    config/loading/base.py      23 lines
    config/loading/file.py       0 lines
    config/loading/remote.py     0 lines
    Total (src/duckalog excluding dashboard): 11320 lines

Expected deletions by milestone:
- Milestone 1: ~1,569 lines (loader.py)
- Milestone 2: ~134 lines (logging_utils, interpolation, secret_types, stubs, base.py, _call_with_monkeypatched_callable) + dist artifacts
- Milestone 3: ~60 lines (3 duplicate _is_remote_uri definitions, replaced by imports)
- Milestone 4: ~200 lines (deprecated functions + build command + associated tests)
- Milestone 5: ~300 lines (init-env command + validate-paths command + tests)
- Total: ~2,260 lines removed from source; ~350 lines from deleted tests

## Interfaces and Dependencies

No new interfaces are introduced. The following interfaces are removed:

- Public function: `build_catalog(config_path, ...)` — removed from `__init__.py` exports, but the internal helper remains in `engine.py` for `duckalog run --dry-run` and other internal callers.
- Public function: `connect_and_build_catalog(...)` — removed entirely from `python_api.py`.
- CLI command: `duckalog build` — removed from `cli.py`.
- CLI command: `duckalog validate-paths` — merged into `duckalog show-paths --check`.
- CLI command: `duckalog init-env` — removed from `cli.py`.
- Module: `duckalog.config.loader` — deleted entirely.
- Module: `duckalog.config.interpolation` — deleted entirely.
- Module: `duckalog.logging_utils` — deleted; importers use `duckalog.config.validators` directly.
- Module: `duckalog.secret_types` — deleted; superseded by `duckalog.config.models.SecretConfig`.

The stable interfaces that must not change:

- `duckalog.config.load_config(path, ...)` — canonical config loading entry point.
- `duckalog.connect_to_catalog(config_path, ...)` — canonical connection management.
- `duckalog.run` CLI command — canonical CLI workflow.
- `duckalog validate` CLI command — config validation.
- `duckalog generate-sql` CLI command — SQL generation.
- `duckalog query` CLI command — ad-hoc SQL execution.
- All Pydantic models in `config/models.py`.
- All SQL generation functions in `sql_generation.py` and `sql_utils.py`.

Revision note (2026-04-14): This pass tightened the plan around code that actually exists today. It added `config/interpolation.py` and `tests/test_deprecation_warnings.py` to the dead-code cleanup, corrected the plan to keep `build_catalog()` as an internal helper instead of renaming it, removed accidental dashboard-related wording from the milestone steps, and updated line counts and validation commands so the plan matches the current source tree.

Revision note (2026-04-14, pass 2): This pass corrected Milestone 3 with code-grounded details. The three `_is_remote_uri` copies differ structurally: `imports.py` and `env.py` use a try/except-fallback pattern importing from `remote_config` with a hardcoded scheme list as fallback, while `sql.py` defines it as a nested function inside `process_sql_file_references()` (not module-level). The plan now explicitly tells the worker that `sql.py`'s copy is nested, that `imports.py` already has a redundant `check_remote_uri` import that should be consolidated, and that the behavior is equivalent or improved when switching to the canonical source. No other milestones were changed.

Revision note (2026-04-14, pass 3): This pass hardened Milestone 4 with code-grounded execution details discovered by reading `engine.py`, `python_api.py`, `config/api.py`, `tests/test_engine_cli.py`, and `tests/test_connection_api.py`. Added: (1) removing `build_catalog` from `engine.py` `__all__` and fixing its docstring examples, (2) removing the dead `from .engine import build_catalog` import in `python_api.py`, (3) deleting the deprecated `_load_config_from_local_file` wrapper from `config/api.py` and renaming `_impl` to the simpler internal name, (4) explicit instructions to update surviving tests in `test_engine_cli.py` and `test_connection_api.py` to import `build_catalog` from `duckalog.engine` instead of `duckalog`, and (5) precise identification of which tests to remove vs. which to keep with updated imports.
