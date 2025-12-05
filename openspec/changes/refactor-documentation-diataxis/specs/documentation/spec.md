## ADDED Requirements

### Requirement: Comprehensive How-to Guides
The documentation SHALL provide task-oriented how-to guides for common operations including environment management, debugging, migration, and performance tuning.

#### Scenario: Environment management guide
- **GIVEN** a user needs to manage multiple environments (dev/staging/prod)
- **WHEN** they search for environment management documentation
- **THEN** they find a dedicated how-to guide explaining configuration organization patterns
- **AND** the guide shows practical examples of splitting configs for different environments
- **SO** they can implement appropriate environment separation

#### Scenario: Debugging build failures guide
- **GIVEN** a user encountering catalog build failures
- **WHEN** they look for debugging help
- **THEN** they find a troubleshooting guide with common error scenarios
- **AND** each scenario includes symptoms, causes, and solutions
- **SO** they can diagnose and fix build issues efficiently

#### Scenario: Migration from manual SQL guide
- **GIVEN** a user with existing DuckDB workflows
- **WHEN** they want to migrate to duckalog
- **THEN** they find a migration guide with step-by-step instructions
- **AND** the guide includes before/after examples
- **SO** they can migrate existing workflows systematically

#### Scenario: Performance tuning guide
- **GIVEN** a user with performance concerns
- **WHEN** they search for optimization guidance
- **THEN** they find a performance tuning guide with practical techniques
- **AND** the guide covers memory settings, query optimization, and data organization
- **SO** they can optimize their catalog performance

### Requirement: Progressive Tutorials
The documentation SHALL provide step-by-step tutorials that guide users from basic to complex catalog creation with hands-on exercises.

#### Scenario: Getting started tutorial
- **GIVEN** a complete beginner to duckalog
- **WHEN** they follow the getting started tutorial
- **THEN** they build progressively more complex catalogs through clear steps:
  - Step 1: Single Parquet file catalog
  - Step 2: Adding SQL transformations
  - Step 3: Multi-source joins
  - Step 4: Using config imports for modularity
- **AND** each step builds on previous knowledge
- **AND** all examples are reproducible with provided data
- **SO** they learn duckalog fundamentals through practice

#### Scenario: Dashboard basics tutorial
- **GIVEN** a user who has created basic catalogs
- **WHEN** they follow the dashboard tutorial
- **THEN** they learn to launch and use the web UI through hands-on steps
- **AND** they understand security features and deployment options
- **SO** they can effectively use the dashboard for catalog management

### Requirement: Complete CLI Reference
The documentation SHALL provide comprehensive CLI command reference with all flags, options, and examples for every command.

#### Scenario: Complete build command documentation
- **GIVEN** a user needing to understand all build command options
- **WHEN** they consult the CLI reference
- **THEN** they find complete documentation for the build command including:
  - All flags (--db-path, --fs-key, --fs-secret, etc.)
  - Remote storage options (S3, GCS, Azure, SFTP)
  - Filesystem authentication patterns
  - Usage examples for common scenarios
- **SO** they can use all build command capabilities effectively

#### Scenario: Show-imports diagnostics documentation
- **GIVEN** a user using config imports
- **WHEN** they need to debug import resolution
- **THEN** they find documentation for show-imports command with all flags
- **AND** documentation explains --diagnostics flag output format
- **AND** documentation shows how to interpret import graph and merged config
- **SO** they can troubleshoot import issues effectively

### Requirement: Configuration Schema Reference
The documentation SHALL provide a comprehensive YAML/JSON schema reference documenting all configuration options with types, defaults, required fields, and examples.

#### Scenario: Complete configuration option lookup
- **GIVEN** a user writing a configuration file
- **WHEN** they need to understand available options
- **THEN** they find a schema reference with all configuration sections:
  - duckdb (database, pragmas, install_extensions, load_extensions)
  - secrets (all secret types with required/optional fields)
  - attachments (duckdb, sqlite, postgres with connection parameters)
  - iceberg_catalogs (catalog_type, uri, warehouse, options)
  - views (all source types with required fields)
  - semantic_models (dimensions, measures, joins, defaults)
- **AND** each option includes type, default value, and description
- **SO** they can write correct configurations without trial and error

#### Scenario: Config import resolution algorithm reference
- **GIVEN** a user using config imports
- **WHEN** they need to understand merge behavior
- **THEN** they find documentation of the import resolution algorithm
- **AND** documentation explains merge strategies for conflicting definitions
- **AND** documentation shows circular dependency detection
- **SO** they understand how imports are processed

### Requirement: Explanation Documentation Balance
The documentation SHALL provide explanation-oriented content covering philosophy, design decisions, and performance characteristics to balance the Diátaxis framework.

#### Scenario: Understanding when to use duckalog
- **GIVEN** a user evaluating duckalog for their use case
- **WHEN** they look for guidance on applicability
- **THEN** they find philosophy documentation explaining:
  - When duckalog is appropriate vs plain DuckDB
  - Design principles (config-driven, idempotent, multi-source)
  - Trade-offs and limitations
- **SO** they can make informed decisions about adoption

#### Scenario: Understanding performance characteristics
- **GIVEN** a user concerned about performance
- **WHEN** they look for performance information
- **THEN** they find explanation documentation covering:
  - Path resolution performance impact
  - View materialization vs virtual views
  - Memory and storage considerations
  - Query performance patterns
- **SO** they understand performance implications of their choices

## MODIFIED Requirements

### Requirement: Architecture Documentation
The project SHALL provide a comprehensive architecture document that explains the system's design, components, and data flow, including proper cross-references to detailed guides for specific topics following the Diátaxis framework.

#### Scenario: Developer onboarding
- **WHEN** a new developer wants to understand how Duckalog works
- **THEN** they can read the architecture document to understand the system overview, component interactions, and architectural patterns
- **AND** they see up-to-date descriptions of the config package structure (models, loader, interpolation, validators, SQL integration), engine orchestration (for example, `CatalogBuilder`), and how SQL generation and dashboard features integrate with these components
- **AND** the document includes clear cross-references to tutorials, how-to guides, and reference docs for deeper dives

#### Scenario: Architecture reference with Diátaxis links
- **WHEN** developers need to make architectural decisions or understand existing patterns
- **THEN** they can reference the architecture document for guidance on system design principles and component relationships
- **AND** the document reflects the current implementation boundaries rather than legacy module layouts
- **AND** the document links to relevant how-to guides for implementation tasks
- **AND** the document links to reference documentation for detailed specifications
- **SO** they can navigate from high-level understanding to specific implementation details

#### Scenario: Documentation discovery from architecture
- **WHEN** users browse the documentation
- **THEN** they can easily find the architecture document from the main documentation index under "Understanding" or "Explanation" section
- **AND** the architecture document clearly links to deeper guides for topics like path resolution (how-to), secrets (reference), and remote configuration (tutorial/how-to)
- **SO** the architecture serves as a hub for navigating to specific documentation
