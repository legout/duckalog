## ADDED Requirements
### Requirement: Comprehensive Secrets Options Documentation
The documentation SHALL clearly document the \`options\` field for all DuckDB secret types, explaining that it accepts additional key-value parameters specific to each secret type.

#### Scenario: User finds options field in S3 documentation
- **WHEN** a user reads the S3 Secret Fields table
- **THEN** the \`options\` field is listed with clear explanation of its purpose
- **AND** the documentation explains it accepts DuckDB-specific S3 parameters

#### Scenario: User understands options availability across all secret types
- **WHEN** a user reviews any secret type documentation
- **THEN** the \`options\` field is consistently documented as available
- **AND** the documentation clarifies its universal availability

### Requirement: Practical S3 Options Examples
The documentation SHALL include practical examples of using the \`options\` field with S3 secrets to handle common real-world scenarios.

#### Scenario: User needs S3 SSL and URL style configuration
- **WHEN** a user reads S3 secret examples
- **THEN** there are examples showing \`use_ssl\` and \`url_style\` in options
- **AND** the examples include both path and virtual URL styles

#### Scenario: User requires custom S3 endpoint parameters
- **WHEN** a user needs non-standard S3 configuration
- **THEN** examples show common custom endpoint options
- **AND** the documentation explains parameter impact

### Requirement: Secret Type Documentation Consistency
All secret type documentation tables SHALL follow the same structure and consistently document the \`options\` field.

#### Scenario: User compares different secret types
- **WHEN** a user reviews S3, Azure, GCS, and Database secret tables
- **THEN** the \`options\` field appears in all tables consistently
- **AND** explanations of its purpose are uniform across types
