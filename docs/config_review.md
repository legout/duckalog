# Duckalog CONFIG Layer Deep Review

Inputs requested: `plan.md`, `progress.md`, `ARCHITECTURE.md`, and the focused config-layer files. `plan.md` and `progress.md` were not present at the requested paths; review proceeded from the code and `ARCHITECTURE.md`.

## Review

### Correct

- `src/duckalog/config/models.py:429-487` centralizes view-definition validation: it rejects missing definitions, multiple SQL sources, and source-specific missing fields before engine code sees a `ViewConfig`.
- `src/duckalog/config/models.py:928-1118` validates cross-config uniqueness and references for views, Iceberg catalogs, semantic models, attachment aliases, base views, and joins. This matches the architecture requirement that config models guarantee structural validity before engine use (`ARCHITECTURE.md:28-33`).
- `src/duckalog/config/api.py:65-75` validates the injected filesystem interface before using it for local config loading.
- `src/duckalog/config/loading/sql.py:181-190` preserves view order while processing SQL file loads in parallel by collecting futures in input order rather than append-on-completion order.
- `ARCHITECTURE.md:56-60` already identifies `duckalog.config.validators` as shallow; the code inspection confirms that assessment.

### Fixed

- None. This was review-only; no source files were edited.

### Blocker

1. **critical — remote config loading through the public API is currently broken.**
   - Evidence: `src/duckalog/config/api.py:30-41` imports `load_config_from_uri()` and calls it with `context=context` at `src/duckalog/config/api.py:40`. The actual remote loader signature in `src/duckalog/remote_config.py:286-294` has no `context` parameter.
   - Validation evidence: `uv run python - <<'PY' ... load_config('s3://bucket/config.yaml') ... PY` returned `TypeError load_config_from_uri() got an unexpected keyword argument 'context'`.
   - Rationale: `load_config()` is the public entry point described in `ARCHITECTURE.md:35-40`; any remote URI passed through that entry point fails before remote fetching begins.

2. **critical — attachment path resolution assumes security validation that the resolver does not perform.**
   - Evidence: `src/duckalog/config/validators.py:219-223` and `src/duckalog/config/validators.py:241-245` resolve DuckDB/SQLite attachment paths and comments state security validation is handled inside `resolve_relative_path()`. Duckalog attachment `config_path` and `database` follow the same unvalidated pattern at `src/duckalog/config/validators.py:263-284`.
   - Evidence: `src/duckalog/config/security/path.py:237-252` shows `resolve_relative_path()` only resolves the path via `DefaultPathResolver._resolve_path_core()` and returns it; it does not call `validate_path_security()` or `is_within_allowed_roots()`.
   - Contrast: view URIs do an explicit security check at `src/duckalog/config/validators.py:185-191`; attachment paths do not.
   - Validation evidence: direct inspection command returned a resolved traversal path rather than an error for `resolve_relative_path('../../../etc/passwd', config_dir)`.
   - Rationale: the architecture assigns root-based path-security validation to this layer (`ARCHITECTURE.md:49-54`). The current attachment path flow can materialize traversal paths outside the config root.

### Note

1. **major — imported config relative paths are resolved against the top-level config directory, not the imported file directory.**
   - Evidence: local import loading in `src/duckalog/config/resolution/imports.py:426-480` parses and interpolates the imported file into `imported_dict`. SQL-file references receive the imported file path at `src/duckalog/config/resolution/imports.py:482-510`, but general view URIs and attachment paths are not resolved there.
   - Evidence: after all imports are merged, `_load_config_with_imports()` validates the combined config and calls `_resolve_paths_in_config(config, config_path)` once at `src/duckalog/config/resolution/imports.py:840-846`; `config_path` is the top-level `file_path` created at `src/duckalog/config/resolution/imports.py:570-571`.
   - Rationale: imported `views[].uri`, `attachments.duckdb[].path`, `attachments.sqlite[].path`, and Duckalog attachment paths keep their raw relative strings until the final top-level resolution pass, so they are interpreted relative to the wrong file and security boundaries are checked against the wrong root.

