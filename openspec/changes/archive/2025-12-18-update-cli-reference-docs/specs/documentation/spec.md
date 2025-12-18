## MODIFIED Requirements

### Requirement: Complete CLI Reference
The documentation SHALL provide a comprehensive CLI command reference with all commands, flags, and examples that match the current implementation.

#### Scenario: Complete build command documentation
- **GIVEN** a user needing to understand all `duckalog build` options
- **WHEN** they consult the CLI reference
- **THEN** they find complete documentation for the build command including:
  - Implemented per-command flags (for example `--db-path`, `--dry-run`, `--verbose`, `--load-dotenv/--no-load-dotenv`)
  - Implemented shared filesystem flags (for example `--fs-protocol`, `--fs-key`, `--fs-secret`, `--aws-profile`, etc.) described as application-level options
  - Accurate usage examples for local and remote config paths
- **SO** they can use the build command successfully without relying on nonexistent flags.

#### Scenario: CLI reference matches `--help` output
- **GIVEN** the CLI is the source of truth for available flags
- **WHEN** a user runs `duckalog --help` or `duckalog <command> --help`
- **THEN** every flag and command referenced in `docs/reference/cli.md` exists in the corresponding help output
- **AND** the documentation does not reference removed or unimplemented flags (for example `--format` on commands where it does not exist).

#### Scenario: Show-imports diagnostics documentation
- **GIVEN** a user using config imports
- **WHEN** they need to debug import resolution
- **THEN** they find documentation for `duckalog show-imports` including implemented flags (for example `--diagnostics`, `--show-merged`, `--format`)
- **AND** documentation explains what diagnostics output means at a high level
- **SO** they can troubleshoot import issues effectively.
