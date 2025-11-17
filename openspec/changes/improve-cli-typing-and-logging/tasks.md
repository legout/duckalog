# Improve CLI Typing and Logging Type Safety – Tasks

## 1. Spec Updates

- [x] 1.1 Review `openspec/specs/errors-logging/spec.md` to confirm current logging behavior and secret-handling requirements.
- [x] 1.2 Review `openspec/specs/catalog-build/spec.md` to understand the CLI requirements and how they map to `duckalog.cli`.
- [x] 1.3 Add spec deltas to:
  - Clarify that logging backends (loguru vs. stdlib) MUST present a consistent logger interface to the rest of the code.
  - Clarify that CLI entry points SHOULD remain type-checker friendly and follow the underlying framework’s best practices.

## 2. Logging Utils Changes

- [x] 2.1 Update `duckalog.logging_utils` to:
  - Use a logger type that can explicitly represent the presence or absence of loguru.
  - Avoid assignments that mypy flags as incompatible while preserving runtime behavior.
- [x] 2.2 Verify that debug and info logging still satisfy the `errors-logging` spec (including secret redaction).
- [x] 2.3 Add or adjust tests (or mypy strictness) to ensure the new logger typing is exercised.

## 3. CLI Typing Changes

- [x] 3.1 Refactor `duckalog.cli` function signatures to:
  - Use Typer’s `Annotated[...]` pattern or equivalent, so that default values and type annotations are compatible.
  - Keep CLI commands and options unchanged from the user’s perspective.
- [x] 3.2 Run `uv run mypy src/duckalog/cli.py` (or `src/duckalog`) to confirm CLI-related mypy errors are resolved.

## 4. Stub and Tooling Decisions

- [x] 4.1 Decide whether to install `types-PyYAML` (and any other critical stubs) as part of the dev environment, or to configure mypy to ignore missing imports for `yaml` and similar libraries.
- [x] 4.2 Update tooling configuration (e.g., `pyproject.toml` mypy settings or dev dependencies) accordingly.

## 5. Validation

- [x] 5.1 Run `uv run mypy src/duckalog` and confirm that logging and CLI-related errors are resolved.
- [ ] 5.2 Trigger the `Tests` workflow to ensure CLI and logging behavior remain correct under the new typing.
