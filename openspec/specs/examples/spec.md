# examples Specification

## Purpose
TBD - created by archiving change expand-examples-library. Update Purpose after archive.
## Requirements
### Requirement: Standardized Example Structure
All Duckalog examples SHALL follow a consistent structure to ensure maintainability and user experience.

#### Scenario: Example directory structure
- **WHEN** creating a new example
- **THEN** the example SHALL include:
  - `README.md` with business context, setup instructions, and learning objectives
  - `catalog.yaml` as the main Duckalog configuration file
  - `data/generate.py` for reproducible data generation
  - `validate.py` for automated example validation
  - Optional `docker-compose.yml` for complex setups

#### Scenario: Example README template
- **WHEN** writing example documentation
- **THEN** the README SHALL include:
  - Business context and use case description
  - Prerequisites and setup requirements
  - Step-by-step setup and execution instructions
  - Expected results and validation criteria
  - Learning objectives and key concepts demonstrated
  - Related examples and next steps for learning progression

#### Scenario: Data generation standards
- **WHEN** creating example data
- **THEN** the generation script SHALL:
  - Be deterministic and reproducible across runs
  - Generate realistic but synthetic data (no real user/business data)
  - Include parameter options for different data sizes
  - Document the data schema and business rules
  - Validate generated data for integrity and requirements

### Requirement: Example Organization and Discovery
Examples SHALL be organized by business domain and difficulty level to help users find relevant scenarios.

#### Scenario: Example categorization
- **WHEN** organizing examples
- **THEN** examples SHALL be categorized by:
  - **Business Intelligence**: customer-analytics, time-series, product-analytics
  - **Data Integration**: multi-source, cloud-warehouses, streaming
  - **Production & Ops**: cicd-integration, scaling, monitoring
  - **Advanced Features**: web-ui, semantic-layer, sql-advanced

#### Scenario: Difficulty progression
- **WHEN** users navigate examples
- **THEN** they SHALL find examples with clear difficulty levels:
  - **Level 1**: Single data source, basic queries, introductory concepts
  - **Level 2**: Multiple sources, simple joins, basic semantic models
  - **Level 3**: Complex business logic, advanced semantic features, time-series
  - **Level 4**: Production patterns, CI/CD, scaling, monitoring

#### Scenario: Example discovery
- **WHEN** users search for examples
- **THEN** they SHALL be able to filter by:
  - Business domain/use case
  - Technical features demonstrated
  - Difficulty level and prerequisites
  - Data sources and integrations used

### Requirement: Example Validation and Quality
All examples SHALL include automated validation to ensure functionality and prevent regressions.

#### Scenario: Automated validation
- **WHEN** running example validation
- **THEN** the validation script SHALL:
  - Verify `catalog.yaml` syntax and semantic correctness
  - Validate generated data meets schema and quality requirements
  - Confirm expected views and tables are created successfully
  - Check query results match expected outputs
  - Report validation failures with actionable error messages

#### Scenario: Performance validation
- **WHEN** validating complex examples
- **THEN** validation SHALL include:
  - Basic performance benchmarks for query execution
  - Memory usage monitoring for large dataset examples
  - Resource utilization documentation
  - Performance optimization recommendations
  - Comparison with baseline performance metrics

#### Scenario: Cross-platform compatibility
- **WHEN** testing examples
- **THEN** they SHALL work across:
  - Different operating systems (Windows, macOS, Linux)
  - Multiple Python versions (3.9+)
  - Various DuckDB versions within supported range
  - Different memory and resource constraints

### Requirement: Example Documentation and Integration
Examples SHALL be integrated with main documentation and provide clear learning paths.

#### Scenario: Documentation integration
- **WHEN** users read main documentation
- **THEN** they SHALL find:
  - References to relevant examples throughout docs
  - Example selection guide based on use case and skill level
  - Cross-references between related examples
  - Example index with search and filtering capabilities

#### Scenario: Learning progression
- **WHEN** users follow learning paths
- **THEN** they SHALL find:
  - Recommended sequence of examples for different goals
  - Prerequisites and dependencies between examples
  - "What's next" recommendations after completing examples
  - Progressive complexity building on previous examples

#### Scenario: Community contribution
- **WHEN** community members contribute examples
- **THEN** they SHALL follow:
  - Standardized example structure and templates
  - Automated validation and testing requirements
  - Documentation quality standards
  - Review process for example acceptance
  - Maintenance and update guidelines for contributed examples

