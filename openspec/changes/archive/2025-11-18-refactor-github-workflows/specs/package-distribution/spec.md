## MODIFIED Requirements

### Requirement: Automated PyPI Publishing Workflow
The project SHALL provide a GitHub Actions workflow that automatically publishes the package to PyPI when version tags are created, while relying on separate CI test workflows for full compatibility coverage.

#### Scenario: Automatic release on version tag
- **WHEN** a developer creates a version tag (e.g., `v1.0.0`) and pushes it to the main branch
- **THEN** the GitHub Actions publishing workflow SHALL trigger, build the package, and publish the validated artifacts to the configured PyPI repository
- **AND** it SHALL assume that the CI test workflow has already run and passed for that commit.

#### Scenario: Manual release capability
- **WHEN** a developer needs to trigger a release manually without creating a tag
- **THEN** they MAY use a `workflow_dispatch` entry point to initiate publishing with specified parameters (for example, TestPyPI vs PyPI, or dry-run)
- **AND** the publishing workflow SHALL still enforce that only built artifacts from a passing CI run are published.

#### Scenario: Package validation before publish
- **WHEN** the publishing workflow runs the build process
- **THEN** it SHALL validate the built distributions using `twine check`
- **AND** run at least one smoke test (for example, installing from the wheel and invoking the CLI) before attempting to publish.

### Requirement: Multi-Python Version Support
The automation SHALL test the package across supported Python versions in CI while allowing the publishing workflow itself to run on a single default Python version.

#### Scenario: Cross-version compatibility testing in CI
- **WHEN** the main CI test workflow runs on the default branch or pull requests
- **THEN** it SHALL execute the test suite for Python versions 3.9, 3.10, 3.11, and 3.12
- **AND** it SHALL provide clear status for each Python version in the matrix.

#### Scenario: Publish workflow uses validated artifacts
- **WHEN** the publishing workflow is triggered by a version tag or manual dispatch
- **THEN** it MAY run on a single default Python version for building and publishing
- **AND** it SHALL rely on the CI test workflow (and/or branch protection rules) to guarantee cross-version compatibility before tags are created.

