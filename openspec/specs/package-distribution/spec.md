# package-distribution Specification

## Purpose
TBD - created by archiving change add-pypi-publish-workflow. Update Purpose after archive.
## Requirements
### Requirement: Automated PyPI Publishing Workflow
The project SHALL provide a GitHub Actions workflow that automatically publishes the package to PyPI when version tags are created.

#### Scenario: Automatic release on version tag
- **WHEN** a developer creates a version tag (e.g., v1.0.0) and pushes it to the main branch
- **THEN** the GitHub Actions workflow triggers, builds the package, runs tests, and publishes to PyPI

#### Scenario: Manual release capability
- **WHEN** a developer needs to trigger a release manually without creating a tag
- **THEN** they can use the workflow_dispatch feature to initiate publishing with specified parameters

#### Scenario: Package validation before publish
- **WHEN** the workflow runs the build process
- **THEN** it SHALL validate the package using twine check and run basic smoke tests before attempting to publish

### Requirement: Multi-Python Version Support
The publishing workflow SHALL test and build the package across multiple Python versions to ensure compatibility.

#### Scenario: Cross-version compatibility testing
- **WHEN** the workflow executes on Python versions 3.9, 3.10, 3.11, and 3.12
- **THEN** it SHALL successfully build and test the package on all specified versions

#### Scenario: Version matrix reporting
- **WHEN** the workflow runs across the Python version matrix
- **THEN** it SHALL provide clear status indicators for each Python version tested

### Requirement: Secure Credential Management
The PyPI publishing workflow SHALL use secure methods for handling PyPI credentials and API tokens.

#### Scenario: GitHub Secrets usage
- **WHEN** the workflow needs to authenticate with PyPI
- **THEN** it SHALL use GitHub Secrets (specifically PYPI_API_TOKEN) and never expose credentials in logs or error messages

#### Scenario: Secure token handling
- **WHEN** the workflow accesses PyPI credentials
- **THEN** it SHALL use the official PyPI publishing action which securely handles API tokens without logging sensitive information

### Requirement: Release Validation and Error Handling
The publishing workflow SHALL include proper validation and error handling to prevent failed releases.

#### Scenario: Package validation failure
- **WHEN** the package fails validation checks (twine check, tests, etc.)
- **THEN** the workflow SHALL stop the publishing process and provide clear error messages

#### Scenario: Network or API failures
- **WHEN** PyPI API calls fail due to network issues or API problems
- **THEN** the workflow SHALL retry appropriate operations and provide meaningful error messages for manual intervention

### Requirement: Package Build and Distribution
The workflow SHALL build both source distribution (sdist) and wheel distributions for optimal package compatibility.

#### Scenario: Universal wheel building
- **WHEN** the workflow builds the package
- **THEN** it SHALL create both sdist and wheel formats to support different installation methods

#### Scenario: Package integrity verification
- **WHEN** the package is built successfully
- **THEN** the workflow SHALL verify package integrity using twine check before attempting to publish

### Requirement: Release Documentation Integration
The publishing workflow SHALL integrate with existing project documentation and release processes.

#### Scenario: Documentation updates
- **WHEN** a new version is published
- **THEN** the workflow SHALL trigger any necessary documentation updates (if configured) and provide release information

#### Scenario: Installation instructions
- **WHEN** users want to install the package
- **THEN** the README and documentation SHALL include clear pip install instructions using the published PyPI package name

### Requirement: Workflow Security and Permissions
The publishing workflow SHALL follow GitHub Actions security best practices with appropriate permissions and access controls.

#### Scenario: Minimal permissions
- **WHEN** the workflow executes
- **THEN** it SHALL request only the minimum required GitHub permissions needed for publishing

#### Scenario: Protected branch deployment
- **WHEN** a release is triggered from a protected branch
- **THEN** the workflow SHALL respect branch protection rules and require appropriate approvals if configured

### Requirement: Version Tag Management
The publishing workflow SHALL follow semantic versioning conventions and proper tag management practices.

#### Scenario: Version tag format validation
- **WHEN** a tag is pushed to trigger the workflow
- **THEN** it SHALL validate that the tag follows the v*.*.* format before proceeding with publishing

#### Scenario: Version consistency verification
- **WHEN** the workflow starts
- **THEN** it SHALL verify that the version in pyproject.toml matches the tag version to prevent mismatches


