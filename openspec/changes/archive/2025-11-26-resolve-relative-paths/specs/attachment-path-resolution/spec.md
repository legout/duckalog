# Attachment Path Resolution Specification

## MODIFIED Requirements

### Requirement: APR-001 - DuckDB Attachment Path Resolution
DuckDB attachment paths SHALL support relative path resolution similar to view data sources.

#### Scenario: Relative DuckDB Attachment Path
Given a DuckDB attachment configuration with `path: "data/reference.duckdb"` in a config at `/project/config/catalog.yaml`
When the configuration is processed  
Then the resolved attachment path SHALL be `/project/config/data/reference.duckdb`

#### Scenario: Absolute DuckDB Attachment Path (Existing)
Given a DuckDB attachment configuration with `path: "/absolute/path/reference.duckdb"`
When the configuration is processed  
Then the path SHALL remain unchanged (backward compatibility)

#### Scenario: Attachment SQL Generation
Given a DuckDB attachment with a resolved relative path
When the ATTACH DATABASE SQL is generated  
Then the statement SHALL use the absolute path

#### Scenario: Attachment Error Handling
Given an invalid relative attachment path
When the configuration is processed  
Then the system SHALL raise a clear error with the original and resolved paths

### Requirement: APR-002 - SQLite Attachment Path Resolution  
SQLite attachment paths SHALL support relative path resolution.

#### Scenario: Relative SQLite Attachment Path
Given a SQLite attachment configuration with `path: "./data/users.db"`
When the configuration is processed  
Then the path SHALL be resolved relative to the config file directory

#### Scenario: SQLite Attachment Validation
Given a resolved SQLite attachment path
When processed  
Then the system SHALL validate that the SQLite file is accessible

#### Scenario: Cross-Platform SQLite Paths
Given a SQLite attachment path on any platform
When resolved  
Then the final path SHALL use correct platform-specific separators

### Requirement: APR-003 - Attachment Security Validation
Attachment path resolution SHALL include security validation to prevent unauthorized file access.

#### Scenario: Attachment Directory Traversal Prevention
Given an attachment path like `path: "../../../sensitive.db"`
When the configuration is processed  
Then the system SHALL raise a security validation error

#### Scenario: Attachment Path Sandboxing
Given any attachment path in the configuration
When resolved  
Then the final path MUST be within the configuration file's directory tree

#### Scenario: Attachment File Permission Validation
Given a resolved attachment path to a file without read permissions
When processed  
Then the system SHALL raise an appropriate access error

### Requirement: APR-004 - Backward Compatibility for Attachments
Existing attachment configurations with absolute paths SHALL continue to work unchanged.

#### Scenario: Existing Absolute Attachment Paths
Given an existing configuration with absolute attachment paths
When processed with the new system  
Then the configuration SHALL work identically to the previous version

#### Scenario: Attachment Migration
Given an attachment configuration that could use relative paths
When processed  
Then the system SHALL provide optional migration suggestions

## ADDED Requirements

### Requirement: APR-005 - Attachment Path Resolution Controls
Attachment path resolution SHALL be controllable through configuration options.

#### Scenario: Selective Attachment Resolution
Given a configuration with the path resolution option disabled
When loaded  
Then attachment paths SHALL remain unchanged

#### Scenario: Global Attachment Resolution Setting
Given a global setting for path resolution behavior
When multiple attachments are processed  
Then they SHALL all follow the same resolution policy

#### Scenario: Per-Attachment Override
Given a configuration with mixed absolute and relative attachment paths
When processed  
Then only the relative paths SHALL be resolved

### Requirement: APR-006 - Attachment Path Diagnostics
The system SHALL provide diagnostic information for attachment path resolution.

#### Scenario: Path Resolution Debugging
Given a configuration with attachment paths
When processed with debug mode enabled  
Then the system SHALL log path resolution actions

#### Scenario: Attachment Path Validation Report
Given a configuration with multiple attachments
When validated  
Then the system SHALL provide a report of all resolved paths and their accessibility

#### Scenario: Attachment Resolution Dry Run
Given a configuration with attachment paths
When processed in dry-run mode  
Then the system SHALL show resolved paths without applying them