# Refine CI Linting and Ruff Formatting – Tasks

## 1. Spec Updates

- [x] 1.1 Review current `ci-workflows` spec and the `Tests` workflow to understand how `ruff check` and `ruff format --check` are used.
- [x] 1.2 Add or update requirements in `ci-workflows` to distinguish:
  - Mandatory linting (Ruff checks, mypy).
  - Optional or advisory formatting checks (Ruff format).
- [x] 1.3 Document expectations for developer-local formatting (e.g., running `ruff format` or using pre-commit/IDE integration).

## 2. CI Workflow Adjustments

- [x] 2.1 Update `.github/workflows/tests.yml` so that:
  - `ruff check` continues to run and fail the job on lint issues.
  - `ruff format --check` is either:
    - Run in advisory mode (non-fatal), or
    - Scoped to specific branches or scheduled runs, as allowed by the updated spec.
- [x] 2.2 Ensure the lint job’s logging clearly differentiates between lint errors and purely formatting suggestions.
- [x] 2.3 Keep mypy in the lint job and confirm it remains a required gate.

## 3. Validation and Documentation

- [x] 3.1 Run `uv run ruff check src/ tests/` and `uv run ruff format --check src/ tests/` locally to confirm behavior matches the updated CI workflow.
- [ ] 3.2 Trigger the `Tests` GitHub workflow on a feature branch to verify:
  - Lint failures behave as expected.
  - Formatting-only issues do not break CI beyond what the spec allows.
- [x] 3.3 Update CONTRIBUTING/README sections (if needed) to:
  - Show how to run linting and formatting locally.
  - Explain which checks are enforced strictly by CI versus advisory.
