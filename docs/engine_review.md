# Engine & Connection Layer Review

Scope: reviewed `ARCHITECTURE.md` engine/connection sections and inspected `src/duckalog/engine.py`, `src/duckalog/connection.py`, `src/duckalog/python_api.py`, and `src/duckalog/performance.py`. Requested `plan.md` and `progress.md` were not present in the repo root.

## Review

### Correct

- `ARCHITECTURE.md` accurately calls out the intended layer split and already identifies `CatalogBuilder`/connection sequencing as a leaky boundary (`ARCHITECTURE.md:17`, `ARCHITECTURE.md:241-243`). The current `CatalogBuilder.build()` is now a short dispatcher (`src/duckalog/engine.py:85-104`), with phase helpers for dry-run, connection setup, export, and cleanup.
- `CatalogConnection` does implement lazy initialization and shared connection reuse for the normal case: it loads config only when needed (`src/duckalog/connection.py:99-105`), connects once (`src/duckalog/connection.py:131-139`), restores state (`src/duckalog/connection.py:141-146`), and returns the same connection on later calls (`src/duckalog/connection.py:96-97`).
- `PerformanceMetrics` is not entirely dead code: the import resolver creates it in `RequestContext` (`src/duckalog/config/resolution/imports.py:42-54`) and records timings around path resolution, file I/O, parsing, env interpolation, SQL processing, and dotenv loading (`src/duckalog/config/resolution/imports.py:377-383`, `src/duckalog/config/resolution/imports.py:619-651`).

### Findings

#### 1. Severity: High — Connection/CLI path does not build or attach Duckalog child catalogs

- Evidence: `build_catalog()` explicitly builds Duckalog attachment dependencies and stores `duckalog_results` (`src/duckalog/engine.py:522-553`), then passes those results into `CatalogBuilder` (`src/duckalog/engine.py:561-570`). `_apply_catalog_state()` only attaches Duckalog child catalogs when `duckalog_results` is provided (`src/duckalog/engine.py:967-984`).
- Evidence: `CatalogConnection.get_connection()` calls `_apply_catalog_state()` with no `duckalog_results` (`src/duckalog/connection.py:141-146`), and then creates/recreates views (`src/duckalog/connection.py:173-180`, `src/duckalog/connection.py:225-228`). The CLI non-dry-run path uses `connect_to_catalog()` rather than `build_catalog()` (`src/duckalog/cli.py:271-279`).
- Verified behavior: a parent config with `attachments.duckalog` and a view selecting from `ref.child_view` fails through `duckalog.python_api.connect_to_catalog(..., force_rebuild=True)` with `EngineError: Failed to rebuild views: Catalog Error: Table with name child_view does not exist`.
- Rationale: this breaks the advertised connection/session restoration path for hierarchical catalogs. It is also a leaky abstraction: the connection layer depends on engine-private helpers (`src/duckalog/connection.py:19-24`) but does not reproduce the dependency-building state that those helpers require.

#### 2. Severity: High — Missing-fsspec remote export error path is unreachable

- Evidence: `_setup_connection()` intends to reject remote export without fsspec (`src/duckalog/engine.py:155-159`), but the guard is nested under `if is_remote_export_uri(target_db)`. `is_remote_export_uri()` returns `False` whenever `FSSPEC_AVAILABLE` is false (`src/duckalog/engine.py:585-588`).
- Verified behavior: with `FSSPEC_AVAILABLE` patched to `False`, `build_catalog(..., db_path='s3://bucket/catalog.duckdb')` tried `duckdb.connect('s3://bucket/catalog.duckdb')` and raised `EngineError Failed to connect to DuckDB at s3://bucket/catalog.duckdb: IO Error: Cannot open file ...`, not the intended remote-export dependency error.
- Rationale: remote URIs are misclassified as local paths when the optional dependency is absent, so error handling no longer matches the engine's own message or the remote-export tests' intent (`tests/test_engine_remote_export.py:185-195`).

#### 3. Severity: Medium — `build_catalog(include_secrets=...)` is dead/ignored API surface

- Evidence: `build_catalog()` exposes `include_secrets` and documents it (`src/duckalog/engine.py:461-483`), but the value is never passed into `CatalogBuilder` or `_handle_dry_run()` (`src/duckalog/engine.py:561-570`). `_handle_dry_run()` always calls `generate_all_views_sql(..., include_secrets=True)` (`src/duckalog/engine.py:142-147`).
- Evidence: repo-wide grep found `include_secrets` only in `engine.py`, `sql_generation.py`, and SQL-generation tests; no call path consumes `build_catalog()`'s parameter.
- Rationale: callers cannot suppress secret SQL through the documented `build_catalog()` argument, so dry-run output may include secrets despite an explicit false value.

