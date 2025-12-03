## MODIFIED Requirements

### Requirement: Dashboard Documentation Entry Points
The dashboard documentation MUST describe how to launch the dashboard from the Python API and MAY describe CLI launch only if the `duckalog ui` command is clearly marked as optional or experimental.

#### Scenario: Python API documented as primary entry point
- **WHEN** users read the dashboard documentation
- **THEN** they see an example that launches the dashboard using the Python API (for example, `run_dashboard("catalog.yaml")`)
- **AND** the example is presented as the primary supported entry point.

#### Scenario: CLI example is marked as optional
- **WHEN** the documentation includes an example using `duckalog ui catalog.yaml`
- **THEN** the example clearly indicates that this CLI command may not be available in all installations
- **AND** directs users to the Python API entry point if the CLI command is not present.

