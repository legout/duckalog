## MODIFIED Requirements

### Requirement: Logging Backend and Helpers
The logging implementation MUST preserve the public logging API and redaction
guarantees, and MAY use a third-party backend such as `loguru` under the hood.

#### Scenario: Logging uses loguru backend
- **GIVEN** the Duckalog implementation uses `loguru` as the underlying
  logging library
- **WHEN** application code calls the public helpers `log_info`, `log_debug`,
  or `log_error`
- **THEN** log messages are emitted through `loguru`
- **AND** existing behavior around log levels and structured details is
  preserved.

#### Scenario: Redaction behavior preserved
- **GIVEN** logs are emitted via the updated helpers
- **WHEN** details include keys such as `password`, `secret`, `token`, or
  similar
- **THEN** the logged output contains redacted placeholders instead of the raw
  secret values
- **AND** this behavior is independent of the underlying logging backend.
