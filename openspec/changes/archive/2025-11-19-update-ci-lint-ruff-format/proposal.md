# Refine CI Linting and Ruff Formatting

## Why

Running the `Tests` GitHub workflow currently fails at the linting stage when `ruff format --check` detects files that would be reformatted. This makes CI brittle for contributors:

- A small formatting drift (e.g., from editing without Ruff) causes the entire lint job to fail, even when code is otherwise correct.
- Local tooling already supports auto-formatting with Ruff, but the CI workflow treats formatting as a hard gate.
- The failure message can be confusing when developers expect mypy or pytest issues but see Ruff formatting output instead.

We want CI to enforce meaningful linting and type-checking without making minor formatting discrepancies a constant source of red builds, while still encouraging consistent formatting across the project.

## What Changes

- Clarify the role of Ruff in CI:
  - Keep `ruff check` as a **hard gate** for lint-level issues.
  - Treat `ruff format` as **developer tooling** and/or an advisory check, not a mandatory blocker for every CI run.
- Update the CI specification (`ci-workflows`) to:
  - Explicitly distinguish between linting (must pass) and formatting (may be advisory/non-blocking).
  - Allow CI to run `ruff format --check` in a way that can be relaxed (e.g., non-fatal or only on designated branches) without violating the spec.
- Provide guidance in tasks for:
  - Adjusting `.github/workflows/tests.yml` so that:
    - `ruff check` continues to fail on genuine lint issues.
    - Formatting checks can be bypassed or made non-fatal where appropriate (for example, running `ruff format --check` but not failing the entire job, or limiting it to main branch).
  - Documenting developer workflow for running `ruff format` locally (pre-commit, IDE, or explicit commands).

## Impact

- **Developer experience**: Fewer frustrating CI failures for purely cosmetic formatting issues; contributors can fix formatting on their own time while still getting clear signals about real lint/type errors.
- **Spec clarity**: The `ci-workflows` spec will clearly state which checks are mandatory vs. advisory, making it easier to evolve CI behavior without guessing.
- **Consistency**: Ruff remains the single source of truth for style, but CI can be configured to enforce it in a way that matches the project's tolerance for strictness.

## Out of Scope

- Changing or removing Ruff as the primary linter.
- Replacing mypy or altering the type-checking strategy.
- Modifying publish/versioning workflows; this proposal is focused on CI linting behavior only.

