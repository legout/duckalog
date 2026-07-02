# Catalog Runtime Boundary Design Spec

Converted from `.execflow/plans/refactor-catalog-runtime-boundary/spec.md` and `.execflow/plans/refactor-catalog-runtime-boundary/execplan.md` using the Superpowers brainstorming/spec style.

## Goal

Unify catalog runtime state across engine, Python API, and CLI connection paths.

## User-visible outcome

After this change, the same catalog configuration will behave consistently whether built by the engine, accessed through the Python API, or exercised by the CLI. The most important visible behavior is hierarchical catalogs: a parent config that attaches a child Duckalog config should work from `connect_to_catalog()` and `duckalog run`, not only from the lower-level build helper.

## Current context

The engine layer lives mainly in `src/duckalog/engine.py`. The Python connection layer lives in `src/duckalog/connection.py` and is wrapped by `src/duckalog/python_api.py`. The engine already has helper functions for applying settings, creating secrets, setting up attachments, and creating views. The connection layer imports several of those private helpers but does not reproduce the dependency-building step needed for nested Duckalog attachments.

## Architecture

Begin with tests. Construct a temporary child config with one view, and a parent config that attaches the child under an alias and defines a view selecting from the child. Assert that `duckalog.python_api.connect_to_catalog(parent, force_rebuild=True)` returns a connection that can query the parent view. Add a CLI variant if an existing CLI fixture supports it.

Then fix the shared runtime path. Prefer introducing a small internal runtime object or helper in `engine.py` that prepares nested Duckalog attachment results and applies state. Use it from both `CatalogBuilder` and `CatalogConnection`. Avoid copying more engine-private code into `connection.py`.

Repair remote output classification so remote URI detection does not depend on fsspec being installed. The system should identify `s3://...` as remote first, then raise the intended optional-dependency error when fsspec is missing.

Finally, handle stale API parameters with concrete compatibility decisions. Keep `build_catalog(include_secrets=False)` working because it is documented enough to appear in tests and call sites. Remove the unfinished internal `use_connection` branch from the supported runtime surface unless a direct caller is found during implementation; the new shared runtime helper is the supported path.

## Files and responsibilities

- `tests/test_connection_api.py`
- `tests/test_engine_hierarchical.py`
- `tests/test_engine_remote_export.py`
- `.execflow/PLANS.md`
- `src/duckalog/engine.py:522-553`
- `src/duckalog/engine.py:967-984`
- `src/duckalog/connection.py:141-146`
- `src/duckalog/engine.py:155-159`
- `src/duckalog/engine.py:585-588`
- `src/duckalog/engine.py`
- `src/duckalog/connection.py`
- `src/duckalog/python_api.py`
- `engine.py`
- `connection.py`
- `engine_review.md`
- `cli_review.md`

## Acceptance criteria

- AC1: A parent config with `attachments.duckalog` works through `duckalog.python_api.connect_to_catalog(..., force_rebuild=True)` and the CLI `run` path.
- AC2: Missing fsspec for remote output produces the intended dependency error rather than DuckDB trying to open `s3://...` as a local file.
- AC3: `build_catalog(include_secrets=False)` works as documented and is covered by a focused regression test.
- AC4: The unfinished internal `use_connection` path is removed from the supported surface, or every direct caller is migrated to the shared runtime helper in the same task.
- AC5: View creation logic has one owned implementation shared by engine and connection layers.

## Constraints

- Constraint 1: Preserve existing successful local catalog build behavior.
- Constraint 2: Do not introduce network-dependent tests.
- Constraint 3: Keep DuckDB connection handling centralized and explicit.

## Non-goals

- Non-goal 1: Redesign all engine phases.
- Non-goal 2: Change config schema for attachments.
- Non-goal 3: Replace DuckDB APIs or add a new database abstraction.

## Error handling and safety

Use the existing domain error type already used by the surrounding module. Security-sensitive paths must fail closed. CLI tests must assert concrete error messages or event payloads instead of swallowing broad exceptions. Remote/cloud behavior must be tested with fakes or mocks, not live services.

## Testing strategy

Use TDD. First add the focused tests named in the original spec. Run them and confirm the current tree fails for the expected reason. Implement the smallest repair at the owning boundary. Then run the focused pytest command, `uv run ruff check src/duckalog tests`, and the targeted mypy command when the original spec names one.

## Implementation handoff

Implement with the paired Superpowers plan at `docs/superpowers/plans/2026-07-01-refactor-catalog-runtime-boundary.md`. Do not start implementation from the old `.execflow` plan unless this Superpowers spec and plan are intentionally updated too.
