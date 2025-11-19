# Improve CLI Typing and Logging Type Safety

## Why

Mypy reports several type issues around the CLI layer and logging utilities that, while not breaking runtime behavior, indicate that our type annotations and integrations with third-party libraries could be clearer:

- **Logging (`duckalog.logging_utils`)**:
  - The optional import of `loguru` assigns `None` to a variable that mypy infers as a concrete logger type, leading to “incompatible types in assignment”. This reflects an imprecise type for the logger handle that is intended to be either a loguru logger or an adapter.
- **CLI (`duckalog.cli`)**:
  - Typer’s `Argument(...)` and `Option(...)` helpers are used as default values for parameters annotated as `Path`, `Path | None`, or `bool`. Mypy correctly flags this as an “incompatible default” because the default objects are `ArgumentInfo` / `OptionInfo`, not the annotated types.
  - Typer’s recommended pattern is to use `Annotated[...]` with `Argument(...)` / `Option(...)`, which is more type-checker friendly.
- **Third-party stubs**:
  - Mypy also flags missing stubs for `yaml` (PyYAML), suggesting `types-PyYAML`. This is a tooling concern rather than a code bug, but it clutters the type-checking output and can hide more meaningful issues.

Improving these areas will make our CLI and logging code easier to reason about under static analysis, reduce noise from mypy, and keep integration with Typer and loguru robust.

## What Changes

- **Logging utilities**:
  - Adjust `duckalog.logging_utils` so that:
    - The logger handle used throughout the module has a type that can represent either a loguru logger or a standard-logging-compatible object.
    - Assignments and fallbacks (e.g., setting the logger to `None` when loguru is unavailable) are typed in a way that passes mypy while preserving the runtime behavior described in the `errors-logging` spec.
- **Typer CLI typing**:
  - Refactor CLI function signatures in `duckalog.cli` to follow Typer’s recommended `Annotated[...]` style, or otherwise make the defaults and annotations consistent:
    - Ensure parameters annotated as `Path` / `Path | None` / `bool` have defaults that are type-compatible (via `Annotated` or explicit typing tricks).
    - Keep the public CLI behavior (`duckalog build`, `duckalog generate-sql`, `duckalog validate`) unchanged.
- **Mypy and stub handling**:
  - Decide on a consistent approach to third-party stubs:
    - Prefer installing stubs for core libraries we rely on in type-checked paths (e.g., `types-PyYAML`), or
    - Configure mypy to ignore missing imports for known libraries where full typing is not critical to our guarantees.

## Impact

- **Cleaner mypy output**: Reduces spurious errors about CLI defaults and logger assignment, making real type issues easier to spot.
- **Better long-term maintainability**: Stronger type guarantees on CLI and logging code reduce the risk of regressions when refactoring.
- **Spec alignment**: The `catalog-build` and `errors-logging` specs will capture that CLI and logging surfaces should remain type-checker friendly, without changing their external behavior.

## Out of Scope

- Changing CLI command names, options, or behavior from the user’s perspective.
- Changing how logs are formatted or where they are emitted.
- Enforcing strict stubs for all third-party libraries beyond what is practical for our use cases.