2. **major — the import resolver is overcomplex and duplicates execution paths.**
   - Evidence: `_load_config_with_imports()` spans `src/duckalog/config/resolution/imports.py:550-858` and mixes dotenv discovery, file I/O, parsing, interpolation, import graph expansion, concurrency, merging, validation, path resolution, and SQL loading.
   - Evidence: global imports and section-specific imports duplicate nearly the same pattern: pattern expansion, ordered-path construction, threaded/sequential loading, and merging at `src/duckalog/config/resolution/imports.py:677-738` and `src/duckalog/config/resolution/imports.py:740-803`.
   - Rationale: this concentrates multiple architecture responsibilities from `ARCHITECTURE.md:42-47` in one function and increases the likelihood of divergence between global and section import behavior.

3. **major — targeted mypy run fails with 13 errors in the reviewed files.**
   - Evidence: `uv run mypy src/duckalog/config/models.py src/duckalog/config/api.py src/duckalog/config/resolution/imports.py src/duckalog/config/resolution/env.py src/duckalog/config/security/path.py src/duckalog/config/validators.py src/duckalog/config/loading/sql.py src/duckalog/config/__init__.py` reported 13 errors.
   - Evidence examples: `src/duckalog/config/api.py:33` passes unexpected `context`; `src/duckalog/config/resolution/imports.py:236`, `:258`, and `:273` return invariant list types; `src/duckalog/config/resolution/imports.py:730` and `:793` need dict annotations; `src/duckalog/config/models.py:992`, `:999`, and `:1006` reuse a loop variable inferred from `DuckDBAttachment`; `src/duckalog/config/resolution/env.py:240-242` returns/cache-types `dict[str, str | None]` where `dict[str, str]` is declared; `src/duckalog/config/security/path.py:343` assigns `Path | None` into a `Path` variable.
   - Rationale: the type errors align with real API drift in `api.py` and add review friction across core config modules.

4. **minor — dead parameters and unused objects add abstraction noise.**
   - Evidence: `src/duckalog/config/resolution/imports.py:550-553` accepts `content` and `format`, but `content` is not used in the function body; `DefaultImportResolver.resolve()` still passes `content` at `src/duckalog/config/resolution/imports.py:871-874`.
   - Evidence: `src/duckalog/config/api.py:83` instantiates `_resolver = DefaultImportResolver(...)` but never uses it before calling `_load_config_with_imports()` directly at `src/duckalog/config/api.py:84-93`.
   - Evidence: `src/duckalog/config/loading/sql.py:14-22` accepts `log_info_func`, but the function body uses `log_debug_func` and never calls `log_info_func`.
   - Evidence: `src/duckalog/config/models.py:1028` builds `_view_by_name`, but no subsequent code reads it.
   - Rationale: these are symptoms of partially retained abstraction seams and increase cognitive load without changing behavior.

5. **minor — duplicated validators in `ViewConfig` perform the same `db_schema` normalization.**
   - Evidence: `src/duckalog/config/models.py:411-418` and `src/duckalog/config/models.py:420-427` are both `@field_validator("db_schema")`, both strip the value, and both reject empty strings with only message wording changed.
   - Rationale: both validators execute on the same field, so the second is redundant and obscures which error message is authoritative.

6. **minor — `config/__init__.py` documentation and facade are stale relative to the actual API.**
   - Evidence: the docstring advertises `load_config_with_context()` and `load_config_with_schema()` at `src/duckalog/config/__init__.py:14-17`, but `__all__` only exports `load_config` for loading at `src/duckalog/config/__init__.py:127-128`.
   - Evidence: the docstring says consolidation eliminated separate modules at `src/duckalog/config/__init__.py:9-10`, while the file still imports from separate path and validator modules at `src/duckalog/config/__init__.py:61-80`.
   - Evidence: the facade signature narrows `path` to `str` at `src/duckalog/config/__init__.py:88-95`, while the implementation accepts `Union[str, Path]` at `src/duckalog/config/api.py:19-27`.
   - Rationale: this public facade no longer accurately documents the current config package surface.

## Validation

- `git status --short` before writing this report showed a pre-existing modified `uv.lock`; final status showed `M uv.lock` plus untracked review-report files, with no staged files.
- `uv run ruff check` on the reviewed files passed with `[]`.
- `uv run mypy` on the reviewed files failed with 13 errors, summarized above.
- `uv run pytest tests/test_config.py tests/test_path_cache.py tests/test_root_based_security.py tests/test_remote_config.py tests/test_custom_filesystem.py -q` failed: 129 passed, 15 failed. Notable config-layer failures include root-based security tests and remote config tests.
- `uv run pytest tests/test_root_based_security.py -q` failed: 2 passed, 7 failed. The test file imports `duckalog.path_resolution` and falls back to placeholder functions when that module is absent (`tests/test_root_based_security.py:9-25`), so part of this failure set reflects stale public import coverage rather than only `config/security/path.py` behavior.

