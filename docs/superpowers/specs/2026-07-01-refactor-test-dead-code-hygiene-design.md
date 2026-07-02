# Test and Dead-Code Hygiene Design Spec

Converted from `.execflow/plans/refactor-test-dead-code-hygiene/spec.md` and `.execflow/plans/refactor-test-dead-code-hygiene/execplan.md` using the Superpowers brainstorming/spec style.

## Goal

Remove stale abstractions, stale docs/tests, and duplicated fixtures after contract repairs.

## User-visible outcome

After this change, contributors will see fewer dead branches, fewer stale names, and smaller tests that still prove the same behavior. This is not the first workstream to implement; it is the cleanup pass that follows security, remote config, runtime, and CLI contract repair. The visible proof is a cleaner source tree, fewer obvious mypy errors in touched files, and tests that no longer pass by catching every exception.

## Current context

This plan covers cleanup across `src/duckalog/`, `tests/`, `ARCHITECTURE.md`, and docs/examples as needed. It is intentionally dependent on the behavioral plans because some currently stale tests should be replaced with better tests while those behaviors are fixed. The review identified examples including unused `DefaultEnvProcessor`, ignored parameters in config loading and SQL file loading, stale `build` command tests, duplicated YAML fixtures, and stale architecture references.

## Architecture

Start with a fresh inventory after prior plans land. Use `rg` and Python AST scripts to identify definitions with no production callers, but verify each candidate manually because tests and public APIs can be valid callers. Remove dead parameters only when there is no compatibility reason to keep them. For public or semi-public names, prefer a deprecation decision over silent deletion.

Update documentation and architecture references to match the current tree. Remove references to files that no longer exist and commands that are no longer supported. Keep `ARCHITECTURE.md` focused on actual boundaries and current open questions.

Consolidate tests by introducing local factory helpers for repeated config YAML patterns, especially in `tests/test_config.py` and `tests/test_config_imports.py`. Remove stale `build` command tests or convert them to canonical `run` tests when they are outside the CLI boundary plan.

## Files and responsibilities

- `.execflow/PLANS.md`
- `file.py`
- `remote.py`
- `ARCHITECTURE.md`
- `tests/test_config.py`
- `src/duckalog/`
- `tests/`
- `tests/test_config_imports.py`
- `tests_deadcode_review.md`
- `cli_review.md`
- `tests/conftest.py`

## Acceptance criteria

- AC1: Dead abstractions identified in the review are removed or justified with live callers/tests.
- AC2: Stale documentation references to removed files, and removed commands are updated.
- AC3: Repeated test YAML blocks and helper functions are consolidated without reducing coverage.
- AC4: Mypy error count on touched modules decreases, especially obvious annotation drift.
- AC5: Full ruff check passes and targeted tests continue passing.

## Constraints

- Constraint 1: Do this after or alongside behavior plans so tests are not consolidated around broken behavior.
- Constraint 2: Do not remove public API without an explicit compatibility decision.
- Constraint 3: Keep cleanup PRs reviewable and reversible.

## Non-goals

- Non-goal 1: Add new features.
- Non-goal 2: Rewrite the entire test suite.
- Non-goal 3: Make project-wide mypy perfect in one pass.

## Error handling and safety

Use the existing domain error type already used by the surrounding module. Security-sensitive paths must fail closed. CLI tests must assert concrete error messages or event payloads instead of swallowing broad exceptions. Remote/cloud behavior must be tested with fakes or mocks, not live services.

## Testing strategy

Use TDD. First add the focused tests named in the original spec. Run them and confirm the current tree fails for the expected reason. Implement the smallest repair at the owning boundary. Then run the focused pytest command, `uv run ruff check src/duckalog tests`, and the targeted mypy command when the original spec names one.

## Implementation handoff

Implement with the paired Superpowers plan at `docs/superpowers/plans/2026-07-01-refactor-test-dead-code-hygiene.md`. Do not start implementation from the old `.execflow` plan unless this Superpowers spec and plan are intentionally updated too.
