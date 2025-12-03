## MODIFIED Requirements

### Requirement: Architecture Documentation
The project SHALL provide a comprehensive architecture document that explains the system's design, components, and data flow, including how the configuration package, SQL generation, engine orchestration, and dashboard/semantic-layer features fit together.

#### Scenario: Developer onboarding
- **WHEN** a new developer wants to understand how Duckalog works
- **THEN** they can read the architecture document to understand the system overview, component interactions, and architectural patterns
- **AND** they see up-to-date descriptions of the config package structure (models, loader, interpolation, validators, SQL integration), engine orchestration (for example, `CatalogBuilder`), and how SQL generation and dashboard features integrate with these components.

#### Scenario: Architecture reference
- **WHEN** developers need to make architectural decisions or understand existing patterns
- **THEN** they can reference the architecture document for guidance on system design principles and component relationships
- **AND** the document reflects the current implementation boundaries rather than legacy module layouts (for example, it does not describe modules that no longer exist).

#### Scenario: Documentation discovery
- **WHEN** users browse the documentation
- **THEN** they can easily find the architecture document from the main documentation index
- **AND** that document clearly links to deeper guides for topics like path resolution, secrets, and remote configuration.

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

