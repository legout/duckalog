## MODIFIED Requirements

### Requirement: UI Config Loading
Duckalog UI SHALL load configuration from YAML/JSON catalog files and provide clear guidance when the input is invalid.

#### Scenario: Reject non-text/binary inputs
- **WHEN** the UI is invoked with a path that is clearly a database/binary file (e.g., `.duckdb`, `.db`, `.sqlite`) or fails UTF-8 decoding
- **THEN** the UI SHALL stop before startup
- **AND** emit an actionable error explaining that a Duckalog YAML/JSON config is required and suggest a valid path.

#### Scenario: Preserve normal config formats
- **WHEN** a valid YAML or JSON config is provided
- **THEN** the UI SHALL load it successfully using the detected format without regression to existing behavior.

### Requirement: UI Schema Inspection Safety
The UI SHALL perform schema inspection using safe identifier handling.

#### Scenario: Safe describe queries
- **WHEN** the UI describes a view for schema display
- **THEN** the view name SHALL be safely quoted/validated to avoid SQL errors or injection via identifier misuse.

### Requirement: UI Dependency Hygiene
The UI code SHALL avoid redundant imports and initialization that can mask errors or bloat startup.

#### Scenario: Deduplicated datastar import
- **WHEN** importing UI dependencies
- **THEN** datastar SHALL be imported once with a single clear error message if missing.
