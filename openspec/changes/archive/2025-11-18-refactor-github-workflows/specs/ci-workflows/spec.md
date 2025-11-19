# ci-workflows Specification

## Purpose
Define a maintainable structure for GitHub Actions workflows that handle testing, linting, and security scanning for Duckalog without unnecessary duplication or over-complexity.

## Requirements

## ADDED Requirements

### Requirement: Dedicated Test Workflow
The project SHALL provide a dedicated CI workflow for tests and linting that runs on pull requests and protected branches.

#### Scenario: Lint and type-check
- **WHEN** a pull request targets a protected branch or code is pushed to `main` or `develop`
- **THEN** the CI workflow SHALL run linting and type-checking steps (for example, Ruff and mypy) on the default Python version
- **AND** fail the run when lint or type errors are detected.

#### Scenario: Cross-version test matrix
- **WHEN** the test job runs on CI
- **THEN** it SHALL execute the test suite across the supported Python versions (3.9–3.12)
- **AND** fail the workflow if any matrix entry fails.

#### Scenario: No hidden or auto-generated tests
- **WHEN** the CI workflow runs
- **THEN** it SHALL execute the repository’s committed test suite
- **AND** it SHALL NOT silently auto-generate placeholder tests that could mask missing coverage.

### Requirement: Focused Security Workflow
The project SHALL provide a security workflow that focuses on a curated set of high-value scans instead of duplicative or experimental tools.

#### Scenario: Secrets and dependency scanning
- **WHEN** the security workflow runs on schedule or on demand
- **THEN** it SHALL perform secret scanning and dependency vulnerability scanning using supported tools
- **AND** produce artifacts or reports that can be reviewed from the workflow run.

#### Scenario: Static analysis for code security
- **WHEN** the security workflow runs
- **THEN** it SHALL run at least one static analysis tool configured for security-focused rules on the Python source tree
- **AND** fail or warn based on project-defined severity thresholds.

#### Scenario: Avoid unnecessary container and supply-chain scans
- **WHEN** configuring security workflows
- **THEN** the project MAY omit container image scanning, in-toto/SLSA provenance verification, or other heavy-weight supply-chain tooling
- **AND** reserve such scans for separate, explicitly justified workflows if needed.

### Requirement: Workflow Separation of Concerns
The CI workflows SHALL avoid duplicating responsibilities across testing, publishing, and security pipelines.

#### Scenario: No duplicate test matrices in publish workflow
- **WHEN** the publishing workflow is defined
- **THEN** it SHALL NOT duplicate the full test matrix already executed by the CI test workflow
- **AND** instead rely on branch protections and status checks from the CI test workflow before tags are created.

#### Scenario: Clear ownership of checks
- **WHEN** maintainers update CI workflows
- **THEN** each workflow (tests, security, publishing, release-prep) SHALL have a clearly scoped responsibility
- **AND** overlapping checks (for example, the same Bandit invocation in multiple jobs) SHOULD be consolidated into a single owner workflow.

