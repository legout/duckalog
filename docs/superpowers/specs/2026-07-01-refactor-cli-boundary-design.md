# CLI Boundary Simplification Design Spec

Converted from `.execflow/plans/refactor-cli-boundary/spec.md` and `.execflow/plans/refactor-cli-boundary/execplan.md` using the Superpowers brainstorming/spec style.

## Goal

Make CLI help, errors, config loading, and query rendering truthful and shared.

## User-visible outcome

After this change, users following CLI help will be able to invoke filesystem options correctly, broken import graphs will be reported as failures, and contributors will find shared command behavior in focused helpers rather than copied blocks in `cli.py`. The visible proof is command help and CLI tests that reflect real commands and real failure behavior.

## Current context

The Typer CLI entry point is `src/duckalog/cli.py`. Some helper code already exists in `src/duckalog/cli_filesystem.py`, `src/duckalog/cli_imports.py`, and `src/duckalog/cli_display.py`, but the main command functions remain large and repeat config loading, error mapping, and rendering logic. Tests live primarily in `tests/test_cli_filesystem.py`, `tests/test_engine_cli.py`, and `tests/test_cli_query.py`.

## Architecture

First, make the CLI option contract explicit: filesystem options remain Typer global options. Update examples, help expectations, and tests to use `duckalog --fs-protocol ... validate config.yaml` rather than placing filesystem options after subcommands. Do not add command-local aliases in this workstream.

Next, make `show-imports` diagnostic behavior honest. The helper in `cli_imports.py` should propagate missing-file, invalid-config, and remote-fetch failures to the command so Typer exits non-zero with an actionable message. It may still render partial graph context, but partial success must be labeled as failure.

Then extract repeated path validation and config error handling from `run`, `generate_sql`, and `validate` into a small internal helper. Extract query-result rendering into `cli_display.py` so `run --query`, `query`, and the interactive shell use one path.

Finally, repair tests. Replace stale `build` command assertions with canonical `run` coverage. Do not support `python -m duckalog.cli` in this workstream; tests must use the installed `duckalog` entry point behavior or Typer's test runner.

## Files and responsibilities

- `tests/test_cli_filesystem.py`
- `tests/test_engine_cli.py`
- `tests/test_cli_query.py`
- `.execflow/PLANS.md`
- `cli.py`
- `src/duckalog/cli.py:49-136`
- `src/duckalog/cli.py:210-211`
- `src/duckalog/cli_imports.py:58-96`
- `src/duckalog/cli.py:569-590`
- `src/duckalog/cli.py`
- `src/duckalog/cli_filesystem.py`
- `src/duckalog/cli_imports.py`
- `src/duckalog/cli_display.py`
- `cli_imports.py`
- `cli_display.py`
- `cli_review.md`
- `tests_deadcode_review.md`

## Acceptance criteria

- AC1: Filesystem options are documented and tested as global options before the subcommand, for example `duckalog --fs-protocol s3 validate config.yaml`.
- AC2: `show-imports` exits non-zero and reports actionable errors when imports are missing or invalid.
- AC3: Local/remote config existence checks and ConfigError handling are centralized for `run`, `generate-sql`, and `validate`.
- AC4: Query-result rendering is shared between `run --query`, `query`, and interactive mode.
- AC5: Tests no longer invoke the removed `build` command or the unsupported `python -m duckalog.cli` path.

## Constraints

- Constraint 1: Preserve canonical `duckalog run` behavior.
- Constraint 2: Avoid broad CLI rewrites before remote/config contracts are repaired.
- Constraint 3: Keep Typer as the CLI framework.

## Non-goals

- Non-goal 1: Redesign every CLI command.
- Non-goal 2: Replace Typer.
- Non-goal 3: Implement live cloud CLI tests.

## Error handling and safety

Use the existing domain error type already used by the surrounding module. Security-sensitive paths must fail closed. CLI and dashboard tests must assert concrete error messages or event payloads instead of swallowing broad exceptions. Remote/cloud behavior must be tested with fakes or mocks, not live services.

## Testing strategy

Use TDD. First add the focused tests named in the original spec. Run them and confirm the current tree fails for the expected reason. Implement the smallest repair at the owning boundary. Then run the focused pytest command, `uv run ruff check src/duckalog tests`, and the targeted mypy command when the original spec names one.

## Implementation handoff

Implement with the paired Superpowers plan at `docs/superpowers/plans/2026-07-01-refactor-cli-boundary.md`. Do not start implementation from the old `.execflow` plan unless this Superpowers spec and plan are intentionally updated too.
