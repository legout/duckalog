## ADDED Requirements
### Requirement: S3 Options Field Documentation
The S3 secret documentation SHALL clearly document the \`options\` field and provide practical examples for common S3-specific parameters.

#### Scenario: User needs to configure S3 SSL settings
- **WHEN** a user reads the S3 Secret Fields table
- **THEN** the \`options\` field is listed with description of S3-specific parameters
- **AND** common parameters like \`use_ssl\` are documented

#### Scenario: User works with S3-compatible storage
- **WHEN** a user needs to configure URL style for MinIO or similar
- **THEN** the documentation shows \`options.url_style\` usage
- **AND** explains the difference between 'path' and 'virtual' styles

### Requirement: S3 Options Usage Examples
The documentation SHALL include practical S3 examples demonstrating the \`options\` field with environment variable integration.

#### Scenario: User needs S3 with custom SSL and URL style
- **WHEN** a user views S3 secret examples
- **THEN** there is an example showing both \`use_ssl\` and \`url_style\` in options
- **AND** the example uses environment variables for security
- **AND** the example includes explanatory comments

#### Scenario: User learns environment variable patterns for S3 options  
- **WHEN** a user sees the options example
- **THEN** the pattern shows how to reference environment variables in options
- **AND** the example validates successfully without errors
