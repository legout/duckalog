# documentation Specification

## Purpose
TBD - created by archiving change add-architecture-documentation. Update Purpose after archive.
## Requirements
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

### Requirement: Component Interaction Overview
The architecture document SHALL describe how the core modules and orchestration components interact, including the configuration package, SQL generation, engine orchestration, CLI/Python API entry points, and dashboard/semantic-layer features.

#### Scenario: Understanding data flow
- **WHEN** a developer wants to trace how a configuration file becomes a DuckDB catalog
- **THEN** the architecture document shows the step-by-step flow through config loading and interpolation, validation and model construction, SQL generation, and catalog building via the engine orchestration layer
- **AND** it highlights where path resolution, remote configuration loading, and secret creation plug into this flow.

#### Scenario: Module responsibilities
- **WHEN** a developer wants to understand what each module is responsible for
- **THEN** the architecture document clearly delineates the responsibilities and boundaries of each core component (configuration package, SQL generation, engine orchestration, CLI/Python API, and dashboard/semantic-layer features)
- **AND** it distinguishes between public APIs and internal implementation details while remaining accurate to the current codebase.

### Requirement: Architectural Patterns Documentation
The architecture document SHALL document the key architectural patterns and design decisions used in the system.

#### Scenario: Design decisions reference
- **WHEN** developers need to understand why certain patterns were chosen
- **THEN** the architecture document explains the rationale behind architectural choices like separation of concerns, config-driven design, and idempotent operations

#### Scenario: Extension guidance
- **WHEN** developers want to extend the system with new capabilities
- **THEN** the architecture document provides guidance on how to extend the system following existing patterns

### Requirement: Visual Architecture Documentation
The architecture document SHALL include visual diagrams that illustrate system components and data flow.

#### Scenario: Visual understanding
- **WHEN** developers prefer visual representations of complex systems
- **THEN** the architecture document provides clear diagrams showing component interactions and data flow patterns

#### Scenario: System overview
- **WHEN** stakeholders need a high-level understanding of the system architecture
- **THEN** they can quickly grasp the overall system design through visual diagrams and accompanying explanations

### Requirement: Documentation Integration
The architecture document SHALL be properly integrated into the existing documentation structure with appropriate navigation and cross-references.

#### Scenario: Seamless navigation
- **WHEN** users are browsing the documentation
- **THEN** they can easily navigate to and from the architecture document through the main index and related sections

#### Scenario: Cross-reference consistency
- **WHEN** users follow links between documentation sections
- **THEN** all cross-references work correctly and maintain consistency with the technical specification

### Requirement: Unified Intro and Quickstart
The project SHALL maintain a consistent high-level introduction and quickstart across `README.md` and `docs/index.md`, with a clearly defined single source of truth.

#### Scenario: README quickstart matches docs quickstart
- **GIVEN** a new user browsing the GitHub repository
- **WHEN** they read the quickstart in `README.md`
- **AND** then follow the link to the documentation homepage (`docs/index.md`)
- **THEN** they see an equivalent high-level introduction and quickstart flow (same main steps and expectations)
- **AND** there are no contradictory or obviously outdated differences between the two entry points
- **SO** they can move between README and docs without confusion.

#### Scenario: Single canonical intro snippet
- **GIVEN** a maintainer updating the introductory and quickstart text
- **WHEN** they follow the documented process for editing this content
- **THEN** they only need to update a single canonical location (for example a shared snippet or the docs index)
- **AND** the README automatically reuses or mirrors that content according to the documented policy
- **SO** the risk of the two entry points drifting out of sync is minimized.

### Requirement: Architecture Document in Explanation Section
The architecture document SHALL live under the “Explanation/Understanding” section of the documentation while remaining easy to discover from the main index.

#### Scenario: Architecture appears in Understanding section
- **GIVEN** a user navigates to the “Understanding” or “Explanation” section of the docs
- **WHEN** they scan the entries in that section
- **THEN** they find the architecture document listed there (for example as `Architecture`)
- **AND** the document URL and file path reflect that it belongs to the explanation layer (for example under `explanation/`)
- **SO** the architecture content is clearly categorized as explanation rather than a top-level miscellaneous page.

#### Scenario: Architecture discoverable from main index
- **GIVEN** a developer browsing the documentation from the homepage
- **WHEN** they look for an overview of Duckalog’s architecture
- **THEN** they can navigate to the architecture document either via the “Understanding/Explanation” section or via an obvious link from the main index
- **AND** the architecture document clearly links out to deeper design and implementation guides where applicable
- **SO** new contributors can quickly find and use the architecture documentation.

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