#### 4. Severity: Medium — `use_connection` path appears unfinished and is untested/dead in production callers

- Evidence: `build_catalog()` exposes `use_connection` (`src/duckalog/engine.py:463-486`) and `CatalogBuilder` branches into `_build_with_connection()` (`src/duckalog/engine.py:91-92`), but grep found no CLI or test callers using `use_connection`.
- Evidence: `_build_with_connection()` opens a `CatalogConnection` against the target database before checking whether that target is a remote export URI (`src/duckalog/engine.py:110-119`, `src/duckalog/engine.py:129-138`). The comments explicitly note the path is bypassing `_setup_connection()` and needs refinement (`src/duckalog/engine.py:121-128`).
- Evidence: this path also ignores `self.duckalog_results`; the `CatalogConnection` constructor has no parameter for dependency build results (`src/duckalog/engine.py:113-118`, `src/duckalog/connection.py:46-54`).
- Rationale: this public parameter combines unfinished remote-export handling with the same hierarchical-catalog gap described above, while adding another orchestration mode to the engine.

#### 5. Severity: Medium — Engine error wrapping is inconsistent with `build_catalog()` documentation

- Evidence: `build_catalog()` documents `EngineError` for connection and SQL execution failures (`src/duckalog/engine.py:492-494`). `_setup_connection()` wraps connection failures (`src/duckalog/engine.py:172-178`) and `_create_secrets()` wraps secret creation failures (`src/duckalog/engine.py:741-751`).
- Evidence: other phases execute DuckDB calls without contextual wrapping: extension/pragmas/settings (`src/duckalog/engine.py:758-781`), Iceberg catalog attach (`src/duckalog/engine.py:905-929`), and view creation (`src/duckalog/engine.py:932-951`). `CatalogConnection.get_connection()` compensates with a broad wrapper (`src/duckalog/connection.py:159-166`), but plain `build_catalog()` does not.
- Rationale: the same underlying failure can surface as raw DuckDB exceptions in the build path and as `EngineError` in the connection path, which makes error handling patterns harder to reason about.

#### 6. Severity: Low — View-creation logic is duplicated between engine and connection layers

- Evidence: engine view creation creates schemas then executes `generate_view_sql()` for all views (`src/duckalog/engine.py:932-951`). Connection incremental creation repeats schema creation and `generate_view_sql()` execution for missing views (`src/duckalog/connection.py:212-228`).
- Rationale: the connection layer already imports `_create_views` from engine (`src/duckalog/connection.py:19-23`) but still carries its own partial copy. This duplication is a drift risk for future changes to schema/view creation semantics.

#### 7. Severity: Low — `CatalogConnection.get_connection()` contains a dead compatibility branch

- Evidence: the read-only missing-file check at `src/duckalog/connection.py:109-114` performs `pass` and is immediately followed by the real check at `src/duckalog/connection.py:116-123`.
- Rationale: the no-op branch and contradictory comments add noise to already stateful connection initialization.

#### 8. Severity: Low — Python API narrows lower-level connection capabilities and duplicates generated-config validation

- Evidence: `connection.connect_to_catalog()` accepts `filesystem` and `load_dotenv` (`src/duckalog/connection.py:254-260`), but `python_api.connect_to_catalog()` exposes only `config_path`, `database_path`, `read_only`, and `force_rebuild` (`src/duckalog/python_api.py:62-67`) and forwards only those (`src/duckalog/python_api.py:100-105`).
- Evidence: generated-config validation exists in both `config_init.py` (`src/duckalog/config_init.py:195-222`) and `python_api.py` (`src/duckalog/python_api.py:147-164`). The public package import selects the `config_init` version (`src/duckalog/__init__.py:22-35`), leaving the `python_api.py` version as parallel API surface.
- Rationale: programmatic users lose access to connection features that the lower layer already supports, and duplicate validation helpers create two places for behavior to diverge.

#### 9. Severity: Low — `ConfigDependencyGraph` keeps unused/nondeterministic state

- Evidence: `visited` is initialized (`src/duckalog/engine.py:236-238`) and written in `finally` (`src/duckalog/engine.py:317-319`), but grep found no reads. Cycle-path diagnostics are built from the unordered `visiting` set (`src/duckalog/engine.py:282-285`).
- Rationale: this is overcomplicated state management in dependency orchestration; the stored state does not currently affect behavior, and cycle messages can be nondeterministic.

#### 10. Severity: Low — `RegressionDetector` has zero-baseline division edge cases