## Residual risks

- This was a static/deep review plus focused validation, not a full repository audit.
- `plan.md` and `progress.md` were unavailable at the requested paths, so no plan/progress context could be incorporated.
- The working tree had a pre-existing `uv.lock` modification before the review began; other untracked review reports are present but were not created by this review.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Completed a review-only CONFIG layer assessment of the requested files and ARCHITECTURE.md without editing source or widening into unrelated layers."
    },
    {
      "id": "criterion-2",
      "status": "satisfied",
      "evidence": "Report includes concrete file:line findings, severity, rationale, and validation command output summaries."
    }
  ],
  "changedFiles": [
    "/Users/volker/coding/libs/duckalog/config_review.md",
    "uv.lock (pre-existing modified file; not edited by this review)",
    "other untracked review-report files present at final status (not created by this review)"
  ],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "git status --short",
      "result": "passed",
      "summary": "Initial status reported pre-existing modified uv.lock; final status reported M uv.lock plus untracked review-report files, and no cached diff."
    },
    {
      "command": "uv run mypy src/duckalog/config/models.py src/duckalog/config/api.py src/duckalog/config/resolution/imports.py src/duckalog/config/resolution/env.py src/duckalog/config/security/path.py src/duckalog/config/validators.py src/duckalog/config/loading/sql.py src/duckalog/config/__init__.py",
      "result": "failed",
      "summary": "13 mypy errors in 6 reviewed files."
    },
    {
      "command": "uv run pytest tests/test_config.py tests/test_path_cache.py tests/test_root_based_security.py tests/test_remote_config.py tests/test_custom_filesystem.py -q",
      "result": "failed",
      "summary": "129 passed, 15 failed."
    },
    {
      "command": "uv run pytest tests/test_root_based_security.py -q",
      "result": "failed",
      "summary": "2 passed, 7 failed."
    },
    {
      "command": "uv run ruff check src/duckalog/config/models.py src/duckalog/config/api.py src/duckalog/config/resolution/imports.py src/duckalog/config/resolution/env.py src/duckalog/config/security/path.py src/duckalog/config/validators.py src/duckalog/config/loading/sql.py src/duckalog/config/__init__.py",
      "result": "passed",
      "summary": "Ruff returned [] for the reviewed files."
    }
  ],
  "validationOutput": [
    "mypy: 13 errors in 6 files; top codes assignment, return-value, var-annotated, call-arg, import-untyped.",
    "pytest focused suite: 129 passed, 15 failed.",
    "pytest root-based security suite: 2 passed, 7 failed.",
    "ruff: []"
  ],
  "residualRisks": [
    "plan.md and progress.md were absent at the requested paths.",
    "uv.lock was already modified before review; other untracked review reports are present at final status; source files were not edited.",
    "Review did not cover the entire repository outside the requested CONFIG focus."
  ],
  "noStagedFiles": true,
  "diffSummary": "Added config_review.md report only; no source or test files edited by this review. Workspace also contains pre-existing/concurrent uv.lock and other review-report changes.",
  "reviewFindings": [
    "critical: src/duckalog/config/api.py:40 - public remote load_config path passes unsupported context keyword to remote_config.load_config_from_uri.",
    "critical: src/duckalog/config/validators.py:219 - attachment path resolution assumes validation inside resolve_relative_path, but src/duckalog/config/security/path.py:237-252 only resolves.",
    "major: src/duckalog/config/resolution/imports.py:840 - imported relative paths are resolved once against the top-level config path after merge.",
    "major: src/duckalog/config/resolution/imports.py:550 - _load_config_with_imports is overlarge and duplicates global/section import processing.",
    "major: reviewed target mypy run failed with 13 errors.",
    "minor: dead parameters/unused objects in api.py, imports.py, loading/sql.py, and models.py.",
    "minor: duplicate db_schema validators in models.py.",
    "minor: stale config/__init__.py facade documentation."
  ],
  "manualNotes": "Findings written to /Users/volker/coding/libs/duckalog/config_review.md."
}
```
