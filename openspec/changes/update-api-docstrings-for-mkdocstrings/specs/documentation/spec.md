## ADDED Requirements

### Requirement: MkDocStrings-Only API Reference
The API reference page SHALL be generated entirely from mkdocstrings using Python docstrings, without duplicating per-API descriptions in hand-written markdown.

#### Scenario: API reference generated from docstrings
- **GIVEN** a user opens the API reference page in the documentation
- **WHEN** they scroll through the documented functions, classes, and modules
- **THEN** all detailed descriptions, parameter lists, return types, and exceptions originate from Python docstrings rendered by mkdocstrings
- **AND** there is no conflicting or duplicated manual per-function description in the markdown file itself
- **SO** the API documentation stays in sync with the code by updating docstrings only.

#### Scenario: API reference structure matches public surface
- **GIVEN** a maintainer updates the list of public modules and symbols
- **WHEN** they adjust the mkdocstrings directives in the API reference (for example `::: duckalog` or per-module blocks)
- **THEN** the rendered API reference automatically reflects the new public surface based on docstrings
- **AND** no additional hand-written markdown is required to keep the reference accurate
- **SO** the maintenance burden for API documentation remains low.

### Requirement: Complete Public API Docstrings
All public Python API functions, classes, and methods SHALL have complete, Google-style docstrings suitable for direct rendering in the API reference.

#### Scenario: Public functions documented consistently
- **GIVEN** a developer inspects public functions such as `load_config`, `build_catalog`, `validate_config`, `generate_sql`, and connection helpers
- **WHEN** they view their docstrings in the source or in the rendered API reference
- **THEN** each docstring includes:
  - A clear one-line summary
  - Parameter/Args descriptions with types and meaning
  - A Returns section describing the return type and semantics (if applicable)
  - A Raises section for relevant exceptions
- **AND** the formatting follows Google-style conventions compatible with mkdocstrings
- **SO** users can rely on the API reference for precise, structured information.

#### Scenario: Examples for key entry points
- **GIVEN** a user reading the API reference for high-level entry points (for example connection helpers and catalog-building functions)
- **WHEN** they view the docstrings rendered in the docs
- **THEN** they see at least one short, accurate code example demonstrating typical usage
- **AND** the example can be copy-pasted with minimal modification to work in a real project
- **SO** users can quickly learn how to apply the APIs without searching separate guides.

