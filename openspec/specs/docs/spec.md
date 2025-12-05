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
The navigation SHALL include entries for ALL maintained example pages under `docs/examples/` organized by difficulty level to provide comprehensive access to usage patterns and configurations.

#### Scenario: All examples are discoverable by difficulty
- **GIVEN** users exploring example documentation
- **WHEN** they navigate to the Examples section
- **THEN** they can find all maintained examples grouped or tagged by difficulty (Beginner/Intermediate/Advanced)
- **AND** examples include config imports, DuckDB secrets, DuckDB settings, environment variables, local attachments, multi-source analytics, path resolution, and simple parquet
- **SO** users can discover examples appropriate to their skill level

#### Scenario: Examples maintain logical grouping
- **GIVEN** the Examples section contains multiple pages
- **WHEN** new example pages are added
- **THEN** the navigation maintains logical grouping by topic or difficulty
- **AND** entries follow consistent formatting with difficulty indicators
- **SO** the structure remains coherent and accessible

#### Scenario: Cross-references between examples
- **GIVEN** a user reading an intermediate example
- **WHEN** the example builds on beginner concepts
- **THEN** the example includes clear cross-references to prerequisite examples
- **AND** related advanced examples are suggested
- **SO** users can navigate the learning path effectively

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

### Requirement: Top-Level Navigation Tabs
The documentation navigation MUST expose the main documentation sections as top-level chapters in the UI (for example via the top navigation bar), rather than hiding them only in the left sidebar.

#### Scenario: Main chapters visible in top bar
- **GIVEN** a user opens the Duckalog documentation site in a browser
- **WHEN** they look at the top navigation area
- **THEN** they see the primary documentation chapters listed as first-level entries (for example: Home, Getting Started, How-to Guides, Reference, Understanding, Examples, Legacy Guides, Security)
- **AND** selecting any of these chapters shows its contents in the left sidebar
- **SO** they can understand the overall documentation structure at a glance.

#### Scenario: Sidebar shows within-chapter navigation
- **GIVEN** a user clicks on a chapter such as "How-to Guides" or "Reference" in the top navigation
- **WHEN** the page loads
- **THEN** the left sidebar shows navigation only for that chapter’s internal pages
- **AND** the sidebar does not repeat unrelated top-level chapters
- **SO** users can focus on the current chapter while still having quick access to others from the top bar.

### Requirement: Diátaxis Framework Navigation Structure
The documentation navigation SHALL be organized according to the Diátaxis framework with clear sections for Tutorials, How-to Guides, Reference, and Explanation/Understanding to match documentation to user intent.

#### Scenario: User finding learning material
- **GIVEN** a new user wants to learn duckalog from scratch
- **WHEN** they browse the documentation navigation
- **THEN** they find a "Getting Started" or "Tutorials" section with step-by-step learning materials
- **AND** the tutorials are clearly distinct from reference documentation
- **SO** they can learn progressively without confusion

#### Scenario: User finding problem solutions
- **GIVEN** an experienced user needs to solve a specific problem
- **WHEN** they browse the documentation navigation
- **THEN** they find a "How-to Guides" section with task-oriented instructions
- **AND** guides are organized by common tasks (environment management, debugging, migration)
- **SO** they can quickly find solutions without reading full tutorials

#### Scenario: User finding technical reference
- **GIVEN** a user needs to look up specific API details or configuration options
- **WHEN** they browse the documentation navigation
- **THEN** they find a "Reference" section with comprehensive technical information
- **AND** reference docs include Python API, CLI commands, and configuration schema
- **SO** they can find precise technical information efficiently

### Requirement: Examples with Progressive Learning Path
The examples section SHALL organize examples with clear difficulty ratings, prerequisites, and learning progression to guide users from beginner to advanced usage.

#### Scenario: Beginner identifying appropriate examples
- **GIVEN** a new user exploring examples
- **WHEN** they view the examples index
- **THEN** they see difficulty ratings (Beginner/Intermediate/Advanced) for each example
- **AND** they see prerequisites listed for each example
- **AND** they see "What you'll learn" descriptions
- **SO** they can choose appropriate examples for their skill level

#### Scenario: Progressive skill building
- **GIVEN** a user completing beginner examples
- **WHEN** they look for next steps
- **THEN** the examples index shows a clear progression path
- **AND** intermediate examples build on beginner concepts
- **AND** advanced examples reference prerequisite knowledge
- **SO** they can build skills systematically

### Requirement: Documentation Type Indicators
Each documentation page SHALL clearly indicate its type (Tutorial, How-to, Reference, or Explanation) to set appropriate user expectations.

#### Scenario: User understanding doc purpose
- **GIVEN** a user reading any documentation page
- **WHEN** they view the page header or breadcrumbs
- **THEN** they can identify whether it's a Tutorial, How-to Guide, Reference, or Explanation
- **AND** the navigation hierarchy reflects the documentation type
- **SO** they understand how to use the documentation effectively

