## MODIFIED Requirements

### Requirement: DuckDB Secrets Configuration
The system SHALL allow users to define DuckDB secrets in the catalog configuration file with controllable persistence behavior, defaulting to temporary secrets for security.

#### Scenario: SecretConfig with controllable persistence
- **WHEN** a user provides secret configurations using the `SecretConfig` model
- **THEN** the system SHALL use the `persistent` field (defaulting to `false`) to control secret persistence
- **AND** temporary secrets (`persistent: false` or unspecified) SHALL be recreated on each connection
- **AND** persistent secrets (`persistent: true`) SHALL be created once and survive reconnections

#### Scenario: Temporary secrets for security
- **GIVEN** a secret configuration without explicit `persistent: true`
- **WHEN** catalog connections are established
- **THEN** the secret SHALL be created as temporary using `CREATE SECRET`
- **AND** the secret SHALL NOT be stored in the database file
- **AND** the secret SHALL be recreated on each new connection

#### Scenario: Persistent secrets for convenience
- **GIVEN** a secret configuration with `persistent: true`
- **WHEN** catalog connections are established
- **THEN** the secret SHALL be created as persistent using `CREATE PERSISTENT SECRET`
- **AND** the secret SHALL be stored in the database file and survive reconnections
- **AND** existing persistent secrets SHALL not be recreated unless missing

#### Scenario: Security-conscious default behavior
- **GIVEN** any secret configuration without explicit persistence setting
- **WHEN** the configuration is loaded
- **THEN** the secret SHALL default to `persistent: false` for security
- **AND** users must explicitly opt-in to secret persistence
- **AND** documentation SHALL explain the security implications