- Evidence: `BenchmarkResult.__post_init__()` leaves `avg_time` at `0.0` when `iterations == 0` (`src/duckalog/performance.py:92-94`). `RegressionDetector.detect()` divides by `baseline.avg_time` for overall degradation (`src/duckalog/performance.py:109-118`) and by `base_total` for metric degradation (`src/duckalog/performance.py:121-136`) without checking zero baselines.
- Rationale: benchmark comparison can crash on an empty or zero-duration baseline instead of returning a regression/no-regression result.

### Validation notes

- `pytest tests/test_connection_api.py tests/test_engine_remote_export.py tests/test_performance_regression.py` failed under system Python because the package was not importable.
- `uv run pytest tests/test_connection_api.py tests/test_engine_remote_export.py tests/test_performance_regression.py` collected tests and reported `19 passed, 8 failed`. Several failures are in `tests/test_engine_remote_export.py`; at least part of that file is stale against current config validation (`tests/test_engine_remote_export.py:142-154` omits required `version`).
- Current `git status --short` shows modified `uv.lock` and untracked `config_review.md` in addition to this report; this review did not edit `uv.lock` or `config_review.md`.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Completed the requested review-only deliverable and wrote findings to engine_review.md without modifying source/test files."
    }
  ],
  "changedFiles": [
    "engine_review.md"
  ],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "read plan.md, progress.md, ARCHITECTURE.md, src/duckalog/{engine.py,connection.py,python_api.py,performance.py}",
      "result": "completed with missing inputs",
      "summary": "plan.md and progress.md were absent; architecture and target source files were read."
    },
    {
      "command": "grep for include_secrets, use_connection, performance classes, build/connect call sites",
      "result": "passed",
      "summary": "Confirmed ignored/dead parameters and call-site coverage."
    },
    {
      "command": "pytest tests/test_connection_api.py tests/test_engine_remote_export.py tests/test_performance_regression.py",
      "result": "failed",
      "summary": "System Python could not import duckalog; no tests collected."
    },
    {
      "command": "uv run pytest tests/test_connection_api.py tests/test_engine_remote_export.py tests/test_performance_regression.py",
      "result": "failed",
      "summary": "19 passed, 8 failed; failures concentrated in remote-export tests and stale config fixture."
    },
    {
      "command": "manual uv run python reproductions for hierarchical CatalogConnection and missing-fsspec remote export",
      "result": "completed",
      "summary": "Confirmed hierarchical connection failure and remote URI misclassification when fsspec is unavailable."
    },
    {
      "command": "git status --short; git diff --stat; git diff --cached --stat",
      "result": "passed",
      "summary": "git status shows modified uv.lock and untracked config_review.md plus this report; git diff --cached is empty, so no staged files."
    }
  ],
  "validationOutput": [
    "uv run pytest tests/test_connection_api.py tests/test_engine_remote_export.py tests/test_performance_regression.py: 19 passed, 8 failed",
    "Hierarchical CatalogConnection reproduction: EngineError: Failed to rebuild views: Catalog Error: Table with name child_view does not exist",
    "Missing-fsspec remote export reproduction: EngineError from duckdb.connect on local-looking s3:// path, not intended remote-export dependency error"
  ],
  "residualRisks": [
    "Review was inspection-focused; no fixes were applied by instruction.",
    "uv.lock is modified and config_review.md is untracked outside this review; neither was touched."
  ],
  "noStagedFiles": true,
  "diffSummary": "Added engine_review.md report only; source and tests were not edited.",
  "reviewFindings": [
    "high: src/duckalog/connection.py:141 - connection path restores catalog state without duckalog_results, so Duckalog child catalogs are not attached",
    "high: src/duckalog/engine.py:585 - remote URI detection returns false when fsspec is unavailable, bypassing intended dependency error",
    "medium: src/duckalog/engine.py:461 - build_catalog include_secrets argument is documented but ignored",
    "medium: src/duckalog/engine.py:106 - use_connection path is unfinished/untested and bypasses normal remote/dependency orchestration",
    "medium: src/duckalog/engine.py:758 - SQL execution error wrapping is inconsistent across build phases",
    "low: src/duckalog/connection.py:212 - view creation logic duplicates engine._create_views",
    "low: src/duckalog/connection.py:109 - dead no-op compatibility branch",
    "low: src/duckalog/python_api.py:62 - Python wrapper narrows lower-level connection options and duplicates validation helper",
    "low: src/duckalog/engine.py:236 - unused/nondeterministic ConfigDependencyGraph state",
    "low: src/duckalog/performance.py:109 - RegressionDetector can divide by zero for zero baselines"
  ],
  "manualNotes": "Report written to /Users/volker/coding/libs/duckalog/engine_review.md as requested."
}
```