### Requirement: S3 Options Field Documentation
The S3 secret documentation SHALL clearly document the \`options\` field and provide practical examples for common S3-specific parameters.

#### Scenario: User needs to configure S3 SSL settings
- **WHEN** a user reads the S3 Secret Fields table
- **THEN** the \`options\` field is listed with description of S3-specific parameters
- **AND** common parameters like \`use_ssl\` are documented

#### Scenario: User works with S3-compatible storage
- **WHEN** a user needs to configure URL style for MinIO or similar
- **THEN** the documentation shows \`options.url_style\` usage
- **AND** explains the difference between 'path' and 'virtual' styles

### Requirement: S3 Options Usage Examples
The documentation SHALL include practical S3 examples demonstrating the \`options\` field with environment variable integration.

#### Scenario: User needs S3 with custom SSL and URL style
- **WHEN** a user views S3 secret examples
- **THEN** there is an example showing both \`use_ssl\` and \`url_style\` in options
- **AND** the example uses environment variables for security
- **AND** the example includes explanatory comments

#### Scenario: User learns environment variable patterns for S3 options  
- **WHEN** a user sees the options example
- **THEN** the pattern shows how to reference environment variables in options
- **AND** the example validates successfully without errors

### Requirement: Example for SQL Files and Templates
The examples library MUST include at least one runnable example that demonstrates using `sql_file` and `sql_template` in Duckalog catalogs.

#### Scenario: Example structure for external SQL
- **GIVEN** the examples directory
- **WHEN** a user inspects the example for SQL files and templates
- **THEN** they SHALL find an example directory that follows the standardized structure:
  - `README.md` describing the business context and explaining `sql_file` and `sql_template` usage
  - `catalog.yaml` defining at least one inline SQL view, one `sql_file`-based view, and one or more `sql_template`-based views
  - `data/generate.py` that produces deterministic synthetic data for the example
  - `validate.py` that validates the example end-to-end
  - a `sql/` subdirectory containing the SQL and template files referenced from `catalog.yaml`.

#### Scenario: Example demonstrates per-view template variables
- **GIVEN** the example catalog demonstrating SQL templates
- **WHEN** a user opens `catalog.yaml`
- **THEN** they SHALL see one or more views that use `sql_template` with a `variables` mapping
- **AND** the corresponding template file SHALL use `{{variable}}` placeholders consistent with the configuration
- **AND** the `README.md` SHALL explain how these variables are defined and substituted during config loading.

#### Scenario: Example validation covers external SQL behavior
- **GIVEN** the example validation script
- **WHEN** the user runs the example's validation step
- **THEN** the script SHALL:
  - Load the catalog using `load_config(..., load_sql_files=True)`
  - Build or open a DuckDB catalog database
  - Query the views defined via `sql_file` and `sql_template`
  - Assert that the results match the expected behavior described in the README
  - Report clear errors if SQL files or templates are misconfigured.

### Requirement: Config Imports Comprehensive Guide
The examples SHALL include a comprehensive guide for config imports feature explaining import resolution, merge behavior, diagnostics, and best practices.

#### Scenario: Import resolution understanding
- **GIVEN** a user wanting to use config imports
- **WHEN** they read the config imports guide
- **THEN** they find detailed explanation of:
  - Import path resolution (relative to config file)
  - Import processing order
  - Remote import support (S3, GCS, Azure, HTTP)
  - Circular dependency detection
- **AND** they see practical examples of each import type
- **SO** they understand how imports are resolved and processed

#### Scenario: Merge behavior documentation
- **GIVEN** a user with conflicting definitions across imported configs
- **WHEN** they consult the config imports guide
- **THEN** they find documentation of merge strategies:
  - How views are merged/overridden
  - How attachments are combined
  - How secrets are merged
  - Conflict resolution rules
- **AND** they see examples of merge outcomes
- **SO** they can predict and control merge behavior

#### Scenario: Diagnostics usage guide
- **GIVEN** a user debugging import issues
- **WHEN** they need to use show-imports diagnostics
- **THEN** they find guide documentation showing:
  - How to use --diagnostics flag
  - How to interpret import graph output
  - How to use --show-merged to preview final config
  - How to export import graph as JSON
- **AND** they see example diagnostic outputs with explanations
- **SO** they can effectively debug import problems

#### Scenario: Config imports best practices
- **GIVEN** a user organizing large configurations
- **WHEN** they look for organizational guidance
- **THEN** they find best practices for config imports:
  - When to use imports vs single file
  - How to organize shared configurations
  - Patterns for environment-specific configs
  - Import depth recommendations
- **AND** they see real-world organizational examples
- **SO** they can organize configurations effectively

### Requirement: Example Metadata and Prerequisites
Each example SHALL include metadata indicating difficulty level, prerequisites, learning objectives, and estimated completion time.

#### Scenario: Example difficulty identification
- **GIVEN** a user browsing examples
- **WHEN** they view any example page
- **THEN** they see a difficulty level indicator (Beginner/Intermediate/Advanced)
- **AND** they see prerequisites listed (e.g., "Complete 'Simple Parquet' example first")
- **AND** they see "What you'll learn" section
- **AND** they see estimated time to complete
- **SO** they can assess if the example is appropriate for their level

#### Scenario: Learning objectives clarity
- **GIVEN** a user selecting an example to work through
- **WHEN** they read the example introduction
- **THEN** they find clear learning objectives stating what skills they'll gain
- **AND** objectives align with the difficulty level
- **AND** objectives specify what they'll be able to do after completion
- **SO** they have clear expectations of outcomes

#### Scenario: Progressive skill indicators
- **GIVEN** a user completing multiple examples
- **WHEN** they track their progress
- **THEN** they can see how examples build on each other
- **AND** they can identify their current skill level
- **AND** they can choose appropriate next examples
- **SO** they can follow a coherent learning path

### Requirement: Example Cross-Referencing
Examples SHALL include cross-references to related examples, relevant how-to guides, and reference documentation to facilitate learning and discovery.

#### Scenario: Related examples discovery
- **GIVEN** a user completing an example
- **WHEN** they finish the example
- **THEN** they see "Related Examples" section suggesting:
  - Prerequisite examples (if not already completed)
  - Next logical examples in learning progression
  - Alternative approaches to similar problems
- **SO** they can continue learning systematically

#### Scenario: Reference documentation links
- **GIVEN** a user working through an example
- **WHEN** they encounter configuration options or commands
- **THEN** they find links to reference documentation for:
  - Configuration schema for options used
  - CLI command reference for commands demonstrated
  - API reference for functions called
- **SO** they can learn more details about specific features

#### Scenario: How-to guide connections
- **GIVEN** a user understanding example concepts
- **WHEN** they want to apply concepts to real problems
- **THEN** they find links to relevant how-to guides:
  - "See how to debug this in production" → troubleshooting guide
  - "Learn to optimize this pattern" → performance tuning guide
  - "Adapt this for multiple environments" → environment management guide
- **SO** they can bridge from learning to practical application

