## MODIFIED Requirements

### Requirement: Documentation Examples Structure
The documentation MUST present examples as structured Markdown documents with explanations, not as raw configuration files.

#### Scenario: Multi-source example is properly documented
- **GIVEN** a user browsing the examples section of the documentation
- **WHEN** they navigate to the multi-source example
- **THEN** they see a Markdown document that includes:
  - Introduction explaining the business scenario and use case
  - Prerequisites and requirements section
  - Full YAML configuration presented in annotated code blocks
  - Step-by-step usage instructions with commands
  - Explanation of key concepts demonstrated
  - Troubleshooting tips specific to the example

#### Scenario: Examples directory provides navigation
- **GIVEN** a user looking for relevant example configurations
- **WHEN** they visit the examples directory
- **THEN** they see:
  - Overview of all available examples
  - Clear guidance on when to use each example
  - Decision tree or guide for selecting the right example
  - Quick links to each specific example document

#### Scenario: Multiple focused examples cover common patterns
- **GIVEN** a user with specific configuration needs
- **WHEN** they look through the examples
- **THEN** they can find targeted examples for:
  - Simple Parquet-only configurations
  - Local attachment patterns (DuckDB/SQLite)
  - Environment variable usage and best practices
  - Each example includes explanations and variations

#### Scenario: Documentation site navigation reflects new structure
- **GIVEN** a user navigating the documentation site
- **WHEN** they use the navigation menu
- **THEN** all example-related links point to Markdown documentation pages, not raw YAML files