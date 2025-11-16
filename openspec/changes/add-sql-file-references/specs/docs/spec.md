## MODIFIED Requirements

### Requirement: View SQL Sources
Views MUST support SQL queries from both inline configuration and external SQL files.

#### Scenario: Inline SQL continues to work unchanged
- **GIVEN** an existing configuration with inline SQL
- **WHEN** the configuration is processed by Duckalog
- **THEN** the inline SQL continues to function exactly as before
- **AND** no changes to existing behavior are introduced

#### Scenario: Backward compatibility maintained
- **GIVEN** a configuration file using inline `sql` fields
- **WHEN** the configuration is loaded and validated
- **THEN** all existing functionality remains unchanged
- **AND** no migration is required for existing configurations

## ADDED Requirements

### Requirement: SQL File References
Views MUST support referencing SQL queries from external `.sql` files instead of inline content.

#### Scenario: Simple SQL file reference
- **GIVEN** a configuration with `sql_file` field pointing to a valid SQL file
- **WHEN** the configuration is processed
- **THEN** Duckalog MUST load the SQL content from the specified file
- **AND** use that SQL content for view creation
- **AND** resolve the file path relative to the configuration file location

#### Scenario: SQL file existence validation
- **GIVEN** a configuration referencing a non-existent SQL file
- **WHEN** the configuration is validated
- **THEN** Duckalog MUST raise a clear error indicating the missing file
- **AND** provide the expected file path for user reference

#### Scenario: SQL file path resolution
- **GIVEN** a configuration with relative path `sql_file: "queries/user_activity.sql"`
- **AND** the configuration file is located at `/project/config/catalog.yaml`
- **WHEN** the SQL file is resolved
- **THEN** Duckalog MUST look for the file at `/project/config/queries/user_activity.sql`

#### Scenario: Security path restrictions
- **GIVEN** a configuration attempting to reference a SQL file outside allowed directories
- **WHEN** the path resolution occurs
- **THEN** Duckalog MUST prevent access and raise a security error
- **AND** provide clear guidance on allowed path patterns

### Requirement: Template SQL Processing
Views MUST support SQL templates with variable substitution from configuration.

#### Scenario: Template variable substitution
- **GIVEN** a configuration with `sql_template` field and `sql_variables`
- **AND** the template contains `{{ table_name }}` placeholders
- **WHEN** the template is processed
- **THEN** Duckalog MUST replace placeholders with variable values from `sql_variables`
- **AND** produce valid SQL with substituted values

#### Scenario: Environment variable substitution in templates
- **GIVEN** a template containing `${env:AWS_REGION}` placeholders
- **AND** the environment variable is set to `us-west-2`
- **WHEN** the template is processed
- **THEN** Duckalog MUST replace the placeholder with the environment variable value
- **AND** maintain existing environment variable interpolation behavior

#### Scenario: Template validation
- **GIVEN** a template with undefined variables
- **WHEN** template processing occurs
- **THEN** Duckalog MUST detect undefined variables
- **AND** provide clear error messages indicating missing variable definitions
- **AND** prevent view creation until variables are properly defined

### Requirement: Configuration Schema Updates
The configuration schema MUST accept new fields for SQL file references while maintaining existing functionality.

#### Scenario: Schema validation for SQL reference fields
- **GIVEN** a view configuration with `sql_file` field
- **WHEN** the configuration is validated
- **THEN** the schema MUST accept the new field
- **AND** ensure mutual exclusivity with inline `sql` field
- **AND** validate that at least one SQL source (inline or file) is provided

#### Scenario: Multiple SQL reference formats
- **GIVEN** a view configuration supporting different SQL source types
- **WHEN** the configuration is processed
- **THEN** Duckalog MUST support:
  - `sql` (inline SQL) - existing behavior
  - `sql_file` (direct file reference)
  - `sql_template` (template with variables)
  - `sql_directory` (directory of SQL files for batch processing)

### Requirement: SQL File Content Validation
Duckalog MUST validate SQL file content to ensure it's properly formatted and safe to execute.

#### Scenario: SQL file encoding validation
- **GIVEN** a referenced SQL file
- **WHEN** the file content is loaded
- **THEN** Duckalog MUST validate the file is valid UTF-8
- **AND** raise an error for files with invalid encoding
- **AND** provide guidance on encoding requirements

