# Secrets SQL Generation Specification

## Purpose
Define how Duckalog generates SQL statements for creating DuckDB secrets from configuration objects.

## ADDED Requirements

### Requirement: SQL Generation for CREATE SECRET
The system SHALL generate valid DuckDB `CREATE [PERSISTENT] SECRET` SQL statements from validated SecretConfig objects.

#### Scenario: Generate S3 secret with config provider
- **GIVEN** a secret with `type: s3`, `provider: config`, `name: prod_s3`, `key_id: AKIA123`, `secret: secret456`, `region: us-west-2`
- **WHEN** `generate_secret_sql()` is called
- **THEN** it SHALL return `CREATE SECRET prod_s3 (TYPE s3, KEY_ID 'AKIA123', SECRET 'secret456', REGION 'us-west-2')`

#### Scenario: Generate persistent S3 secret
- **GIVEN** a secret with `type: s3`, `provider: config`, `persistent: true`, `name: prod_s3`, `key_id: AKIA123`, `secret: secret456`
- **WHEN** `generate_secret_sql()` is called
- **THEN** it SHALL return `CREATE PERSISTENT SECRET prod_s3 (TYPE s3, KEY_ID 'AKIA123', SECRET 'secret456')`

#### Scenario: Generate S3 secret with scope
- **GIVEN** a secret with `type: s3`, `name: scoped_s3`, `scope: 'prod/'`, `key_id: AKIA123`, `secret: secret456`
- **WHEN** `generate_secret_sql()` is called
- **THEN** it SHALL return `CREATE SECRET scoped_s3 (TYPE s3, KEY_ID 'AKIA123', SECRET 'secret456'; SCOPE 'prod/')`

#### Scenario: Generate S3 secret with credential_chain provider
- **GIVEN** a secret with `type: s3`, `provider: credential_chain`, `name: auto_s3`, `region: us-east-1`
- **WHEN** `generate_secret_sql()` is called
- **THEN** it SHALL return `CREATE SECRET auto_s3 (TYPE s3, PROVIDER credential_chain, REGION 'us-east-1')`

#### Scenario: Generate Azure secret with connection string
- **GIVEN** a secret with `type: azure`, `name: azure_prod`, `connection_string: 'DefaultEndpointsProtocol=...'`
- **WHEN** `generate_secret_sql()` is called
- **THEN** it SHALL return `CREATE SECRET azure_prod (TYPE azure, CONNECTION_STRING 'DefaultEndpointsProtocol=...')`

#### Scenario: Generate Azure secret with tenant_id and account_name
- **GIVEN** a secret with `type: azure`, `name: azure_prod`, `tenant_id: tenant123`, `account_name: myaccount`, `secret: mysecret`
- **WHEN** `generate_secret_sql()` is called
- **THEN** it SHALL return `CREATE SECRET azure_prod (TYPE azure, TENANT_ID 'tenant123', ACCOUNT_NAME 'myaccount', SECRET 'mysecret')`

#### Scenario: Generate database secret with connection string
- **GIVEN** a secret with `type: postgres`, `name: pg_prod`, `connection_string: 'postgresql://user:pass@host/db'`
- **WHEN** `generate_secret_sql()` is called
- **THEN** it SHALL return `CREATE SECRET pg_prod (TYPE postgres, CONNECTION_STRING 'postgresql://user:pass@host/db')`

#### Scenario: Generate database secret with individual parameters
- **GIVEN** a secret with `type: postgres`, `name: pg_prod`, `host: localhost`, `port: 5432`, `database: analytics`, `key_id: user`, `secret: pass`
- **WHEN** `generate_secret_sql()` is called
- **THEN** it SHALL return `CREATE SECRET pg_prod (TYPE postgres, HOST 'localhost', PORT 5432, DATABASE 'analytics', USER 'user', PASSWORD 'pass')`

#### Scenario: Generate HTTP secret for basic auth
- **GIVEN** a secret with `type: http`, `name: api_auth`, `key_id: username`, `secret: password`
- **WHEN** `generate_secret_sql()` is called
- **THEN** it SHALL return `CREATE SECRET api_auth (TYPE http, USERNAME 'username', PASSWORD 'password')`

#### Scenario: Generate secret with options
- **GIVEN** a secret with `type: s3`, `options: {url_style: 'path', use_ssl: true}`
- **WHEN** `generate_secret_sql()` is called
- **THEN** it SHALL include the options in the SECRET parameters

### Requirement: Credential Redaction
The system SHALL redact sensitive credentials in debug output to prevent secret leakage.

#### Scenario: Redacted credentials in debug output
- **GIVEN** a secret with credentials (e.g., SECRET 'mysecret')
- **WHEN** debugging is enabled
- **THEN** credentials SHALL appear as `***REDACTED***` in logs
- **AND** the actual credentials SHALL NOT be logged

### Requirement: Dry-Run SQL Generation for Secrets
The system SHALL include CREATE SECRET statements in dry-run output when secrets are configured.

#### Scenario: Include secrets in dry-run SQL
- **GIVEN** a config with secrets defined
- **WHEN** `build_catalog(config, dry_run=True)` is called
- **THEN** the returned SQL SHALL include CREATE SECRET statements
- **AND** CREATE SECRET statements SHALL appear before CREATE VIEW statements
