## ADDED Requirements
### Requirement: DuckDB Secrets Configuration
The system SHALL allow users to define DuckDB secrets in the catalog configuration file for accessing external services and databases.

#### Scenario: S3 secret with CONFIG provider
- **WHEN** a user provides an S3 secret configuration in YAML
- **THEN** the system SHALL execute `CREATE SECRET` with the specified KEY_ID, SECRET, REGION, and other parameters

#### Scenario: Persistent secret with scope
- **WHEN** a user provides a persistent secret with a scope prefix
- **THEN** the system SHALL execute `CREATE PERSISTENT SECRET ... SCOPE 'prefix'` to create a scoped persistent secret

#### Scenario: Multiple secrets for same service type
- **WHEN** a user defines multiple S3 secrets with different scopes
- **THEN** the system SHALL create all secrets and allow DuckDB to automatically select the appropriate one based on path matching

#### Scenario: Secret with credential_chain provider
- **WHEN** a user provides a secret using the credential_chain provider
- **THEN** the system SHALL execute `CREATE SECRET ... USING credential_chain` to let DuckDB auto-fetch credentials

#### Scenario: Azure secret configuration
- **WHEN** a user provides an Azure secret with connection string or tenant ID
- **THEN** the system SHALL create the appropriate Azure secret type with the specified parameters

#### Scenario: Database secret for PostgreSQL
- **WHEN** a user provides a PostgreSQL secret with connection parameters
- **THEN** the system SHALL create a postgres secret type for use with PostgreSQL attachments

#### Scenario: Secret validation
- **WHEN** a user provides an invalid secret configuration (missing required fields for type)
- **THEN** the system SHALL raise a validation error during config loading

#### Scenario: Empty secrets configuration
- **WHEN** a user does not provide secrets or provides an empty list
- **THEN** the system SHALL continue without error and create no secrets

#### Scenario: Secrets with environment variables
- **WHEN** a user provides secret values using `${env:VAR_NAME}` syntax
- **THEN** the system SHALL interpolate environment variables before creating the secret

#### Scenario: HTTP secret for basic auth
- **WHEN** a user provides an HTTP secret with username and password
- **THEN** the system SHALL create an http secret type for HTTP basic authentication