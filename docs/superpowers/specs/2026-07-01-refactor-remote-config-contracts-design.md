# Remote Config Contracts Design Spec

Converted from `.execflow/plans/refactor-remote-config-contracts/spec.md` and `.execflow/plans/refactor-remote-config-contracts/execplan.md` using the Superpowers brainstorming/spec style.

## Goal

Restore local/remote config loading parity through the public load_config() API.

## User-visible outcome

After this change, users can load a config from a remote URI through the same `load_config()` function they use for local files. Remote configs will no longer fail immediately with a `TypeError`, and documented import behavior will work in mocked tests without depending on cloud services. The visible proof is a remote root config importing another remote config and producing the merged validated `Config` object.

## Current context

Duckalog has two config loading paths. The local path starts in `src/duckalog/config/api.py` and calls `src/duckalog/config/resolution/imports.py`, which handles imports, `.env` interpolation, SQL-file processing, and path resolution. The remote path is implemented in `src/duckalog/remote_config.py`; it fetches URI content through fsspec or a custom filesystem and currently validates directly. The review found that these two paths do not share the same contract.

## Architecture

Start with tests in `tests/test_remote_config.py` that call `load_config()` with a fake remote URI and assert no `TypeError`. Then add tests for remote imports: a fake filesystem should return a root YAML with `imports: [s3://bucket/base.yaml]` and a child YAML with one view; the result should include both views. Also add a test for `load_dotenv=True` using a temporary local `.env` and remote content referencing `${env:VAR}`.

In implementation, make `load_config_from_uri()` accept a `context` parameter if remote loading needs the same request cache and import context used by local loading. Prefer reusing `_load_config_with_imports()` or extracting a shared content-loading adapter rather than adding a second import resolver. Fix `validate_filesystem()` so a missing/empty protocol error is not caught and ignored. Keep the documented `github://` behavior by adding it to the scheme requirements and covering it with mocked/fake-filesystem tests. Live GitHub access remains outside this workstream.

## Files and responsibilities

- `tests/test_remote_config.py`
- `tests/test_config_imports.py`
- `tests/test_cli_remote.py`
- `config/api.py`
- `remote_config.py`
- `.execflow/PLANS.md`
- `src/duckalog/config/api.py:30-41`
- `src/duckalog/remote_config.py:286-294`
- `src/duckalog/remote_config.py:409-420`
- `src/duckalog/config/api.py`
- `src/duckalog/config/resolution/imports.py`
- `src/duckalog/remote_config.py`
- `config_review.md`
- `sql_remote_review.md`
- `cli_review.md`

## Acceptance criteria

- AC1: `duckalog.config.load_config('s3://...')` delegates without `TypeError`.
- AC2: Remote configs support documented remote imports, including transitive import resolution and cycle detection consistent with local configs.
- AC3: `load_dotenv=True` has defined, tested behavior for remote configs.
- AC4: Documented `github://` URIs are supported through the same fsspec-backed remote-loading path and covered by mocked tests.
- AC5: Filesystem validation rejects missing or empty protocols instead of swallowing the error.

## Constraints

- Constraint 1: Keep `load_config()` as the public entry point.
- Constraint 2: Preserve custom filesystem injection.
- Constraint 3: Avoid network-dependent tests; use fake filesystems/mocks.

## Non-goals

- Non-goal 1: Rewrite all import-resolution internals.
- Non-goal 2: Add live cloud integration tests.
- Non-goal 3: Change the config schema.

## Error handling and safety

Use the existing domain error type already used by the surrounding module. Security-sensitive paths must fail closed. CLI and dashboard tests must assert concrete error messages or event payloads instead of swallowing broad exceptions. Remote/cloud behavior must be tested with fakes or mocks, not live services.

## Testing strategy

Use TDD. First add the focused tests named in the original spec. Run them and confirm the current tree fails for the expected reason. Implement the smallest repair at the owning boundary. Then run the focused pytest command, `uv run ruff check src/duckalog tests`, and the targeted mypy command when the original spec names one.

## Implementation handoff

Implement with the paired Superpowers plan at `docs/superpowers/plans/2026-07-01-refactor-remote-config-contracts.md`. Do not start implementation from the old `.execflow` plan unless this Superpowers spec and plan are intentionally updated too.
