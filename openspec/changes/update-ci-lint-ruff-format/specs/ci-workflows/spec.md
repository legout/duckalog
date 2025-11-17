## MODIFIED Requirements

### Requirement: Dedicated Test Workflow

#### Scenario: Lint and type-check
- **WHEN** a pull request targets a protected branch or code is pushed to `main` or `develop`
- **THEN** the CI workflow SHALL run linting and type-checking steps (for example, Ruff and mypy) on the default Python version
- **AND** fail the run when lint or type errors are detected
- **AND** MAY run formatting checks (for example, `ruff format --check`) in advisory or non-blocking mode.

### Requirement: Workflow Separation of Concerns

#### Scenario: Clear ownership of checks
- **WHEN** maintainers update CI workflows
- **THEN** each workflow (tests, security, publishing, release-prep) SHALL have a clearly scoped responsibility
- **AND** linting failures (e.g., `ruff check`, mypy) SHOULD remain hard gates for code quality
- **AND** formatting-only checks (e.g., `ruff format --check`) MAY be configured to avoid blocking CI (for example, by running on specific branches, in scheduled jobs, or in non-fatal steps).
