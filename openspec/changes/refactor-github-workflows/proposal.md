# Refactor GitHub Workflows

## Why

The current GitHub Actions setup for Duckalog covers testing, security scanning, version automation, changelog generation, and PyPI publishing, but it has grown complex and overlapping:
- The publish workflow re-runs tests and security checks that already exist in other workflows.
- The tests workflow uses an aggressive matrix and auto-generated smoke tests that can hide missing real tests.
- The security workflow runs a large number of overlapping tools, including container and supply-chain scans that are heavy for a library project.
- Version tagging and changelog generation live in separate workflows with duplicated version-detection logic.

This makes CI slower, harder to maintain, and more difficult for contributors to understand at a glance.

## What Changes

- **Clarify workflow responsibilities** so that tests, security scans, release preparation (version + changelog), and publishing each have focused workflows with minimal overlap.
- **Simplify `publish.yml`** to:
  - Build sdist + wheel once on a default Python version.
  - Validate distributions (`twine check`) and run a small smoke test (install + CLI).
  - Rely on the main CI test workflow for cross-version test coverage instead of duplicating a full matrix.
- **Align `tests.yml` with CI expectations** by:
  - Keeping a dedicated lint/type-check job (e.g., Ruff + mypy) on the default Python version.
  - Running tests across supported Python versions via a matrix.
  - Failing the workflow when tests fail, and avoiding auto-generated placeholder tests.
- **Right-size `security.yml`** by:
  - Keeping a curated set of high-value scans: secrets, dependency vulnerabilities, and security-focused static analysis.
  - Avoiding redundant or experimental tools (e.g., multiple overlapping scanners, container images, or provenance checks) unless justified in a separate workflow.
- **Reduce duplication in release workflows** by:
  - Ensuring version change detection logic is not reimplemented in multiple workflows.
  - Allowing changelog automation and version tagging to share version information while still satisfying existing version-automation and changelog-automation specs.
- **Update specs** to describe:
  - That cross-version testing happens in CI (tests workflow), while the publish workflow may run on a single default Python.
  - That CI workflows have clear separation of concerns and avoid duplicated test/security work.

## Impact

- **Simpler CI mental model**: contributors can quickly understand which workflow handles tests, security, release prep, and publishing.
- **Faster, more focused runs**: less duplicated test and security work, especially around publish and security workflows.
- **Spec alignment**: `package-distribution` and a new `ci-workflows` spec describe the intended workflow structure, so future changes can stay consistent.
- **No loss of safety**: cross-version testing, basic security scanning, and package validation remain required; they are just performed in clearer places.

## Out of Scope

- Changing the underlying versioning strategy (still based on `pyproject.toml` + semantic versioning).
- Altering the public CLI or package API.
- Implementing new security policies beyond simplifying existing scans and responsibilities.

