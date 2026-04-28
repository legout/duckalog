# Remove dead wrappers, canonicalize public guidance, and deepen Duckalog’s owned boundaries

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document must be maintained in accordance with `.ticket-flow/PLANS.md`.

This plan builds on `.ticket-flow/plans/simplification-refactoring/execplan.md` and `ARCHITECTURE.md`. Some earlier cleanup has already landed in the live tree — for example, the public `build_catalog` and `connect_and_build_catalog` exports are already gone and `remote_config.is_remote_uri()` is already the canonical URI detector — but the repository still carries dead wrapper modules, empty stubs, stale documentation, a shallow config/logging boundary, large orchestration modules (`cli.py`, `engine.py`, `connection.py`), and a dashboard that still speaks in `/build` terms.

## Purpose / Big Picture

Today, a contributor or user still has to remember too many legacy names and too many “almost canonical” places: dead wrapper modules remain in `src/duckalog/`, documentation still tells users to run `duckalog build` even though the command is gone, path and remote-URI logic are spread across several modules, the SQL generator still disagrees with its own tests about `scope`, and the CLI, engine, and connection layers still duplicate behavior instead of hiding it behind one owned boundary. That creates change amplification: removing a feature or fixing a behavior requires touching docs, examples, compatibility files, and multiple orchestration paths.

After this work, the system will present one clear mental model. There will be one canonical config-loading and path-security boundary, one clear CLI/API story (`run`, `show-paths --check`, `connect_to_catalog()`), one owned runtime state pipeline, and fewer dead or duplicate modules in the tree. A new contributor will be able to grep the repository and find the real implementation instead of wrappers, and a user following the README or examples will run commands that actually exist. The result should be observable in three ways: obsolete command names disappear from docs and examples, dead wrapper files disappear from `src/duckalog/`, and the CLI/config/engine/dashboard acceptance suites continue to pass with simpler internal structure.

## Progress

- [ ] Milestone 1: Remove dead wrapper modules, dead benchmark code, empty stubs, and stale compatibility tests.
- [ ] Milestone 2: Rewrite user-facing docs and examples so they only describe the current CLI and Python API.
- [ ] Milestone 3: Deepen the configuration boundary by removing duplicate validation and collapsing the shallow path wrapper layer; remote-URI detection is already canonical, so the remaining work is trimming `validators.py` and the package exports.
- [ ] Milestone 4: Share one catalog-state pipeline between the engine and connection layers, and split oversized SQL-generation switches into owned helpers without dropping the modeled `scope` behavior.
- [ ] Milestone 5: Shrink CLI and dashboard orchestration by moving bulky helper logic behind internal modules and aligning the dashboard build flow with the canonical `run` terminology.

## Surprises & Discoveries

- Observation: The source tree still contains files that were supposed to be removed by earlier cleanup work: `src/duckalog/config/interpolation.py`, `src/duckalog/logging_utils.py`, `src/duckalog/secret_types.py`, `src/duckalog/config/loading/base.py`, `src/duckalog/config/loading/file.py`, and `src/duckalog/config/loading/remote.py` all still exist. Two of them are zero-byte stubs.
  Evidence: direct file reads of those paths on 2026-04-14 showed deprecated proxy code, dead re-export code, unused secret models, and two empty files.

- Observation: User-facing documentation is much more out of date than the code. The removed `duckalog build` command still appears throughout the public docs and examples.
  Evidence: `grep -Rno --exclude-dir=__pycache__ 'duckalog build' README.md docs examples 2>/dev/null | wc -l` returned `230` during planning.

- Observation: `src/duckalog/config/validators.py` is a shallow consolidation layer. Most of its path helpers are simple pass-through wrappers over `src/duckalog/config/security/path.py`, which is already the deeper module.
  Evidence: `validators.py` imports `_detect_path_type_core`, `_resolve_relative_path_core`, `_validate_file_accessibility_core`, and related helpers directly from `config/security/path.py` and immediately re-exports thin wrappers.

- Observation: `src/duckalog/connection.py` already imports private engine helpers (`_apply_duckdb_settings`, `_create_secrets`, `_setup_attachments`, `_setup_iceberg_catalogs`, `_resolve_db_path`, `_create_views`), which proves the shared state-restoration pipeline already exists conceptually even though it is not owned in one place.
  Evidence: the top of `src/duckalog/connection.py` imports those private functions directly from `src/duckalog/engine.py`.

- Observation: `src/duckalog/config/__init__.py` contains a dead helper (`_call_with_monkeypatched_callable`) that no production or test code imports.
  Evidence: `grep -Rno --exclude-dir=__pycache__ '_call_with_monkeypatched_callable' src tests 2>/dev/null` returned only the definition in `src/duckalog/config/__init__.py`.

- Observation: `src/duckalog/benchmarks.py` is not imported anywhere in `src/` or `tests/`; it only duplicates a benchmark entrypoint already represented by example scripts, and `src/duckalog/performance.py` contains benchmark-reporting classes that are only used by that deleted runner.
  Evidence: `grep -Rno --exclude-dir=__pycache__ 'from .*benchmarks\|import .*benchmarks\|BenchmarkSuite\|run_standard_benchmarks' src tests examples docs README.md 2>/dev/null` returned only definitions inside `src/duckalog/benchmarks.py`, and `grep -Rno --exclude-dir=__pycache__ 'PerformanceTracker\|PerformanceReporter' src tests 2>/dev/null` returned only the definitions in `src/duckalog/performance.py` and the deleted benchmark runner.

- Observation: The current tree already centralizes remote-URI detection in `duckalog.remote_config.is_remote_uri()`; `src/duckalog/config/resolution/imports.py`, `src/duckalog/config/resolution/env.py`, and `src/duckalog/config/loading/sql.py` already import that helper instead of defining their own copies.
  Evidence: direct reads of those three modules on 2026-04-21 showed `from duckalog.remote_config import is_remote_uri as _is_remote_uri` and no local `_is_remote_uri` implementation.

- Observation: `src/duckalog/config/api.py` still imports `_is_remote_uri` from `config.resolution.imports` even though the name is unused there, and `duckalog.config.__init__` still re-exports `_load_config_from_local_file`.
  Evidence: `rg -n "_is_remote_uri|_load_config_from_local_file" src/duckalog/config/api.py src/duckalog/config/__init__.py` shows the unused import plus the package-level export.

