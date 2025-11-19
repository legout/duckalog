# changelog-automation Specification

## Purpose
Automate changelog generation and updates based on git diff and commit history when version changes occur.

## Requirements

### ADDED Requirement: Automated Changelog Generation
The system SHALL automatically generate changelog entries when version changes are detected.

#### Scenario: Git diff analysis
- **WHEN** a version change is detected in `pyproject.toml`
- **THEN** system SHALL analyze git diff and commit history since the last version tag
- **AND** extract meaningful change descriptions from commit messages and code changes

#### Scenario: Structured changelog entry generation
- **WHEN** git history analysis is complete
- **THEN** system SHALL generate changelog entries in Keep a Changelog (KCH) format
- **AND** categorize changes (Added, Changed, Fixed, Deprecated, Security, Breaking)
- **AND** include relevant information like commit references and issue links

#### Scenario: CHANGELOG.md integration
- **WHEN** automated changelog entries are generated
- **THEN** system SHALL update the existing CHANGELOG.md file with new entries
- **AND** maintain proper formatting and section organization

#### Scenario: Changelog format validation
- **WHEN** CHANGELOG.md is updated
- **THEN** system SHALL validate that the file follows Keep a Changelog format
- **AND** ensure proper version ordering and entry structure

### ADDED Requirement: Git History Analysis
The system SHALL analyze git commit history and diff to extract change information.

#### Scenario: Commit message parsing
- **WHEN** processing git history for changelog generation
- **THEN** system SHALL parse commit messages to identify change types and scope
- **AND** extract relevant information like issue numbers, PR references, and breaking change indicators

#### Scenario: Code change detection
- **WHEN** analyzing git diff between versions
- **THEN** system SHALL identify modified source files and code changes
- **AND** categorize changes based on impact and scope (feature, bugfix, breaking, etc.)

#### Scenario: Version range analysis
- **WHEN** generating changelog for a specific version range
- **THEN** system SHALL analyze all commits within the specified range
- **AND** generate comprehensive changelog covering the entire development period

### ADDED Requirement: Changelog Workflow Integration
The changelog automation SHALL integrate with the existing version tagging workflow.

#### Scenario: Sequential workflow execution
- **WHEN** a version change is detected and changelog generation is enabled
- **THEN** changelog generation workflow SHALL run after version tagging is complete
- **AND** before the publishing workflow is triggered

#### Scenario: Shared state management
- **WHEN** both version tagging and changelog workflows are active
- **THEN** workflows SHALL share version information and git analysis results
- **AND** coordinate execution to ensure proper sequencing

#### Scenario: Artifact integration
- **WHEN** changelog generation is complete
- **THEN** generated changelog entries SHALL be available to the publishing workflow
- **AND** included in GitHub release notes automatically

### ADDED Requirement: Template-Based Generation
The system SHALL use templates for consistent changelog entry formatting.

#### Scenario: Standard entry template
- **WHEN** generating a standard changelog entry
- **THEN** system SHALL use a consistent template with version, date, change type, and description
- **AND** ensure proper formatting and readability

#### Scenario: Category-based templates
- **WHEN** generating different types of changelog entries
- **THEN** system SHALL provide appropriate templates for each change category
- **AND** maintain consistent structure across all entry types

#### Scenario: Template customization
- **WHEN** standard changelog templates don't meet project needs
- **THEN** system SHALL allow custom template configuration
- **AND** support project-specific changelog formats and conventions

### ADDED Requirement: CHANGELOG.md Format Compliance
The system SHALL maintain compatibility with Keep a Changelog format standards.

#### Scenario: Version ordering
- **WHEN** updating CHANGELOG.md
- **THEN** system SHALL ensure new versions are added at the top and in descending order
- **AND** maintain proper spacing and section delimiters

#### Scenario: Entry structure validation
- **WHEN** writing changelog entries
- **THEN** system SHALL validate each entry follows the required format
- **AND** reject entries that don't meet formatting standards

### ADDED Requirement: Manual Override Support
The changelog automation SHALL provide manual override options for special cases.

#### Scenario: Manual changelog entry
- **WHEN** developers need to add custom changelog entries
- **THEN** they SHALL be able to manually trigger changelog generation with specific parameters
- **AND** bypass automated git analysis for custom entries

#### Scenario: Template customization
- **WHEN** project requires specific changelog format
- **THEN** system SHALL allow custom template configuration
- **AND** support project-specific changelog formats and conventions