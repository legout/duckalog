## ADDED Requirements

### Requirement: Explicit Python Version Support Metadata
The package metadata MUST clearly declare the supported Python versions and keep that declaration consistent across `pyproject.toml`, classifiers, documentation, and status badges.

#### Scenario: pyproject.toml requires supported versions
- **WHEN** `pyproject.toml` is inspected
- **THEN** the `requires-python` field reflects the minimum supported Python version for Duckalog
- **AND** Trove classifiers only list Python versions that are officially supported and tested.

#### Scenario: Documentation matches package metadata
- **WHEN** users read the README, docs site, or project overview
- **THEN** the stated supported Python versions match the versions declared in `pyproject.toml` and classifiers
- **AND** no documentation claims support for versions that are not actually supported.

