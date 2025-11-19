# Refactor GitHub Workflows – Tasks

## 1. Spec Updates

- [x] 1.1 Review existing specs for `package-distribution`, `version-automation`, and `changelog-automation` to confirm current expectations.
- [x] 1.2 Add a `ci-workflows` spec that defines responsibilities for tests, linting, and security workflows.
- [x] 1.3 Update the `package-distribution` spec so multi-Python testing is clearly owned by CI tests, while the publish workflow can run on a single default Python.

## 2. Workflow Refactor

- [x] 2.1 Simplify `.github/workflows/publish.yml` to:
  - Build sdist + wheel once on the default Python version.
  - Run `twine check` and a smoke test (install from dist and run the CLI).
  - Avoid re-running the full test matrix already covered in CI.
- [x] 2.2 Update `.github/workflows/tests.yml` to:
  - Keep a dedicated lint/type-check job (e.g., Ruff + mypy) on the default Python.
  - Run tests across supported Python versions using a matrix.
  - Fail on test failures and remove auto-generated placeholder tests.
- [x] 2.3 Trim `.github/workflows/security.yml` to:
  - Focus on secret scanning, dependency vulnerability scanning, and security-focused static analysis.
  - Reduce or remove heavy container/supply-chain scans unless explicitly needed in a separate workflow.
- [x] 2.4 Ensure `auto-tag-version.yml` and `auto-generate-changelog.yml` (or their successors) share a single version-detection strategy and do not introduce extra matrix-heavy work.

## 3. Validation and Rollout

- [x] 3.1 Run `openspec validate refactor-github-workflows --strict` and fix any issues.
- [x] 3.2 Test the updated workflows on a feature branch (including tag-based and workflow_dispatch paths).
- [x] 3.3 Update documentation (e.g., CONTRIBUTING or README) to reference the simplified CI and release workflows.
