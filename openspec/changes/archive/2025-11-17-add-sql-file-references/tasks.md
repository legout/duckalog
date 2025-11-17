# Tasks: Add SQL File References Support

## 1. Core Infrastructure Implementation

- [x] 1.1 Create SQLFileLoader class:
  - Implement file existence validation
  - Add file readability checks
  - Include path resolution logic (relative to config file)
  - Add size limit validation to prevent large file issues
  
- [x] 1.2 Implement PathResolver utility:
  - Support relative path resolution from config file location
  - Handle absolute path validation with security checks
  - Add path normalization (resolve .., ., redundant separators)
  - Include cross-platform path handling (Windows/macOS/Linux)
  
- [x] 1.3 Add SQLFileReference data model:
  - Create new Pydantic models for SQL file references
  - Support sql_file, sql_template, and sql_directory fields
  - Add sql_variables and env/config substitution options
  - Include validation rules for field combinations
  
- [x] 1.4 Update View model:
  - Add new fields for SQL file references to existing View model
  - Implement mutual exclusivity validation (sql vs sql_file vs sql_template)
  - Maintain backward compatibility with existing inline sql field
  - Add proper field documentation and examples

## 2. Template Processing Engine

- [x] 2.1 Create TemplateProcessor class:
  - Implement {{ variable }} substitution from config
  - Support ${env:ENV_VAR} environment variable substitution
  - Add ${config:path} configuration value substitution
  - Include recursive template processing
  
- [x] 2.2 Add variable validation:
  - Validate template variable names and formats
  - Check for undefined variables in templates
  - Add circular reference detection
  - Include variable type validation (string, number, boolean)
  
- [x] 2.3 Implement template security:
  - Add variable name sanitization to prevent injection
  - Prevent access to sensitive system variables
  - Include template context isolation
  - Add validation for variable value types and formats

## 3. Configuration Parser Integration

- [x] 3.1 Update ConfigParser to handle SQL file references:
  - Add SQL file loading during configuration parsing
  - Implement inline SQL vs file reference logic
  - Add proper error handling for missing/invalid files
  - Include processing status tracking
  
- [x] 3.2 Enhance error handling and validation:
  - Add clear error messages for missing SQL files
  - Include file permission/access errors
  - Add SQL syntax validation error reporting
  - Include template processing error details
  
- [x] 3.3 Update load_config function:
  - Modify to accept SQL file loading parameters
  - Add option to skip SQL file validation for performance
  - Include caching mechanism for frequently accessed SQL files
  - Add progress reporting for large SQL file processing

## 4. View Builder Integration

- [x] 4.1 Update ViewBuilder to use SQL from files:
  - Modify view creation logic to load SQL from external files
  - Add support for template processing in view generation
  - Include fallback to inline SQL for backward compatibility
  - Add view validation with external SQL
  
- [x] 4.2 Implement View dependency tracking:
  - Track SQL file dependencies for change detection
  - Add incremental rebuild support when SQL files change
  - Include dependency graph visualization for debugging
  - Add performance monitoring for SQL file loading

## 5. Validation and Security

- [x] 5.1 Add comprehensive file system validation:
  - Implement file existence checks before processing
  - Add file encoding validation (UTF-8 requirement)
  - Include file permission checks (read access validation)
  - Add size limit enforcement (configurable limits)
  
- [x] 5.2 Implement security restrictions:
  - Add path sandboxing to prevent directory traversal
  - Include restricted directory configuration
  - Add file extension validation (.sql only)
  - Include malicious file detection and prevention
  
- [x] 5.3 Add SQL content validation:
  - Implement basic SQL syntax parsing
  - Add SQL injection pattern detection
  - Include query complexity analysis
  - Add database-specific SQL validation rules

## 6. Testing Infrastructure

- [x] 6.1 Create comprehensive test suite:
  - Unit tests for SQLFileLoader class
  - Integration tests for TemplateProcessor
  - Path resolution tests for all platforms
  - Template variable substitution tests
  
- [x] 6.2 Add end-to-end testing:
  - Test complete workflow from config to view creation
  - Include error scenario testing (missing files, invalid SQL, etc.)
  - Add performance testing with large SQL files
  - Include backward compatibility verification
  
