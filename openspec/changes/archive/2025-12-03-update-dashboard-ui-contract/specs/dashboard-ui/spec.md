## MODIFIED Requirements

### Requirement: Local Dashboard Launch
The system SHALL provide a way to launch a local web dashboard for a single Duckalog catalog from the Python API, and MAY optionally provide a CLI command for launching the same dashboard implementation.

#### Scenario: Launch dashboard from CLI with config path (optional)
- **GIVEN** a valid `catalog.yaml` configuration file on disk
- **AND** an installation where the `duckalog ui` CLI command is enabled
- **WHEN** the user runs `duckalog ui catalog.yaml`
- **THEN** a local HTTP server is started on a default host and port
- **AND** the CLI prints the URL where the dashboard is available.