### ADDED Requirement: Automated Version Change Detection
The system SHALL automatically detect when version in `pyproject.toml` changes and trigger automated tagging workflow.

#### Scenario: Version increment detection
- **WHEN** a developer pushes a change to `pyproject.toml` with an updated version field
- **THEN** workflow SHALL extract new version and compare it with the latest tagged version
- **AND** proceed with tag creation only if the new version is greater than the latest tag

#### Scenario: No version change
- **WHEN** `pyproject.toml` is modified but the version field remains unchanged
- **THEN** workflow SHALL detect no version change and skip tag creation
- **AND** exit gracefully without triggering the publish workflow

### ADDED Requirement: Automated Git Tag Creation
The system SHALL automatically create and push Git tags that correspond to the version in `pyproject.toml`.

#### Scenario: Standard version tagging
- **WHEN** a version change is detected and validated
- **THEN** workflow SHALL create a Git tag in the format `v{version}` (e.g., `v0.1.0`)
- **AND** push the tag to the repository to trigger the existing publish.yml workflow

#### Scenario: Tag conflict handling
- **WHEN** attempting to create a tag that already exists
- **THEN** workflow SHALL detect the conflict and fail with a clear error message
- **AND** provide guidance on how to resolve the version conflict

### ADDED Requirement: Version Format Validation
The system SHALL validate that version numbers in `pyproject.toml` follow semantic versioning before creating tags.

#### Scenario: Valid semantic version
- **WHEN** version in `pyproject.toml` follows semantic versioning (e.g., `1.2.3`, `0.1.0`)
- **THEN** workflow SHALL accept the version and proceed with tag creation

#### Scenario: Invalid version format
- **WHEN** version in `pyproject.toml` does not follow semantic versioning
- **THEN** workflow SHALL reject the version and fail with a descriptive error message
- **AND** provide examples of valid version formats

### ADDED Requirement: Manual Override Capability
The system SHALL provide manual override options for special cases that require bypassing automated checks.

#### Scenario: Force tag creation
- **WHEN** a developer needs to recreate a tag or handle special release scenarios
- **THEN** they SHALL be able to manually trigger the workflow with a force flag
- **AND** bypass certain validation checks while maintaining safety constraints

#### Scenario: Dry run testing
- **WHEN** developers want to test the tagging logic without creating actual tags
- **THEN** they SHALL be able to run the workflow in dry-run mode
- **AND** see what actions would be taken without executing them

### ADDED Requirement: Workflow Security and Permissions
The automated tagging workflow SHALL follow GitHub Actions security best practices with minimal required permissions.

#### Scenario: Minimal permissions
- **WHEN** the workflow executes
- **THEN** it SHALL request only the minimum permissions needed (contents: write for tag operations)
- **AND** use the principle of least privilege

#### Scenario: Branch protection
- **WHEN** the workflow is triggered
- **THEN** it SHALL only run on the main branch or other protected release branches
- **AND** respect existing branch protection rules

### ADDED Requirement: Integration with Automated Tagging System
The automated tagging workflow SHALL integrate seamlessly with the existing publishing workflow without breaking existing functionality.

#### Scenario: Workflow triggering
- **WHEN** an automated tag is created and pushed
- **THEN** the existing publish.yml workflow SHALL be triggered via its tag-based trigger
- **AND** execute all existing jobs (test, build, publish, create-github-release)

#### Scenario: Backward compatibility
- **WHEN** developers continue to use existing manual tagging or workflow_dispatch triggers
- **THEN** the publish.yml workflow SHALL continue to function as before
- **AND** all existing functionality remains unchanged

### ADDED Requirement: Automated Tagging Integration
The automated tagging system SHALL provide all functionality required for seamless version-based releases.

#### Scenario: End-to-end automated release
- **WHEN** a developer updates the version in `pyproject.toml` and pushes to the main branch
- **THEN** the system SHALL automatically extract the version, validate it, create an appropriate Git tag, and trigger the complete publishing pipeline
- **AND** the published package version SHALL always match the Git tag version

#### Scenario: Manual override integration
- **WHEN** developers need to bypass automated checks for special cases
- **THEN** they SHALL be able to use manual workflow_dispatch triggers with force and dry-run options
- **AND** the system SHALL provide clear feedback about actions taken
