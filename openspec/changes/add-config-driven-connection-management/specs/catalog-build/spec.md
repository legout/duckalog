## ADDED Requirements

### Requirement: Session State Restoration
The system MUST provide automatic restoration of DuckDB settings and attachments on every catalog connection, since these are session-only in DuckDB and do not persist across connections.

#### Scenario: Connection restores DuckDB settings
- **GIVEN** a catalog configuration with DuckDB pragmas and settings
- **WHEN** a new database connection is established to an existing catalog
- **THEN** the system SHALL reapply all configured pragmas and settings
- **AND** the connection SHALL have the same session state as during initial build

#### Scenario: Connection reattaches databases
- **GIVEN** a catalog configuration with database attachments (DuckDB, SQLite, PostgreSQL)
- **WHEN** a new database connection is established to an existing catalog
- **THEN** the system SHALL re-execute ATTACH DATABASE statements for all configured attachments
- **AND** the connection SHALL have access to all attached databases

### Requirement: Config-Driven Entry Point
The system MUST provide a primary entry point that intelligently handles existing catalogs vs initial builds, applying only what's needed.

#### Scenario: Smart catalog initialization
- **GIVEN** a catalog configuration and a database path
- **WHEN** `connect_to_catalog(config_path)` is called
- **THEN** the system SHALL detect if the catalog exists
- **AND** if it doesn't exist, perform a full catalog build
- **AND** if it exists, restore session state and only create missing views

#### Scenario: Incremental view updates
- **GIVEN** an existing catalog with views and an updated configuration
- **WHEN** the configuration adds new views that don't exist in the catalog
- **THEN** the system SHALL create only the missing views
- **AND** existing views SHALL remain unchanged

#### Scenario: Force rebuild capability
- **GIVEN** an existing catalog and an updated configuration
- **WHEN** `connect_to_catalog(config_path, force_rebuild=True)` is called
- **THEN** the system SHALL perform a full catalog rebuild regardless of existing state
- **AND** all views SHALL be recreated

### Requirement: Connection Management
The system MUST provide a connection manager class to handle session state restoration and resource management.

#### Scenario: Lazy connection with state restoration
- **GIVEN** a `CatalogConnection` instance initialized with a config path
- **WHEN** `get_connection()` is called for the first time
- **THEN** the system SHALL establish a new DuckDB connection
- **AND** automatically restore all session state (settings, attachments)
- **AND** apply any incremental updates needed

#### Scenario: Connection persistence
- **GIVEN** an active `CatalogConnection` instance
- **WHEN** `get_connection()` is called multiple times
- **THEN** the system SHALL return the existing connection without re-restoring state
- **AND** the connection SHALL remain valid until `close()` is called

## MODIFIED Requirements

### Requirement: Build Catalog from Config
The system SHALL provide functions to build or update a DuckDB catalog from a validated configuration while supporting both full rebuild and incremental update workflows.

#### Scenario: Catalog built from config with session state
- **GIVEN** a valid configuration describing a DuckDB database path, attachments, and views
- **WHEN** `build_catalog(config_path)` is called
- **THEN** the system SHALL apply pragmas and extensions
- **AND** SHALL create or reattach all database attachments
- **AND** SHALL create or replace all configured views
- **AND** SHALL ensure the resulting catalog has proper session state

#### Scenario: Idemp incremental catalog updates
- **GIVEN** a valid config and an existing DuckDB catalog file
- **WHEN** `build_catalog(config_path, incremental=True)` is run multiple times
- **THEN** the system SHALL restore session state on each connection
- **AND** SHALL only create views that don't already exist
- **AND** SHALL preserve existing views unless force_rebuild=True

### Requirement: Secrets Persistence
DuckDB secret configurations SHALL allow user control over secret persistence behavior, with temporary secrets as the default security-conscious choice.

#### Scenario: Temporary secrets (default behavior)
- **GIVEN** a configuration with secrets that do not specify `persistent: true`
- **WHEN** catalog connections are established
- **THEN** secrets SHALL be created as temporary (non-persistent) by default
- **AND** secrets SHALL be recreated on each connection setup
- **AND** secrets SHALL NOT be stored in the database file

#### Scenario: Persistent secrets (opt-in)
- **GIVEN** a configuration with secrets that specify `persistent: true`
- **WHEN** catalog connections are established
- **THEN** those specific secrets SHALL be created as persistent
- **AND** persistent secrets SHALL survive database reconnection
- **AND** temporary secrets SHALL continue to be recreated on each connection

#### Scenario: Mixed persistence configuration
- **GIVEN** a configuration with both persistent and temporary secrets
- **WHEN** catalog connections are established
- **THEN** persistent secrets SHALL be created once if they don't exist
- **AND** temporary secrets SHALL be recreated on each connection
- **AND** the system SHALL handle both types appropriately