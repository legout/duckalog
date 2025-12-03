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

### Requirement: Dashboard Documentation Entry Points
The dashboard documentation MUST describe how to launch the dashboard from the Python API and MAY describe CLI launch only if the `duckalog ui` command is clearly marked as optional or experimental.

#### Scenario: Python API documented as primary entry point
- **WHEN** users read the dashboard documentation
- **THEN** they see an example that launches the dashboard using the Python API (for example, `run_dashboard("catalog.yaml")`)
- **AND** the example is presented as the primary supported entry point.

#### Scenario: CLI example is marked as optional
- **WHEN** the documentation includes an example using `duckalog ui catalog.yaml`
- **THEN** the example clearly indicates that this CLI command may not be available in all installations
- **AND** directs users to the Python API entry point if the CLI command is not present.

### Requirement: Core Guides Navigation Coverage
The navigation SHALL include entries for all core guides including User Guide usage, path resolution guides, and security documentation to ensure discoverability.

#### Scenario: Security documentation is navigable
- **GIVEN** users browsing the documentation site
- **WHEN** they look for security-related information
- **THEN** they can find the SECURITY.md page through clear navigation entry
- **SO** security documentation is easily discoverable

#### Scenario: Path resolution guides are navigable
- **GIVEN** users learning about path resolution
- **WHEN** they navigate through the User Guide section
- **THEN** they can find all path resolution documentation including overview, best practices, examples, and migration guides
- **SO** path resolution information is systematically accessible

### Requirement: Complete Examples Navigation Coverage
The navigation SHALL include entries for ALL maintained example pages under `docs/examples/` to provide comprehensive access to usage patterns and configurations.

#### Scenario: All examples are discoverable
- **GIVEN** users exploring example documentation
- **WHEN** they navigate to the Examples section
- **THEN** they can find all maintained examples including DuckDB secrets, DuckDB settings, environment variables, local attachments, multi-source analytics, path resolution examples, and simple parquet
- **SO** users can discover and learn from comprehensive examples

#### Scenario: Examples maintain alphabetical ordering
- **GIVEN** the Examples section contains multiple pages
- **WHEN** new example pages are added
- **THEN** the navigation maintains alphabetical ordering within the Examples section
- **AND** entries follow consistent formatting
- **SO** the structure remains coherent and predictable

### Requirement: API Documentation Quality Standards
API reference pages included in the docs site SHALL build without mkdocstrings/Griffe warnings for public APIs to ensure high-quality generated documentation.

#### Scenario: Type annotations prevent warnings
- **GIVEN** public functions referenced in API documentation
- **WHEN** mkdocstrings/Griffe processes the code
- **THEN** all public functions have explicit return type annotations
- **AND** any variadic parameters use acceptable annotation patterns or detailed docstring descriptions
- **SO** no warnings are emitted during documentation generation

#### Scenario: Config module API docs are clean
- **GIVEN** functions from `src/duckalog/config/loader.py` are referenced in API docs
- **WHEN** the documentation is generated
- **THEN** all public loader functions have explicit return type annotations
- **AND** no mkdocstrings/Griffe warnings are produced
- **SO** the config module API documentation meets quality standards

