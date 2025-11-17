## MODIFIED Requirements

### Requirement: Documentation Site
The project MUST provide a MkDocs-based documentation site with quickstart, user guide, API reference sections, and proper repository/website metadata.

#### Scenario: Quickstart page exists
- **GIVEN** the built documentation site
- **WHEN** a user opens the landing page
- **THEN** they see a quickstart section showing installation, a minimal config, and example CLI/Python usage.

#### Scenario: User guide covers key workflows
- **GIVEN** the documentation site
- **WHEN** a user navigates to the user guide
- **THEN** they find explanations and examples for configuring DuckDB, attachments, Iceberg catalogs, and views.

#### Scenario: API reference via mkdocstrings
- **GIVEN** mkdocstrings is configured for the project
- **WHEN** the docs are built
- **THEN** the API reference section includes generated documentation for `duckalog` public APIs based on their docstrings.

#### Scenario: Repository metadata is configured
- **GIVEN** the MkDocs configuration file
- **WHEN** the documentation site is built and deployed
- **THEN** it includes proper site_url, repo_url, and repo_name settings for navigation and SEO