# version-automation Specification

## Purpose
Automate the process of creating Git tags based on version changes in pyproject.toml to trigger the existing publish.yml workflow.

## ADDED Requirements

### Requirement: Version Change Detection
The system SHALL automatically detect when the version in `pyproject.toml` changes and trigger the tagging workflow.

#### Scenario: Version increment detection
- **WHEN** a developer pushes a change to `pyproject.toml` with an updated version field
- **THEN** the workflow SHALL extract the new version and compare it with the latest tagged version
- **AND** proceed with tag creation only if the new version is greater than the latest tag

#### Scenario: No version change
- **WHEN** `pyproject.toml` is modified but the version field remains unchanged
- **THEN** the workflow SHALL detect no version change and skip tag creation
- **AND** exit gracefully without triggering the publish workflow

### Requirement: Automated Git Tag Creation
The system SHALL automatically create and push Git tags that correspond to the version in `pyproject.toml`.

#### Scenario: Standard version tagging
- **WHEN** a version change is detected and validated
- **THEN** the workflow SHALL create a Git tag in the format `v{version}` (e.g., `v0.1.0`)
- **AND** push the tag to the repository to trigger the existing publish.yml workflow

#### Scenario: Tag conflict handling
- **WHEN** attempting to create a tag that already exists
- **THEN** the workflow SHALL detect the conflict and fail with a clear error message
- **AND** provide guidance on how to resolve the version conflict

### Requirement: Version Format Validation
The system SHALL validate that version numbers in `pyproject.toml` follow semantic versioning before creating tags.

#### Scenario: Valid semantic version
- **WHEN** the version in `pyproject.toml` follows semantic versioning (e.g., `1.2.3`, `0.1.0`)
- **THEN** the workflow SHALL accept the version and proceed with tag creation

#### Scenario: Invalid version format
- **WHEN** the version in `pyproject.toml` does not follow semantic versioning
- **THEN** the workflow SHALL reject the version and fail with a descriptive error message
- **AND** provide examples of valid version formats

### Requirement: Integration with Existing Publishing Workflow
The automated tagging system SHALL integrate seamlessly with the existing publish.yml workflow without breaking existing functionality.

#### Scenario: Workflow triggering
- **WHEN** an automated tag is created and pushed
- **THEN** the existing publish.yml workflow SHALL be triggered via its tag-based trigger
- **AND** execute all existing jobs (test, build, publish, create-github-release)

#### Scenario: Backward compatibility
- **WHEN** developers continue to use existing manual tagging or workflow_dispatch triggers
- **THEN** the publish.yml workflow SHALL continue to function as before
- **AND** all existing functionality remains unchanged

### Requirement: Error Handling and Safety
The system SHALL include proper error handling and safety measures to prevent failed releases and repository inconsistencies.

#### Scenario: Version extraction failure
- **WHEN** the workflow cannot extract the version from `pyproject.toml` due to malformed syntax
- **THEN** the workflow SHALL fail gracefully with a clear error message
- **AND** not create any tags or trigger publishing

#### Scenario: Git operation failures
- **WHEN** Git tag creation or push operations fail due to permissions or network issues
- **THEN** the workflow SHALL provide detailed error information
- **AND** not leave the repository in an inconsistent state

### Requirement: Manual Override Capability
The system SHALL provide manual override options for special cases that require bypassing automated checks.

#### Scenario: Force tag creation
- **WHEN** a developer needs to recreate a tag or handle special release scenarios
- **THEN** they SHALL be able to manually trigger the workflow with a force flag
- **AND** bypass certain validation checks while maintaining safety constraints

#### Scenario: Dry run testing
- **WHEN** developers want to test the tagging logic without creating actual tags
- **THEN** they SHALL be able to run the workflow in dry-run mode
- **AND** see what actions would be taken without executing them

### Requirement: Workflow Security and Permissions
The automated tagging workflow SHALL follow GitHub Actions security best practices with minimal required permissions.

#### Scenario: Minimal permissions
- **WHEN** the workflow executes
- **THEN** it SHALL request only the minimum permissions needed (contents: write for tag operations)
- **AND** use the principle of least privilege

#### Scenario: Branch protection
- **WHEN** the workflow is triggered
- **THEN** it SHALL only run on the main branch or other protected release branches
- **AND** respect existing branch protection rules