- Observation: `_validate_unique_names()` in `src/duckalog/config/resolution/imports.py` covers four categories of uniqueness (view names, Iceberg catalog names, semantic model names, and attachment aliases), but `Config._validate_uniqueness` in `src/duckalog/config/models.py` only covers the first three. The model validator does not check attachment alias duplicates at all. Removing `_validate_unique_names` without first extending the model validator would silently lose attachment-alias uniqueness validation.
  Evidence: direct reads of `_validate_unique_names` (imports.py line 368) and `Config._validate_uniqueness` (models.py line 929). The attachment-alias block in `_validate_unique_names` iterates all four attachment types (duckdb, sqlite, postgres, duckalog) and raises `DuplicateNameError` on cross-type alias collisions. `Config._validate_uniqueness` has no such block.

- Observation: The exception handler around `Config.model_validate()` in `src/duckalog/config/resolution/imports.py` (lines ~968–976) contains a branch for "Duplicate attachment alias" that is dead code today: the model validator never raises that string because it does not check attachment aliases. After extending the model validator to cover attachment aliases, this branch would become live and correctly re-map the `ValueError` to `DuplicateNameError`.
  Evidence: `rg -n 'Duplicate attachment alias' src/duckalog/config/resolution/imports.py` matches only the exception-handler branch, and reading `Config._validate_uniqueness` in models.py confirms no attachment-alias check exists.

- Observation: `src/duckalog/config/security/base.py` is NOT dead. Unlike `src/duckalog/config/loading/base.py` (which defines unused ABCs with no concrete subclasses), `security/base.py` defines `PathResolver` and `PathValidator` ABCs that are actively subclassed by `DefaultPathResolver` and `DefaultPathValidator` in `security/path.py`. Similarly, `src/duckalog/config/resolution/base.py` is NOT dead: it defines `ImportContext`, `EnvProcessor`, and `ImportResolver` protocols that are used throughout the resolution chain.
  Evidence: `rg -n 'PathResolver|PathValidator' src/duckalog/config/security/path.py` shows active subclassing; `rg -n 'ImportContext|EnvProcessor|ImportResolver' src/duckalog/config/resolution/imports.py src/duckalog/config/resolution/env.py` shows active usage.

- Observation: `tests/test_config.py` and `tests/test_remote_config.py` still import `_load_config_from_local_file` through `duckalog.config`, which will break as soon as the package-level re-export disappears.
  Evidence: `rg -n "_load_config_from_local_file" tests/test_config.py tests/test_remote_config.py` finds direct imports from `duckalog.config`.

- Observation: `tests/test_sql_generation.py` already encodes the intended `scope` behavior for `SecretConfig`, but the current implementation omits it and therefore fails those tests.
  Evidence: `uv run pytest tests/test_sql_generation.py -q` currently fails in `test_generate_secret_sql_s3_with_scope` and `test_generate_secret_sql_scope_quoting` because `generate_secret_sql()` returns SQL without any `SCOPE` clause.

- Observation: `tests/test_dashboard.py` still hard-codes `/build`, `/build/status`, and `BuildController` expectations even though the dashboard code already uses Litestar and the plan wants `run` terminology.
  Evidence: direct reads of `tests/test_dashboard.py` and `src/duckalog/dashboard/routes/query.py` show the mismatch.

- Observation: `src/duckalog/config/loading/base.py` defines abstract `ConfigLoader` and `SQLFileLoader` types, but no concrete code subclasses them; the real SQL loader is the concrete `src/duckalog/sql_file_loader.py:SQLFileLoader` class.
  Evidence: `rg -n "ConfigLoader|SQLFileLoader\(" src tests` only finds the abstract definitions plus the concrete loader class and its call sites, not any subclassing relationship.

## Decision Log

- Decision: Treat dead-file removal and public-doc cleanup as separate early milestones, even though both are “cleanup” work.
  Rationale: They solve different user problems. Removing dead wrappers reduces contributor confusion in the codebase, while docs cleanup removes immediate user-facing breakage. They are also independently verifiable and mostly parallel-safe.
  Date/Author: 2026-04-14 / Pi

- Decision: Preserve `src/duckalog/config/security/path.py` as the canonical path boundary and shrink `src/duckalog/config/validators.py` instead of deleting the security layer.
  Rationale: `config/security/path.py` is the deeper module; it already hides path normalization, traversal prevention, and root validation. `validators.py` is the shallow wrapper. The simplification should remove the wrapper, not the deeper boundary.
  Date/Author: 2026-04-14 / Pi

- Decision: Keep the public CLI command names stable in this plan. Internal refactoring may move helper code out of `src/duckalog/cli.py`, but the public commands remain `run`, `validate`, `show-paths`, `show-imports`, `query`, `init`, and `ui`.
  Rationale: The docs are already out of date because commands were removed recently. Another public rename would create more change amplification instead of reducing it.
  Date/Author: 2026-04-14 / Pi

- Decision: Use internal helper extraction for the CLI (`cli_filesystem.py`, `cli_imports.py`, `cli_display.py`) rather than creating a new `duckalog/cli/` package.
  Rationale: The repo already has `src/duckalog/cli.py` as the console-script entry point. Creating a same-name package beside it would add import ambiguity. Flat helper modules hide complexity without introducing a new package concept.
  Date/Author: 2026-04-14 / Pi

- Decision: The dashboard’s build flow should be renamed to `run` in one clean change instead of carrying `/build` and `/run` as parallel routes.
  Rationale: The dashboard is an optional extra, not the documented primary interface. Carrying both names would preserve an obsolete concept and add another special case.
  Date/Author: 2026-04-14 / Pi

- Decision: Remove `src/duckalog/benchmarks.py` and the benchmark-only reporting/tracker classes from `src/duckalog/performance.py` instead of keeping a second benchmark entrypoint in `src/`.
  Rationale: The runner is unimported dead code and the repository already has example benchmark scripts. Keeping the extra entrypoint would preserve a duplicate way to start the same workflow.
  Date/Author: 2026-04-14 / Pi

