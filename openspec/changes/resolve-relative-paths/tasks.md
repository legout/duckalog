# Relative Path Resolution Tasks

## 1. Path Resolution Utilities (Phase 1)
- [x] 1.1 Create path resolution utility module
  - [x] Implement `is_relative_path()` function to detect relative paths
  - [x] Implement `resolve_relative_path()` function for path resolution
  - [x] Add cross-platform path handling with pathlib
  - [x] Create path validation functions for security
  - [x] Add Windows-specific drive detection logic

- [x] 1.2 Implement security validation
  - [x] Add directory traversal attack prevention
  - [x] Implement path sandboxing relative to config directory
  - [x] Create path access validation rules
  - [x] Add security test cases for malicious paths

## 2. Configuration Integration (Phase 1)
- [x] 2.1 Integrate path resolution into ViewConfig validation
  - [x] Add path resolution to ViewConfig model validator
  - [x] Implement resolution for Parquet and Delta sources
  - [x] Preserve original path for error messages
  - [x] Add resolved path tracking for debugging

- [x] 2.2 Update configuration loading pipeline
  - [x] Pass config file path to resolution functions
  - [x] Integrate resolution in load_config() function
  - [x] Handle edge cases (missing config file paths)
  - [x] Add logging for path resolution actions

## 3. SQL Generation Updates (Phase 1)
- [x] 3.1 Update SQL generation for resolved paths
  - [x] Modify generate_view_sql() to use resolved paths
  - [x] Ensure absolute paths are properly quoted
  - [x] Handle Windows path formatting in SQL
  - [x] Maintain backward compatibility with absolute paths

- [x] 3.2 Update attachment path handling
  - [x] Apply resolution to DuckDB and SQLite attachments
  - [x] Update attachment SQL generation
  - [x] Add validation for attachment file accessibility
  - [x] Test attachment path resolution

## 4. Testing and Validation (Phase 2)
- [x] 4.1 Create comprehensive test suite
  - [x] Unit tests for path resolution utilities
  - [x] Integration tests for configuration loading
  - [x] End-to-end tests for catalog building
  - [x] Cross-platform compatibility tests

- [x] 4.2 Add security and edge case testing
  - [x] Directory traversal attack tests
  - [x] Malicious path validation tests
  - [x] Windows path handling tests
  - [x] Permission and access denied tests

- [ ] 4.3 Update existing examples
  - [ ] Convert examples to use relative paths where appropriate
  - [ ] Add documentation of path resolution behavior
  - [ ] Validate all existing configurations still work
  - [ ] Add path resolution examples to documentation

## 5. Documentation and Migration (Phase 2)
- [ ] 5.1 Update documentation
  - [ ] Document path resolution behavior in README
  - [ ] Add examples to configuration documentation
  - [ ] Create migration guide for existing users
  - [ ] Update API documentation for config module

- [ ] 5.2 Create migration utilities
  - [ ] Add CLI flag to show resolved paths (dry-run mode)
  - [ ] Create utility to convert absolute to relative paths
  - [ ] Add validation command to check path accessibility
  - [ ] Document best practices for path management