## ADDED Requirements

### Requirement: Security Regression Tests for SQL and Paths
The project MUST include regression tests that exercise security‑sensitive behavior for SQL generation and path resolution, to prevent re‑introducing previously fixed vulnerabilities.

#### Scenario: SQL injection regression tests
- **GIVEN** view configurations and secrets whose names and values contain quotes, semicolons, comments, and other potentially dangerous characters
- **WHEN** SQL is generated for catalog builds or dry‑run modes
- **THEN** automated tests assert that the resulting SQL remains syntactically valid
- **AND** configuration‑derived values remain safely contained within quoted identifiers or literals
- **AND** no additional statements can be injected via these fields.

#### Scenario: Path traversal regression tests
- **GIVEN** configurations that reference local files using relative and absolute paths, including attempts to escape the config directory via `..` segments or platform‑specific forms
- **WHEN** path resolution helpers are invoked during config loading or catalog builds
- **THEN** automated tests assert that only paths within allowed roots (such as the config directory) are accepted
- **AND** paths that resolve outside allowed roots cause configuration errors rather than silent acceptance.