- Decision: Remove `_call_with_monkeypatched_callable` and stop re-exporting `_load_config_from_local_file` from `duckalog.config` as part of the dead-code cleanup.
  Rationale: No production caller uses the helper, and keeping package-level compatibility exports makes the config surface harder to understand for no runtime benefit.
  Date/Author: 2026-04-14 / Pi

- Decision: Keep `_load_config_from_local_file()` in `src/duckalog/config/api.py` as the internal helper and remove only the package-level re-export from `duckalog.config`.
  Rationale: The code already uses that name internally, and renaming it would add churn without reducing complexity. The real cleanup is to stop advertising it as part of the package surface and update the small set of direct test importers to use `duckalog.config.api`.
  Date/Author: 2026-04-21 / Pi

- Decision: Before removing `_validate_unique_names()` from `imports.py`, extend `Config._validate_uniqueness` in `models.py` to also check attachment alias uniqueness across all four attachment types (duckdb, sqlite, postgres, duckalog), matching the coverage that `_validate_unique_names` provides today.
  Rationale: The model validator already checks view names, Iceberg catalog names, and semantic model names, but it does not check attachment aliases. The imports.py version is the only place that validates attachment-alias uniqueness. Removing it without adding the check to the model would silently lose that protection.
  Date/Author: 2026-04-21 / Pi

- Decision: Delete `tests/test_logging_utils.py` alongside `src/duckalog/logging_utils.py` rather than rewriting it.
  Rationale: The test file exclusively exercises the logging compatibility shim. The underlying redacted-logging behavior is already covered by `tests/test_engine_cli.py` (which verifies secret redaction in logs) and other integration tests. Rewriting the test to import from `config.validators` would preserve a test that tests the same logic through a different import path, which adds no value.
  Date/Author: 2026-04-21 / Pi

- Decision: Preserve `SecretConfig.scope` output in `generate_secret_sql()` while splitting provider-specific helpers.
  Rationale: The schema already models `scope`, the SQL-generation tests already expect it, and the current implementation is failing those tests. The split should reduce the giant switch without changing the modeled behavior.
  Date/Author: 2026-04-21 / Pi

- Decision: Update dashboard docs from Starlette to Litestar and rename `/build` to `/run` in the same change as the code rename.
  Rationale: The codebase has already moved to Litestar, so keeping the old framework name in docs would preserve a false mental model. Renaming the route and the docs together keeps the dashboard story coherent.
  Date/Author: 2026-04-21 / Pi

- Decision: Delete `src/duckalog/config/loading/base.py` instead of preserving the ABC layer.
  Rationale: No concrete loader subclasses the ABCs, and the real SQL loader already lives in `src/duckalog/sql_file_loader.py`. Keeping the extra abstraction would preserve a shallow layer without hiding any policy.
  Date/Author: 2026-04-21 / Pi

## Outcomes & Retrospective

This section is intentionally empty at plan creation time. Update it at the end of each major milestone with what was actually achieved, what changed from the original design, and what complexity was removed or unexpectedly remained.

## Context and Orientation

Duckalog lives in `src/duckalog/`. The current architecture is documented in `ARCHITECTURE.md`. The key architectural fact for this plan is that the repository already has one deep configuration-loading path and one canonical runtime path, but the tree still contains many leftover compatibility and orchestration artifacts from earlier refactors.

The most important files for this plan are:

- `src/duckalog/config/api.py` — the public `load_config()` entry point. It decides whether a config path is remote or local and still contains the internal `_load_config_from_local_file()` helper that some tests import directly.
- `src/duckalog/config/resolution/imports.py` — the real local config loader. It expands imports, loads `.env` files, inlines SQL file references, and validates merged configs.
- `src/duckalog/config/security/path.py` — the deep path-security module. It owns path normalization, traversal checks, and allowed-root validation.
- `src/duckalog/config/validators.py` — currently mixes redacted logging with thin path wrappers and config-level path rewriting; the path wrappers are still a shallow delegation layer.
- `src/duckalog/logging_utils.py` — a dead compatibility shim that simply re-exports logging functions from `config/validators.py`.
- `src/duckalog/config/interpolation.py` — a deprecated proxy module that emits warnings and re-exports env interpolation and SQL-file loading helpers.
- `src/duckalog/secret_types.py` — legacy per-backend secret models that are superseded by `SecretConfig` in `src/duckalog/config/models.py`.
- `src/duckalog/config/__init__.py` — still contains a dead helper (`_call_with_monkeypatched_callable`) and a deprecated package-level export (`_load_config_from_local_file`) that do not belong in the public surface.
- `src/duckalog/config/loading/base.py`, `src/duckalog/config/loading/file.py`, `src/duckalog/config/loading/remote.py` — an unused ABC module plus two empty loader stubs. The concrete SQL file loader lives in `src/duckalog/sql_file_loader.py`.
- `src/duckalog/benchmarks.py` — a benchmark runner that is not imported by production code; it only adds a second benchmark entrypoint on top of the example scripts.
- `src/duckalog/performance.py` — timing infrastructure used by the config loader, plus two dead reporting classes (`PerformanceTracker` and `PerformanceReporter`) that are only referenced by the deleted benchmark runner.
- `src/duckalog/remote_config.py` — remote config loading via fsspec. It still imports from `logging_utils.py` and owns the public `is_remote_uri()` helper.
- `src/duckalog/sql_file_loader.py` — the concrete SQL file loader class. It still imports from `logging_utils.py` and also performs its own path-resolution steps; this is the real loader, not the unused ABC in `config/loading/base.py`.
- `src/duckalog/cli.py` — the Typer CLI entry point. It is still the largest operational hotspot in the repo and contains filesystem creation, interactive shell behavior, table display, import-graph analysis, and command implementations all in one file.
- `src/duckalog/engine.py` — catalog build orchestration. It owns the actual DuckDB build pipeline.
- `src/duckalog/connection.py` — connection manager for Python callers. It restores state by importing private engine helpers directly.
- `src/duckalog/sql_generation.py` — DuckDB SQL generators. `generate_secret_sql()` is a large provider-specific switch.
- `src/duckalog/dashboard/routes/query.py`, `src/duckalog/dashboard/components/layout.py`, `src/duckalog/dashboard/routes/home.py`, and `src/duckalog/dashboard/app.py` — the optional dashboard still exposes a `/build` flow even though the CLI and public API have moved to `run` terminology.
- `tests/test_config.py` and `tests/test_remote_config.py` — these tests still import `_load_config_from_local_file` through `duckalog.config`, so they will fail once the package-level re-export is removed unless they are redirected to `duckalog.config.api`.
- `tests/test_sql_generation.py` — this suite currently fails because `generate_secret_sql()` drops `SecretConfig.scope` even though the schema still models `scope` and the tests expect it.
- `tests/test_dashboard.py` — this suite still asserts `/build` routes and `BuildController`, so the dashboard rename must update code and tests together.
- `README.md`, `docs/`, and `examples/` — user-facing guidance. These files still contain hundreds of references to removed commands (`duckalog build`, `validate-paths`, `init-env`) and one removed public function (`connect_and_build_catalog`).

