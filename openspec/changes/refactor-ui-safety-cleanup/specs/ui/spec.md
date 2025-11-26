## MODIFIED Requirements

### Requirement: UI Query Safety
The UI SHALL validate queries robustly to prevent DDL/DML or multi-statement execution in read-only endpoints.

#### Scenario: Robust single-statement check
- **WHEN** a query is submitted via the UI
- **THEN** the validation SHALL correctly reject multiple statements and DDL/DML even when semicolons or keywords appear inside strings or comments
- **AND** only safe SELECT statements SHALL be executed.

### Requirement: UI Task Lifecycle Management
Background task tracking SHALL avoid unbounded memory growth.

#### Scenario: Task store eviction
- **WHEN** background task results accumulate
- **THEN** the UI SHALL evict or expire old task entries based on a size limit or TTL to keep memory bounded.

### Requirement: UI Config Persistence Simplicity
Configuration persistence SHALL use a single, minimal atomic write helper.

#### Scenario: Simplified writer
- **WHEN** the UI saves configuration changes
- **THEN** it SHALL use one atomic write path for YAML/JSON, avoiding redundant helpers and complex fallbacks, while preserving format choice.

### Requirement: UI Static Asset Visibility
The UI SHALL surface when bundled static assets are missing.

#### Scenario: Missing static warning
- **WHEN** the UI starts and `static/` assets are absent
- **THEN** it SHALL log a clear warning instead of silently skipping the mount.
