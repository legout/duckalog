## MODIFIED Requirements

### Requirement: Dashboard Documentation Accuracy
The dashboard documentation MUST accurately reflect the current implementation using Datastar framework, include all security features, and document the complete feature set.

#### Scenario: Correct framework documentation
- **GIVEN** users reading dashboard documentation
- **WHEN** they learn about the technical implementation
- **THEN** the documentation correctly identifies Datastar as the reactive web framework
- **AND** does NOT mention deprecated frameworks like starhtml/starui
- **AND** includes information about bundled Datastar assets for offline operation
- **SO** users have accurate technical information

#### Scenario: Security features documented
- **GIVEN** users deploying the dashboard
- **WHEN** they consult the documentation for security information
- **THEN** they find documentation of all security features:
  - Admin token protection for mutating operations
  - Read-only SQL enforcement (SELECT only, blocks DDL/DML)
  - CORS protection (localhost restriction by default)
  - Background task processing for non-blocking operations
  - Atomic configuration updates
- **AND** they find examples of production deployment with security enabled
- **SO** they can deploy the dashboard securely

#### Scenario: Complete feature list
- **GIVEN** users learning dashboard capabilities
- **WHEN** they read the feature documentation
- **THEN** they find complete documentation of all features:
  - View management (create, edit, delete)
  - Query execution with real-time results
  - Data export (CSV, Excel, Parquet formats)
  - Schema inspection (tables and views)
  - Catalog rebuild functionality
  - Semantic layer explorer
  - Model details (dimensions and measures with expressions)
- **AND** each feature includes usage instructions and screenshots/examples
- **SO** they understand full dashboard capabilities

#### Scenario: Python API as primary entry point
- **GIVEN** users wanting to launch the dashboard
- **WHEN** they read the documentation
- **THEN** the Python API method (run_dashboard) is documented as the primary entry point
- **AND** includes working code examples
- **AND** CLI launch (duckalog ui) is clearly marked as optional or may not be available
- **SO** users can reliably launch the dashboard regardless of installation method

#### Scenario: Datastar runtime requirements
- **GIVEN** users installing dashboard dependencies
- **WHEN** they read the installation documentation
- **THEN** they find information about Datastar runtime requirements:
  - No legacy fallback (exclusive Datastar patterns)
  - Reactive data binding capabilities
  - Server-Sent Events for real-time updates
  - Modern web patterns with built-in security
  - Bundled assets for offline operation
- **AND** they understand why duckalog[ui] extra is required
- **SO** they can install and understand dashboard dependencies

## ADDED Requirements

### Requirement: Dashboard Deployment Patterns
The documentation SHALL provide practical deployment patterns for the dashboard including local development, production deployment, and security configuration.

#### Scenario: Local development setup
- **GIVEN** a developer wanting to use the dashboard locally
- **WHEN** they follow the local development documentation
- **THEN** they find clear instructions for:
  - Installing UI dependencies (duckalog[ui])
  - Launching dashboard with default settings
  - Accessing dashboard at localhost
  - Understanding default security (no admin token in dev)
- **SO** they can quickly start using the dashboard for development

#### Scenario: Production deployment guidance
- **GIVEN** a user deploying dashboard in production
- **WHEN** they consult deployment documentation
- **THEN** they find production deployment guidance including:
  - Setting DUCKALOG_ADMIN_TOKEN for security
  - Configuring host and port binding
  - Understanding CORS implications
  - Background task behavior
  - Resource requirements
- **AND** they find example deployment configurations
- **SO** they can deploy securely and reliably

#### Scenario: Security configuration reference
- **GIVEN** a user configuring dashboard security
- **WHEN** they need security configuration details
- **THEN** they find reference documentation for:
  - Admin token environment variable
  - Read-only SQL enforcement (not configurable, always active)
  - CORS middleware configuration
  - Default security settings
  - Security best practices
- **SO** they can configure appropriate security for their deployment
