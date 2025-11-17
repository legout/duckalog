## ADDED Requirements

### Requirement: Top-level README
The project MUST provide a top-level `README.md` that introduces Duckalog and shows how to use it.

#### Scenario: README provides overview and features
- **GIVEN** a new user opening the GitHub repository
- **WHEN** they read `README.md`
- **THEN** they see a short description of Duckalog, its core features, and how it relates to DuckDB catalog configs.

#### Scenario: README includes installation instructions
- **GIVEN** a user with Python 3.9+ and pip
- **WHEN** they follow the README's installation section
- **THEN** they can install Duckalog and its dependencies without referring to other documents.

#### Scenario: README shows CLI quickstart
- **GIVEN** a minimal example config in the README
- **WHEN** the user runs `duckalog build`, `duckalog generate-sql`, and `duckalog validate` as described
- **THEN** the commands behave as documented (builds a catalog, prints SQL, and validates the config).

#### Scenario: README shows Python API quickstart
- **GIVEN** a Python snippet in the README using `build_catalog`, `generate_sql`, or `validate_config`
- **WHEN** a user copies and adapts that snippet
- **THEN** it runs successfully against a valid config without additional undocumented steps.

