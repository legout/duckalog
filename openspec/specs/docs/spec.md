# docs Specification

## Purpose
TBD - created by archiving change add-docs-navigation. Update Purpose after archive.
## Requirements
### Requirement: Add DuckDB secrets example to navigation
The navigation configuration SHALL include an entry for the DuckDB secrets example that allows users to discover and access the secrets documentation from the Examples section.

#### Scenario: User discovers DuckDB secrets documentation
- **GIVEN** the user is browsing the documentation site
- **WHEN** they navigate to the Examples section
- **THEN** they see "DuckDB Secrets" listed in alphabetical order
- **AND** clicking the entry successfully opens the secrets documentation
- **SO** the user can read about managing credentials for external services

### Requirement: Add DuckDB settings example to navigation
The navigation configuration SHALL include an entry for the DuckDB settings example that allows users to discover and access the settings documentation from the Examples section.

#### Scenario: User discovers DuckDB settings documentation
- **GIVEN** the user is browsing the documentation site
- **WHEN** they navigate to the Examples section
- **THEN** they see "DuckDB Settings" listed in alphabetical order
- **AND** clicking the entry successfully opens the settings documentation
- **SO** the user can read about configuring DuckDB session parameters

### Requirement: Maintain navigation structure consistency
The navigation SHALL maintain alphabetical ordering and consistent formatting when new example pages are added to ensure a cohesive user experience.

#### Scenario: Navigation maintains alphabetical ordering
- **GIVEN** the Examples section contains multiple pages
- **WHEN** new example pages are added
- **THEN** the navigation maintains alphabetical ordering
- **AND** entries follow consistent formatting with other examples
- **SO** the structure remains coherent and predictable

### Requirement: Eliminate navigation warnings
The MkDocs build process SHALL complete without warnings about pages existing in the docs directory but not included in the navigation configuration.

#### Scenario: No documentation warnings during build
- **GIVEN** MkDocs site configuration exists
- **WHEN** `mkdocs build` or `mkdocs serve` is executed
- **THEN** there are no warnings about missing navigation entries
- **AND** all pages in `docs/examples/` are included in navigation
- **SO** the documentation site builds cleanly and completely

### Requirement: Python Version Requirements Documentation
All project documentation SHALL clearly state Python version requirements and provide examples using modern Python features.

#### Scenario: Clear Python version requirements
- **GIVEN** users reading documentation for installation instructions
- **WHEN** they look for Python version requirements
- **THEN** they find explicit mention that Python >= 3.12 is required
- **AND** the rationale (modern typing features) is briefly explained

#### Scenario: Code examples use modern Python features
- **GIVEN** users reading code examples in documentation
- **WHEN** they see type hints and function signatures
- **THEN** examples use PEP 604 unions (`str | int`) and built-in generics (`list[int]`, `dict[str, Any]`)
- **AND** examples do not include compatibility code for older Python versions

#### Scenario: Installation instructions reflect version requirements
- **GIVEN** new users following installation instructions
- **WHEN** they check the requirements before installing
- **THEN** installation guides clearly state Python >= 3.12 requirement
- **AND** pip install commands work correctly with the declared requirements