- [x] 6.3 Create fixture and sample data:
  - Create sample SQL files for testing
  - Add template examples with various variable types
  - Include complex SQL queries for stress testing
  - Add test configurations with mixed inline and file references

## 7. Documentation and Examples

- [x] 7.1 Create comprehensive documentation:
  - Add SQL file reference section to user guide
  - Create migration guide from inline to file references
  - Include best practices and security considerations
  - Add troubleshooting guide for common issues
  
- [x] 7.2 Update existing examples:
  - Modify examples to demonstrate SQL file references
  - Include both simple file references and template usage
  - Add mixed inline/file reference examples
  - Include template variable substitution examples
  
- [x] 7.3 Create new example configurations:
  - Simple SQL file reference example
  - Template with variables example
  - Complex analytics with multiple SQL files
  - Security-conscious configuration with path restrictions

## 8. Performance Optimization

- [x] 8.1 Implement SQL file caching:
  - Add file content caching to avoid repeated reads
  - Include file modification timestamp checking
  - Add memory management for large SQL files
  - Include cache invalidation strategies
  
- [x] 8.2 Optimize path resolution:
  - Add path resolution caching
  - Include relative path optimization
  - Add cross-platform path handling optimization
  - Include path validation performance improvements

## 9. Error Handling and User Experience

- [x] 9.1 Enhance error reporting:
  - Add contextual error messages with file/line information
  - Include helpful suggestions for common issues
  - Add recovery suggestions for recoverable errors
  - Include debugging information for development mode
  
- [x] 9.2 Add validation reporting:
  - Include SQL file validation status reporting
  - Add template processing summary
  - Include dependency analysis results
  - Add performance metrics reporting

## 10. Final Integration and Validation

- [x] 10.1 Update CLI to support SQL file references:
  - Modify validate command to check SQL file existence
  - Update generate-sql to handle external SQL files
  - Add build command SQL file processing status
  - Include new command-line options for SQL file management
  
- [x] 10.2 Update Python API:
  - Add SQL file reference support to build_catalog function
  - Include template processing in generate_sql function
  - Add SQL file validation to validate_config function
  - Include new convenience functions for SQL file management
  
- [x] 10.3 Final integration testing:
  - Test complete workflow with real configurations
  - Verify backward compatibility with existing projects
  - Include performance regression testing
  - Add security penetration testing for file access

## Success Criteria

✅ **Core Functionality**: SQL file references work correctly with proper path resolution
✅ **Template Processing**: Variable substitution works for all supported formats
✅ **Backward Compatibility**: All existing inline SQL configurations continue to work unchanged
✅ **Security**: File access restrictions prevent unauthorized access and directory traversal
✅ **Performance**: SQL file loading doesn't significantly impact build time or memory usage
✅ **Error Handling**: Clear, actionable error messages for all failure scenarios
✅ **Documentation**: Complete migration guide and examples enable easy adoption
✅ **Testing**: Comprehensive test coverage ensures reliability across platforms

## Dependencies

- Pydantic for data model validation
- pathlib for cross-platform path handling
- SQL parser library (if implementing SQL syntax validation)
- Jinja2 or similar for template processing
- Existing Duckalog configuration and view building infrastructure

## Implementation Phases

**Phase 1 (Days 1-3): Core Infrastructure**
- Tasks 1.1-1.4: Basic SQL file loading and reference support

**Phase 2 (Days 4-6): Template Processing**
- Tasks 2.1-2.3: Template engine and variable substitution
- Tasks 3.1-3.3: Configuration parser integration

**Phase 3 (Days 7-9): Testing and Polish**
- Tasks 4.1-4.2: View builder integration
- Tasks 5.1-5.3: Security and validation
- Tasks 6.1-6.3: Testing infrastructure

**Phase 4 (Days 10-12): Documentation and Final Integration**
- Tasks 7.1-7.3: Documentation and examples
- Tasks 8.1-8.2: Performance optimization
- Tasks 9.1-9.2: Error handling improvements
- Tasks 10.1-10.3: Final integration and validation

## Estimated Timeline

**Total Implementation Time**: 12-15 days
- Core Implementation: 6-8 days
- Testing and Validation: 3-4 days  
- Documentation: 2-3 days
- Buffer for issues: 1-2 days