#### Scenario: SQL syntax validation
- **GIVEN** a SQL file with content
- **WHEN** the file is processed for view creation
- **THEN** Duckalog MAY perform basic SQL syntax validation
- **AND** provide helpful error messages for syntax issues
- **AND** allow processing to continue for minor formatting issues

#### Scenario: SQL file size limits
- **GIVEN** a SQL file that exceeds configured size limits
- **WHEN** the file is loaded
- **THEN** Duckalog MUST enforce size limits
- **AND** raise an error for files that are too large
- **AND** provide guidance on file size constraints

### Requirement: Integration with Existing Components
SQL file references MUST integrate seamlessly with existing Duckalog components.

#### Scenario: CLI integration
- **GIVEN** a configuration using SQL file references
- **WHEN** the `duckalog validate` command is executed
- **THEN** the validation MUST include SQL file existence and readability checks
- **AND** provide clear status reporting for SQL file processing

#### Scenario: Generate SQL functionality
- **GIVEN** a configuration with SQL file references
- **WHEN** `duckalog generate-sql` is executed
- **THEN** the generated SQL MUST include the actual content from referenced files
- **AND** resolve all template variables appropriately

#### Scenario: Build catalog processing
- **GIVEN** a configuration with SQL file references
- **WHEN** `duckalog build` is executed
- **THEN** Duckalog MUST:
  - Load and process all referenced SQL files
  - Handle template substitution correctly
  - Report any SQL file processing errors clearly
  - Maintain existing catalog creation behavior

### Requirement: Error Handling and User Experience
Duckalog MUST provide clear, actionable error messages for SQL file reference issues.

#### Scenario: Missing file error
- **GIVEN** a configuration referencing a non-existent SQL file
- **WHEN** configuration processing occurs
- **THEN** the error message MUST include:
  - Clear indication that a SQL file is missing
  - The expected file path
  - The configuration file and line reference
  - Suggestions for resolving the issue

#### Scenario: Permission denied error
- **GIVEN** a configuration referencing a SQL file without read permissions
- **WHEN** file access is attempted
- **THEN** Duckalog MUST provide a clear error indicating permission issues
- **AND** suggest steps to resolve permission problems

#### Scenario: Template processing error
- **GIVEN** a template with variable substitution issues
- **WHEN** template processing occurs
- **THEN** the error MUST indicate:
  - Which template variables are problematic
  - Whether variables are missing or have invalid formats
  - Where in the template the issue occurs (line numbers if possible)

### Requirement: Performance and Resource Management
SQL file references MUST not significantly impact performance or resource usage.

#### Scenario: SQL file caching
- **GIVEN** multiple views referencing the same SQL file
- **WHEN** the configuration is processed
- **THEN** Duckalog SHOULD load each SQL file only once
- **AND** cache the content to avoid redundant file reads
- **AND** provide cache invalidation when files are modified

#### Scenario: Large file handling
- **GIVEN** SQL files that are very large (several megabytes)
- **WHEN** the files are loaded and processed
- **THEN** Duckalog MUST handle them efficiently
- **AND** provide progress indication for lengthy operations
- **AND** avoid excessive memory consumption

#### Scenario: Concurrent access
- **GIVEN** multiple configurations accessing the same SQL files simultaneously
- **WHEN** the configurations are processed concurrently
- **THEN** Duckalog MUST handle concurrent file access properly
- **AND** avoid file locking issues where possible

### Requirement: Cross-Platform Compatibility
SQL file reference functionality MUST work consistently across different operating systems.

#### Scenario: Path separator handling
- **GIVEN** a configuration with forward slashes in SQL file paths
- **WHEN** the configuration is processed on Windows
- **THEN** Duckalog MUST handle path separators correctly
- **AND** convert paths appropriately for the operating system

#### Scenario: Absolute path support
- **GIVEN** a configuration with absolute file paths
- **WHEN** the paths are resolved on different operating systems
- **THEN** Duckalog MUST handle absolute paths according to OS conventions
- **AND** maintain security restrictions regardless of operating system

#### Scenario: File system case sensitivity
- **GIVEN** a configuration referencing a SQL file with specific casing
- **WHEN** the file is looked up on case-insensitive file systems
- **THEN** Duckalog MUST handle case variations appropriately
- **AND** provide consistent behavior across different file systems

## REMOVED Requirements

- None - this feature adds functionality without removing existing capabilities

## RENAMED Requirements

- None - existing functionality remains unchanged, new capabilities are added