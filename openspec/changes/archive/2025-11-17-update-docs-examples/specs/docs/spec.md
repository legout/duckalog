## MODIFIED Requirements

### Requirement: Documentation Depth and Examples
The documentation site MUST provide narrative guidance and practical examples
for common Duckalog workflows.

#### Scenario: Quickstart shows an end-to-end workflow
- **GIVEN** a user opening the documentation landing page
- **WHEN** they read the quickstart section
- **THEN** they see a minimal but realistic example that includes:
  - A sample configuration file.
  - Instructions for running `duckalog build`, `duckalog generate-sql`, and
    `duckalog validate`.
  - A short Python snippet using the same config.

#### Scenario: User guide covers common patterns and troubleshooting
- **GIVEN** a user reading the user guide
- **WHEN** they look for guidance on common config patterns and errors
- **THEN** they find sections that describe typical setups (e.g. Parquet-only,
  attachments-only, Iceberg-only)
- **AND** a short troubleshooting section that explains how to interpret and
  resolve common errors (e.g. missing env vars, missing attachments/catalogs,
  invalid config fields).

#### Scenario: Example configs are discoverable
- **GIVEN** example configuration files included under `docs/`
- **WHEN** a user follows links from the user guide or quickstart
- **THEN** they can view and reuse these examples as a starting point for
  their own configs.