This plan also needs to account for the earlier simplification plan at `.ticket-flow/plans/simplification-refactoring/execplan.md`. That earlier plan removed specific deprecated code paths, but this new plan is broader and more architectural: it finishes the dead-code cleanup, fixes the public guidance, and deepens the remaining shallow boundaries so future change touches fewer files.

The main complexity today is paid in three places:

1. Contributors have to know which modules are real and which are wrappers (`logging_utils.py`, `config/interpolation.py`, `config/__init__.py`'s dead helper, `config/loading/base.py`, `config/validators.py`).
2. Users have to translate obsolete docs into current commands because the docs and examples still describe `duckalog build`, `validate-paths`, and `init-env`.
3. Maintainers have to edit multiple orchestration paths when touching the CLI, engine, or connection layers because sequencing is duplicated rather than owned in one place.
4. The repository still carries a dead benchmark entrypoint and benchmark-only reporting classes, which adds yet another place to look for non-production code.

## Plan of Work

### Milestone 1 — Remove dead wrappers, dead benchmark code, and empty stubs (cleanup milestone)

This is a cleanup milestone, not a vertical feature slice, because its job is to delete concepts that no longer belong in the tree. It should land first because every later milestone becomes easier once the dead wrappers, the dead benchmark entrypoint, and the empty stubs are gone.

The scope is the clearly dead code that the repo already proves is obsolete. Delete `src/duckalog/logging_utils.py` and delete its dedicated test file `tests/test_logging_utils.py` (the underlying redacted-logging behavior is already covered by integration tests such as `tests/test_engine_cli.py` which verifies secret redaction in logs). Update `src/duckalog/config_init.py`, `src/duckalog/sql_file_loader.py`, and `src/duckalog/remote_config.py` to import logging helpers from `src/duckalog/config/validators.py` directly. Delete `src/duckalog/config/interpolation.py` and remove or rewrite any deprecation-warning tests that exist only to verify a module we no longer want to ship. Remove `_call_with_monkeypatched_callable` from `src/duckalog/config/__init__.py` and stop re-exporting the deprecated package-level `_load_config_from_local_file` helper there; `tests/test_config.py` and `tests/test_remote_config.py` still import that helper through `duckalog.config`, so they must be redirected to `duckalog.config.api` or rewritten to test through `load_config()` instead. Delete `src/duckalog/secret_types.py` now that `SecretConfig` in `src/duckalog/config/models.py` is the real secret model. Delete `src/duckalog/benchmarks.py` and trim `src/duckalog/performance.py` so it no longer carries reporting/tracker classes that only supported the deleted benchmark runner. Delete `src/duckalog/config/loading/file.py` and `src/duckalog/config/loading/remote.py` because they are zero-byte stubs, and delete `src/duckalog/config/loading/base.py` because its abstract `ConfigLoader` and `SQLFileLoader` types are unused. Update `src/duckalog/config/loading/__init__.py` so it no longer re-exports dead loader ABCs and leaves `src/duckalog/sql_file_loader.py` as the concrete loader owner.

The end state of this milestone is simple to observe: the repository no longer contains the dead wrapper/stub files, `grep` no longer finds production imports of `logging_utils`, `config.interpolation`, or the dead loading stubs, and the dead benchmark entrypoint plus benchmark-only reporting classes have been removed from `src/duckalog/`. The `duckalog.config` package no longer exposes `_call_with_monkeypatched_callable` or `_load_config_from_local_file` as public surface, and the small set of tests that still need the helper import it from `duckalog.config.api` instead. This milestone is a true prerequisite for Milestone 3 because the config-boundary cleanup should not be designed around compatibility files that are about to disappear. It is related to Milestone 2 because the docs also mention removed features, but the two milestones can proceed in parallel after the dead-file deletions are scoped. The main conflict points are `src/duckalog/config/__init__.py`, `src/duckalog/config/loading/__init__.py`, `src/duckalog/sql_file_loader.py`, `src/duckalog/remote_config.py`, `src/duckalog/performance.py`, `src/duckalog/benchmarks.py`, `tests/test_config.py`, `tests/test_remote_config.py`, and the compatibility tests.

### Milestone 2 — Canonicalize README, docs, and examples (vertical user-facing slice)

This milestone is a vertical slice because it directly changes the user-visible behavior of the project: a new user following the README, examples, or reference docs will run commands that actually exist. It does not require the internal refactors from Milestones 3–5, so it should not wait for them.

The work is a large but conceptually simple rewrite. Replace `duckalog build` with `duckalog run` across `README.md`, `docs/`, and `examples/`, but do it carefully: update surrounding prose so it describes what `run` does, not just the command token. Replace `duckalog validate-paths` with `duckalog show-paths --check`. Remove `init-env` sections instead of inventing a new fake replacement. Remove `connect_and_build_catalog` from API docs and examples in favor of `connect_to_catalog()` and the current Python API. Update the dashboard-facing docs so they describe the Litestar app that actually exists today, not the older Starlette story. Update makefiles and helper scripts under `examples/` that still print or execute removed commands. If any historical or changelog-style document must preserve an old command name, move that text into an explicitly historical note rather than leaving it in operational guidance.

This milestone can proceed in parallel with Milestone 3 because it mostly touches docs and example scaffolding. Its only serialization point is shared user-facing terminology: it assumes that `run`, `show-paths --check`, and `connect_to_catalog()` remain the canonical names, which this plan intentionally does not change. The observable end state is that `grep` finds zero operational references to `duckalog build`, `validate-paths`, `init-env`, or `connect_and_build_catalog` in `README.md`, `docs/`, and `examples/`, and that the dashboard docs no longer describe Starlette as the active framework.

### Milestone 3 — Deepen the configuration boundary (migration milestone)

This milestone is a migration milestone because it changes internal ownership boundaries while preserving the public `duckalog.config` interface. The goal is not to add a new layer; it is to remove the shallow ones.

The remote-URI part of this cleanup is mostly already done in code: `src/duckalog/config/resolution/imports.py`, `src/duckalog/config/resolution/env.py`, and `src/duckalog/config/loading/sql.py` already import `duckalog.remote_config.is_remote_uri()` instead of defining private copies. The remaining work is to remove the last stale import from `src/duckalog/config/api.py` if it is still present, and to keep future callers on the canonical helper.

The main structural work is, first, to extend `Config._validate_uniqueness` in `src/duckalog/config/models.py` so it also checks attachment alias uniqueness across all four attachment types (duckdb, sqlite, postgres, duckalog), matching the coverage `_validate_unique_names` in `imports.py` provides today. The existing exception handler in `imports.py` around the `Config.model_validate()` call already maps "Duplicate attachment alias" strings to `DuplicateNameError`, so once the model validator raises that message, the error mapping will work without additional changes. Then remove `_validate_unique_names()` from `src/duckalog/config/resolution/imports.py` and its call site at line 986, because `Config` in `src/duckalog/config/models.py` now performs all four uniqueness checks after model construction. Keep the existing error mapping so duplicate-name failures across imported files still surface as `DuplicateNameError`. Then remove the stale `from .resolution.imports import _is_remote_uri` import from `src/duckalog/config/api.py` (this import is unused: the function body calls `is_remote_uri` via a local `from duckalog.remote_config import` inside the try block, making the module-level import redundant). After uniqueness validation is consolidated, shrink `src/duckalog/config/validators.py` so it owns only what it truly owns: redacted logging plus config-level path rewriting (`_resolve_paths_in_config`, `_resolve_view_paths`, `_resolve_attachment_paths`). Remove the simple pass-through path wrappers from `validators.py` and have internal callers import from `src/duckalog/config/security/path.py` directly. Note that `src/duckalog/config/security/base.py` is NOT in scope for deletion: unlike `config/loading/base.py` it defines `PathResolver` and `PathValidator` ABCs that `DefaultPathResolver` and `DefaultPathValidator` in `security/path.py` actively subclass. Similarly, `src/duckalog/config/resolution/base.py` is NOT in scope: it defines `ImportContext`, `EnvProcessor`, and `ImportResolver` protocols used throughout the resolution chain. To preserve the public `duckalog.config` surface, update `src/duckalog/config/__init__.py` to re-export the path helpers from `config.security.path` instead of from `validators.py`.

This milestone depends on Milestone 1 because dead wrappers and stubs should be gone before we simplify the config boundary. It can run in parallel with Milestone 2. It conflicts with any simultaneous edits to `src/duckalog/config/__init__.py`, `src/duckalog/config/api.py`, `src/duckalog/config/resolution/imports.py`, `src/duckalog/config/resolution/env.py`, `src/duckalog/config/loading/sql.py`, and `src/duckalog/sql_file_loader.py`, so implement it as one focused branch. The observable end state is that path-security helpers have one canonical owner, remote-URI detection has one canonical owner, and uniqueness validation has one canonical owner.

### Milestone 4 — Share one catalog-state pipeline in engine and connection, and deepen SQL generation (deepening milestone)

This milestone reduces change amplification in the runtime core. Today `src/duckalog/connection.py` imports a cluster of private functions from `src/duckalog/engine.py`, which is already a sign that one architectural concept exists but is not owned in one place. The plan is to make that concept explicit and owned.

Introduce one internal pipeline that applies catalog state to a DuckDB connection: settings, secrets, attachments, optional Iceberg catalogs, and view creation. Keep it private, but make it the thing both `CatalogBuilder` and `CatalogConnection` call instead of manually repeating or partially importing the sequence. The exact shape can stay inside `src/duckalog/engine.py` if that keeps concepts fewer; for example, a private helper such as `_apply_catalog_state(conn, config, *, create_views: bool, duckalog_results: dict[str, BuildResult] | None = None)` is preferable to a new public abstraction.

At the same time, split `generate_secret_sql()` in `src/duckalog/sql_generation.py` into provider-specific private helpers so the module stops hiding all provider differences in one giant switch statement. Keep the current public function name and keep the currently modeled `SecretConfig.scope` behavior: the tests already expect `scope` to appear in generated SQL, so the refactor must preserve or restore that output rather than silently dropping it. A small shared helper for the scope suffix is better than duplicating that logic inside every provider branch.

This milestone is related to Milestone 5 because the CLI eventually calls into the same runtime path, but it does not depend on the CLI refactor. It is mostly independent of Milestones 1–3 except for shared config imports. The conflict points are `src/duckalog/engine.py`, `src/duckalog/connection.py`, `src/duckalog/sql_generation.py`, `tests/test_sql_generation.py`, and the engine/connection test suite. The observable end state is that there is one owned place to change catalog state application and one owned place per secret-provider SQL dialect, with the existing `scope` tests passing again.

### Milestone 5 — Shrink CLI and dashboard orchestration without changing the CLI surface (cleanup and deepening milestone)

This milestone is partly cleanup and partly deepening. The CLI should keep its public commands, but it should stop being the place where every implementation detail lives. The dashboard should stop talking about “build” when the rest of the product now says “run.”

Extract three internal helper modules from `src/duckalog/cli.py` without turning the repo into a new package hierarchy. Create `src/duckalog/cli_filesystem.py` for filesystem option normalization and fsspec protocol construction, `src/duckalog/cli_imports.py` for import-graph collection/diagnostics/printing, and `src/duckalog/cli_display.py` for table rendering plus the interactive SQL loop. Leave the Typer command definitions in `src/duckalog/cli.py`, but make that file read like command wiring rather than a kitchen sink. While touching the CLI, keep the current command names and exit semantics exactly the same.

Then align the dashboard with the canonical `run` terminology. Rename `BuildController` in `src/duckalog/dashboard/routes/query.py` to `RunController` (or another clearly run-oriented internal name), rename the route path and UI labels from `/build` to `/run`, and update the build-status DOM IDs and buttons in `src/duckalog/dashboard/components/layout.py` and `src/duckalog/dashboard/routes/home.py` accordingly. Update `src/duckalog/dashboard/routes/__init__.py`, `src/duckalog/dashboard/app.py`, and `tests/test_dashboard.py` in the same change so the code and tests stay consistent. Do this in one change rather than keeping both `/build` and `/run`, because the dashboard is an optional extra and the clean rename removes a stale concept instead of preserving it.

This milestone depends on Milestone 4 only loosely: the shared engine pipeline makes the CLI refactor safer, but the helper extractions themselves can begin earlier. The dashboard rename depends on Milestone 2’s terminology decision (`run` is canonical) and should not happen in parallel with doc changes that are rewriting the same dashboard instructions. The main conflict points are `src/duckalog/cli.py`, the three new helper modules, `src/duckalog/dashboard/app.py`, `src/duckalog/dashboard/routes/__init__.py`, `src/duckalog/dashboard/routes/query.py`, `src/duckalog/dashboard/routes/home.py`, `src/duckalog/dashboard/components/layout.py`, and `tests/test_dashboard.py`.

## Concrete Steps

All commands below are run from the repository root: `/Users/volker/coding/libs/duckalog`.

For Milestone 1, first confirm the current dead files and their importers:

    grep -Rno --exclude-dir=__pycache__ 'logging_utils' src tests 2>/dev/null
    grep -Rno --exclude-dir=__pycache__ 'config.interpolation' src tests 2>/dev/null
    grep -Rno --exclude-dir=__pycache__ 'benchmarks\|PerformanceTracker\|PerformanceReporter' src tests 2>/dev/null
    grep -Rno --exclude-dir=__pycache__ '_call_with_monkeypatched_callable\|_load_config_from_local_file' src tests 2>/dev/null
    ls -l src/duckalog/config/loading/file.py src/duckalog/config/loading/remote.py

After deleting the dead files and updating imports, verify that only intentional historical references remain (ideally none outside generated metadata):

    grep -Rno --exclude-dir=__pycache__ 'logging_utils' src tests 2>/dev/null || true
    grep -Rno --exclude-dir=__pycache__ 'config.interpolation' src tests 2>/dev/null || true
    grep -Rno --exclude-dir=__pycache__ 'secret_types' src tests 2>/dev/null || true
    grep -Rno --exclude-dir=__pycache__ 'benchmarks\|PerformanceTracker\|PerformanceReporter' src tests 2>/dev/null || true
    grep -Rno --exclude-dir=__pycache__ '_call_with_monkeypatched_callable\|_load_config_from_local_file' src tests 2>/dev/null || true

Run the compatibility, config-loading, performance-regression, and public-surface tests that touch these areas. Note that `tests/test_logging_utils.py` should be deleted as part of this milestone (not run):

    uv run pytest tests/test_deprecation_warnings.py tests/test_sql_file_loading.py tests/test_config_imports.py tests/test_config.py tests/test_remote_config.py tests/test_performance_regression.py -q

For Milestone 2, measure the documentation drift before changing it:

    grep -Rno --exclude-dir=__pycache__ 'duckalog build' README.md docs examples 2>/dev/null | wc -l
    grep -Rno --exclude-dir=__pycache__ 'validate-paths' README.md docs examples 2>/dev/null | wc -l
    grep -Rno --exclude-dir=__pycache__ 'init-env' README.md docs examples 2>/dev/null | wc -l
    grep -Rno --exclude-dir=__pycache__ 'connect_and_build_catalog' README.md docs examples 2>/dev/null | wc -l
    grep -Rno --exclude-dir=__pycache__ 'Starlette' README.md docs examples 2>/dev/null | wc -l

After rewriting the docs and examples, the same commands should print `0` (unless a file is intentionally historical and explicitly labeled as historical). If any example helper script still shells out to a removed command, run that script’s printed instructions or local smoke command manually and confirm it points to `duckalog run`.

For Milestone 3, verify the canonical config-boundary owners before editing:

    grep -n 'def _validate_unique_names' src/duckalog/config/resolution/imports.py
    grep -n 'def _validate_uniqueness' src/duckalog/config/models.py
    grep -Rno --exclude-dir=__pycache__ 'def _is_remote_uri\|is_remote_uri as _is_remote_uri' src/duckalog/config src/duckalog/remote_config.py
    grep -n '_is_remote_uri' src/duckalog/config/api.py

First, extend `Config._validate_uniqueness` in `src/duckalog/config/models.py` to add an attachment-alias uniqueness block that checks all four attachment types, raising `ValueError` with "Duplicate attachment alias(es) found: ..." so the existing exception handler in `imports.py` maps it to `DuplicateNameError`. Then remove `_validate_unique_names()` from `imports.py` and its call site. Then remove the stale `_is_remote_uri` import from `api.py`. Then shrink `validators.py` and update `config/__init__.py` re-exports. After the refactor, `remote_config.is_remote_uri()` should be the only URI detector, `_validate_unique_names()` should be gone from `imports.py`, `api.py` should have no unused `_is_remote_uri` import, and internal path helper imports should point at `src/duckalog/config/security/path.py`. Then run:

    uv run pytest tests/test_config.py tests/test_config_imports.py tests/test_path_resolution.py tests/test_path_security.py tests/test_remote_config.py tests/test_sql_file_loading.py tests/test_performance_regression.py -q

For Milestone 4, capture the current duplication boundary first:

    grep -n 'from \.engine import (' -n src/duckalog/connection.py
    grep -n 'def generate_secret_sql' src/duckalog/sql_generation.py

After introducing the shared catalog-state pipeline and splitting secret generation into per-provider helpers, run:

    uv run pytest tests/test_connection_api.py tests/test_engine_cli.py tests/test_engine_hierarchical.py tests/test_engine_remote_export.py tests/test_sql_generation.py -q

For Milestone 5, measure CLI and dashboard terminology and size before editing:

    python3 - <<'PY'
    import pathlib
    p = pathlib.Path('src/duckalog/cli.py')
    print(sum(1 for _ in p.open()), 'lines in src/duckalog/cli.py')
    PY
    grep -Rno --exclude-dir=__pycache__ '/build\|BuildController\|build-status' src/duckalog/dashboard 2>/dev/null

After extracting the helper modules and renaming the dashboard flow to `run`, the CLI file should be materially smaller, and the dashboard grep should only show deliberate migration comments if any. Then run:

    uv run pytest tests/test_cli_filesystem.py tests/test_cli_query.py tests/test_cli_remote.py -q

If the `ui` extra is installed, also run:

    uv run pytest tests/test_dashboard.py -q

If the `ui` extra is not installed locally, install it first with the project extras or run the dashboard smoke tests in the environment that normally validates `duckalog[ui]`.

## Validation and Acceptance

This plan is complete when all of the following are true:

1. The dead wrapper and stub files listed in Milestone 1 are gone from `src/duckalog/`, and no production imports refer to them anymore. The `duckalog.config` package no longer exposes `_call_with_monkeypatched_callable` or `_load_config_from_local_file` as public surface, and any remaining direct helper tests import from `duckalog.config.api` instead of `duckalog.config`.
2. The dead benchmark runner and benchmark-only tracking/reporting classes are gone from `src/duckalog/`, and no production imports refer to them anymore.
3. `README.md`, `docs/`, and `examples/` no longer instruct users to run `duckalog build`, `validate-paths`, `init-env`, or `connect_and_build_catalog()` as current behavior, and the dashboard docs describe the Litestar app and `run` terminology that the code actually uses.
4. `src/duckalog/remote_config.py:is_remote_uri()` is the single remote-URI detector, `Config` in `src/duckalog/config/models.py` is the single owner of uniqueness validation (including attachment alias uniqueness across all four attachment types), and `src/duckalog/config/security/path.py` is the canonical owner of path-security helpers. The stale `_is_remote_uri` import has been removed from `src/duckalog/config/api.py`.
5. `src/duckalog/connection.py` stops reassembling the engine’s state-restoration sequence by hand and instead calls one shared internal pipeline.
6. `src/duckalog/sql_generation.py` still exposes `generate_secret_sql()`, but the provider-specific logic lives in smaller private helpers rather than one giant switch statement, and the current `scope` expectations in `tests/test_sql_generation.py` pass again.
7. `src/duckalog/cli.py` remains the console entry point, but the bulky helper logic has moved into internal helper modules and the file is materially smaller and easier to read.
8. The dashboard no longer presents a `/build` flow or `BuildController`; it uses the canonical `run` terminology instead, and `tests/test_dashboard.py` reflects the renamed route/controller names.
9. The following commands all exit successfully:

    uv run pytest tests/test_deprecation_warnings.py tests/test_sql_file_loading.py tests/test_config_imports.py tests/test_config.py tests/test_remote_config.py tests/test_performance_regression.py -q
    uv run pytest tests/test_config.py tests/test_config_imports.py tests/test_path_resolution.py tests/test_path_security.py tests/test_remote_config.py tests/test_sql_file_loading.py tests/test_performance_regression.py -q
    uv run pytest tests/test_connection_api.py tests/test_engine_cli.py tests/test_engine_hierarchical.py tests/test_engine_remote_export.py tests/test_sql_generation.py -q
    uv run pytest tests/test_cli_filesystem.py tests/test_cli_query.py tests/test_cli_remote.py -q

    If the `ui` extra is installed, also expect:

        uv run pytest tests/test_dashboard.py -q

10. The doc grep commands from Milestone 2 print `0` for operational references to removed commands and removed public functions, and the additional `Starlette` grep also prints `0` once the dashboard docs have been rewritten to match the Litestar app.

## Idempotence and Recovery

Milestone 1 is safe to repeat because deleting already-deleted dead files should produce no-op diffs, and the validation is grep-based. If a deletion reveals a hidden consumer, recover by restoring the file from version control, updating the importer to the canonical module, and then retrying the deletion. Do not keep a compatibility wrapper once the importer is fixed.

Milestone 2 is idempotent because the success condition is grep-based. If a broad replace accidentally edits historical or changelog-style text, restore that one file and reword it explicitly as historical rather than keeping an operational command example.

Milestone 3 should be landed as one focused branch because it changes the ownership of config helpers. If the refactor breaks imports halfway through, revert only the in-progress files and reapply the change in the order described: extend the model validator for attachment aliases first, delete duplicate uniqueness validation second, remove the unused `_is_remote_uri` import from `api.py` third, then shrink `validators.py` and update imports fourth.

Milestone 4 should not be split across partial commits that leave `connection.py` and `engine.py` disagreeing about the state-restoration sequence. Introduce the shared helper first, switch both callers to it second, and only then remove redundant code.

Milestone 5 should not rename the dashboard route in one commit and the UI consumers in another. Update route names, DOM IDs, and controller imports together so the optional dashboard stays internally consistent. If a dashboard rename proves too disruptive in a downstream environment, revert the route rename as one patch and keep the CLI helper extraction independent.

## Artifacts and Notes

The plan is grounded in these planning artifacts and repo observations:

    .ticket-flow/PLANS.md
    ARCHITECTURE.md
    .ticket-flow/plans/simplification-refactoring/execplan.md
    code-review-dead-duplicate-overcomplex.md
    scout/from-the-findings-above.md

The last two files above are referenced in the planning trail but are not present in the working tree; they should be treated as historical context, not as implementation inputs the next contributor can open locally.

Useful evidence captured during planning:

    $ grep -Rno --exclude-dir=__pycache__ 'duckalog build' README.md docs examples 2>/dev/null | wc -l
    230  (historical snapshot from an earlier planning pass; the current tree is lower)

    $ grep -Rno --exclude-dir=__pycache__ 'benchmarks\|PerformanceTracker\|PerformanceReporter' src tests 2>/dev/null
    (only definitions in src/duckalog/benchmarks.py and src/duckalog/performance.py)

    $ grep -Rno --exclude-dir=__pycache__ '_call_with_monkeypatched_callable' src tests 2>/dev/null
    (only the definition in src/duckalog/config/__init__.py)

    $ ls -l src/duckalog/config/loading/file.py src/duckalog/config/loading/remote.py
    -rw-r--r-- ... src/duckalog/config/loading/file.py
    -rw-r--r-- ... src/duckalog/config/loading/remote.py
    (both files are zero bytes)

    $ grep -n 'from \.engine import (' -n src/duckalog/connection.py
    (shows private engine helpers imported directly into connection.py)

Current confirmation from 2026-04-21:

    $ grep -Rno --exclude-dir=__pycache__ 'duckalog build' README.md docs examples 2>/dev/null | wc -l
    198

    $ grep -n '_load_config_from_local_file' tests/test_config.py tests/test_remote_config.py
    (both tests still import the helper from duckalog.config)

    $ uv run pytest tests/test_sql_generation.py -q
    2 failed, 32 passed
    (the failures are both scope-related)

    $ rg -n 'Starlette|/build|BuildController|build-status' README.md docs src/duckalog/dashboard tests/test_dashboard.py
    (shows the dashboard terminology drift still present in docs, code, and tests)

These snippets are not the implementation; they are the evidence for why the implementation should remove dead artifacts and deepen the current boundaries.

## Interfaces and Dependencies

The implementation must preserve these external interfaces while simplifying internals:

- `src/duckalog/config/api.py:load_config()` remains the public config-loading entry point.
- `src/duckalog/config/api.py:_load_config_from_local_file()` remains an internal helper for direct tests and internal code, but it should not be re-exported from `duckalog.config`.
- `src/duckalog/remote_config.py:is_remote_uri()` becomes the only remote-URI detector. No other `_is_remote_uri()` implementation should remain in `src/duckalog/`.
- `src/duckalog/config/models.py:Config` remains the owner of uniqueness validation through its `@model_validator` methods.
- `src/duckalog/config/security/path.py` remains the canonical home for `is_relative_path`, `resolve_relative_path`, `validate_path_security`, `validate_file_accessibility`, `normalize_path_for_sql`, `detect_path_type`, and related path helpers.
- `src/duckalog/config/__init__.py` should no longer expose `_call_with_monkeypatched_callable` or `_load_config_from_local_file`; callers should use `load_config()` and the explicit public path/log helpers.
- `src/duckalog/config/__init__.py` must continue to re-export the path helpers and logging helpers that public callers use today, but it may source those exports from different internal modules after the refactor.
- `src/duckalog/engine.py` should define one private helper that applies catalog state to a connection, and both `CatalogBuilder` and `CatalogConnection` must call it.
- `src/duckalog/performance.py` should retain `PerformanceMetrics`, `OperationMetric`, `BenchmarkResult`, and `RegressionDetector` if the regression tests still use them, but it should not keep `PerformanceTracker` or `PerformanceReporter` after the benchmark runner is deleted.
- `src/duckalog/sql_generation.py` must keep the public `generate_secret_sql(secret: SecretConfig) -> str` signature even if the function delegates to provider-specific private helpers such as `_generate_s3_secret_sql(secret)`, and it must continue to emit `scope` for the `SecretConfig.scope` field that the tests already expect.
- `src/duckalog/cli.py` must remain the console-script entry point. The internal helper modules should be flat sibling files such as `src/duckalog/cli_filesystem.py`, `src/duckalog/cli_imports.py`, and `src/duckalog/cli_display.py`, not a new `duckalog/cli/` package.
- `src/duckalog/dashboard/app.py` and `src/duckalog/dashboard/routes/__init__.py` must register the renamed dashboard run controller after the dashboard terminology change.

Change boundaries and conflict points to respect while ticketizing this plan later:

- `src/duckalog/config/__init__.py`, `src/duckalog/config/api.py`, `src/duckalog/config/validators.py`, and `src/duckalog/config/security/path.py` are a serialization point for Milestone 3. Do not implement two parallel tickets that all edit these files, and keep `tests/test_config.py` and `tests/test_remote_config.py` in the same slice if they still need the internal helper import.
- `src/duckalog/engine.py`, `src/duckalog/connection.py`, `src/duckalog/sql_generation.py`, and `tests/test_sql_generation.py` are a serialization point for Milestone 4.
- `src/duckalog/cli.py` and the new CLI helper modules are a serialization point for Milestone 5. `tests/test_cli_filesystem.py`, `tests/test_cli_query.py`, `tests/test_cli_remote.py`, and `tests/test_dashboard.py` must move with them.
- Dashboard route renames collide on `src/duckalog/dashboard/routes/query.py`, `src/duckalog/dashboard/routes/home.py`, `src/duckalog/dashboard/components/layout.py`, `src/duckalog/dashboard/app.py`, `src/duckalog/dashboard/routes/__init__.py`, and `tests/test_dashboard.py`; do not split them across independent tickets.

Change note: 2026-04-14 — Initial plan created from the architecture audit, the dead-code review artifact, the scout summary, and direct repo inspection because no brainstorm existed for the topic slug `from-the-findings-above`.

Change note: 2026-04-14 — Improved after a second pass through the live codebase. Added the dead `benchmarks.py` runner, the dead `config.__init__` helper/export, and the benchmark-only classes in `performance.py` to the cleanup scope; tightened the validation commands and acceptance checks so they now cover the actual dead code and compatibility surfaces found by grep.

Change note: 2026-04-21 — Improved after a fresh code audit against the live tree. Corrected stale assumptions about the current state of `remote_config.is_remote_uri()`, the direct test imports of `_load_config_from_local_file`, the existing `scope` failures in `tests/test_sql_generation.py`, and the dashboard’s lingering `/build` terminology. Also updated the plan to point direct helper tests at `duckalog.config.api`, to keep `scope` behavior explicit during SQL-generation refactoring, and to treat the dashboard docs/tests as part of the same rename slice.


Change note: 2026-04-21 — Second improvement pass. Found that `_validate_unique_names()` in `imports.py` checks attachment alias uniqueness across four attachment types (duckdb, sqlite, postgres, duckalog), but `Config._validate_uniqueness` in `models.py` does not check attachment aliases at all. The plan's earlier claim that the model validator "already performs uniqueness validation" was partially wrong. Updated Milestone 3 to require extending the model validator for attachment aliases before removing the imports.py version. Also clarified that `config/security/base.py` and `config/resolution/base.py` are NOT dead (unlike `config/loading/base.py`), explicitly called out `tests/test_logging_utils.py` for deletion rather than rewrite, added the unused `_is_remote_uri` import in `api.py` as a concrete cleanup step, and added `tests/test_performance_regression.py` to the Milestone 3 verification command since it uses classes that must be preserved.
