## MODIFIED Requirements

### Requirement: Logging Levels and Secret Handling

#### Scenario: Logger backend compatibility
- **WHEN** the project is run with or without the `loguru` dependency installed
- **THEN** the logging utilities SHALL expose a logger interface that is compatible with the standard Python logging API for the rest of the codebase
- **AND** type-level annotations for the logger handle SHALL allow for the presence or absence of loguru without causing inconsistent types at call sites.

