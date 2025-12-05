## ADDED Requirements

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

## MODIFIED Requirements

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
