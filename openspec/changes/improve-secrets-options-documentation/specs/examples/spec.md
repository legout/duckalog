## ADDED Requirements
### Requirement: S3 Options Usage Examples
The examples repository SHALL include comprehensive S3 secret configurations demonstrating various \`options\` field use cases.

#### Scenario: User needs S3 with custom SSL settings
- **WHEN** a user views S3 secret examples
- **THEN** there are examples showing \`options.use_ssl: true/false\` configurations
- **AND** the examples explain when to disable SSL for testing

#### Scenario: User requires S3 URL style configuration
- **WHEN** a user works with S3-compatible storage
- **THEN** examples show \`options.url_style: 'path'|'virtual'\` usage
- **AND** the documentation explains compatibility requirements

### Requirement: Advanced S3 Configuration Examples
The examples SHALL demonstrate advanced S3 configurations commonly needed in production environments.

#### Scenario: User configures MinIO or S3-compatible storage
- **WHEN** a user sets up non-AWS S3 storage
- **THEN** examples show custom endpoint with appropriate options
- **AND** the examples include typical MinIO configuration parameters

#### Scenario: User needs S3 session token configuration
- **WHEN** a user works with temporary AWS credentials
- **THEN** examples show session token usage in options field
- **AND** the documentation explains credential rotation patterns

### Requirement: Cross-Type Options Comparison Examples
The examples SHALL include side-by-side comparisons showing how the \`options\` field works across different secret types.

#### Scenario: User learns options patterns across secret types
- **WHEN** a user reviews multiple secret type examples
- **THEN** the patterns show consistent options usage structure
- **AND** comparisons highlight type-specific vs universal options
