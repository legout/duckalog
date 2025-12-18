# Implementation Tasks: Early Secret Creation and Endpoint Protocol Handling

## Phase 1: Endpoint Protocol Stripping

### Task 1.1: Implement endpoint protocol stripping
- [x] **File**: `src/duckalog/sql_generation.py`
- [x] **Function**: `generate_secret_sql()`
- [x] **Lines**: 224-225 (S3 endpoint handling)
- [x] **Change**: Add protocol stripping logic for S3 endpoints
- [x] **Testing**: Verify with endpoints containing `http://`, `https://`, and no protocol
- [x] **Acceptance**: S3 secrets with protocol-prefixed endpoints work without errors

### Task 1.2: Add validation for endpoint values
- [x] **File**: `src/duckalog/sql_generation.py`
- [x] **Function**: `generate_secret_sql()`
- [x] **Change**: Add logging when protocol is stripped from endpoints
- [x] **Testing**: Ensure warnings appear in verbose mode
- [x] **Acceptance**: Users can see when endpoints are automatically cleaned

## Phase 2: Extract Secret Creation

### Task 2.1: Extract secret creation from _apply_duckdb_settings
- [x] **File**: `src/duckalog/engine.py`
- [x] **Function**: `_apply_duckdb_settings()`
- [x] **Change**: Remove `_create_secrets()` call from this function
- [x] **Testing**: Ensure extensions, pragmas, and settings still work normally
- [x] **Acceptance**: `_apply_duckdb_settings()` no longer creates secrets

### Task 2.2: Create standalone _create_secrets method
- [x] **File**: `src/duckalog/engine.py`
- [x] **Function**: `_create_secrets()` (already exists but ensure it's callable independently)
- [x] **Change**: Ensure method can be called independently without other setup
- [x] **Testing**: Verify method works when called directly
- [x] **Acceptance**: `_create_secrets()` works as a standalone method

## Phase 3: Update Build Execution Order

### Task 3.1: Update CatalogBuilder.build() execution order
- [x] **File**: `src/duckalog/engine.py`
- [x] **Function**: `CatalogBuilder.build()`
- [x] **Lines**: 86-90
- [x] **Change**: Reorder method calls to create secrets before attachments
- [x] **New Order**: 
  1. `_setup_connection()`
  2. `_apply_pragmas()` (no secrets)
  3. `_create_secrets()` (new position)
  4. `_setup_attachments()`
  5. `_create_views()`

### Task 3.2: Test main catalog build process
- [x] **File**: `tests/test_engine.py` (create or update)
- [x] **Test**: Verify the new execution order works correctly
- [x] **Scenarios**:
  - Catalog with only secrets (no attachments)
  - Catalog with secrets and S3 attachments
  - Catalog with secrets and non-S3 attachments
- [x] **Acceptance**: All test scenarios pass with the new order

## Phase 4: Update Child Catalog Process

### Task 4.1: Update ConfigDependencyGraph._build_database()
- [x] **File**: `src/duckalog/engine.py`
- [x] **Function**: `ConfigDependencyGraph._build_database()`
- [x] **Lines**: 450-462
- [x] **Change**: Ensure child catalogs also follow the new execution order
- [x] **Testing**: Create test for nested Duckalog attachments with S3 dependencies
- [x] **Acceptance**: Child catalogs create secrets before their own attachments

### Task 4.2: Test child catalog secret timing
- [x] **File**: `tests/test_engine.py`
- [x] **Test**: Verify child catalog build order
- [x] **Scenario**: Parent catalog with S3 attachment pointing to child catalog on S3
- [x] **Acceptance**: Child catalog secrets created before parent attempts to attach

## Phase 5: Validation and Error Handling

### Task 5.1: Add secret validation enhancement
- [x] **File**: `src/duckalog/config/loader.py` or `src/duckalog/engine.py`
- [x] **Change**: Add validation for unresolved environment variables in secrets
- [x] **Testing**: Test with missing environment variables
- [x] **Acceptance**: Clear error messages for missing secret environment variables

### Task 5.2: Enhance error messages for connection failures
- [x] **File**: `src/duckalog/engine.py`
- [x] **Change**: Improve error messages when secrets fail to enable connections
- [x] **Testing**: Test with intentionally broken secret configurations
- [x] **Acceptance**: Error messages clearly indicate secret-related issues

## Phase 6: Comprehensive Testing

### Task 6.1: Test S3 attachment scenarios
- [x] **File**: `tests/test_engine.py`
- [x] **Tests**: 
  - S3 attachment with matching S3 secret
  - S3 attachment without proper secret (should fail clearly)
  - S3 attachment with protocol-prefixed endpoint
- [x] **Acceptance**: All S3 attachment scenarios work as expected

### Task 6.2: Test backward compatibility
- [x] **File**: `tests/test_engine.py`
- [x] **Tests**:
  - Existing configurations without remote attachments
  - Configurations with local attachments only
  - Configurations with different secret types (non-S3)
- [x] **Acceptance**: All existing functionality continues to work

### Task 6.3: Performance testing
- [x] **File**: `tests/test_engine.py`
- [x] **Test**: Verify build process timing hasn't significantly changed
- [x] **Acceptance**: Build performance remains acceptable (within 10% of original)

## Phase 7: Documentation and Cleanup

### Task 7.1: Update documentation
- [ ] **File**: `docs/guides/usage.md` or relevant configuration guide
- [ ] **Change**: Document the new build process order
- [ ] **Change**: Note automatic endpoint protocol handling
- [ ] **Acceptance**: Documentation reflects the new behavior

### Task 7.2: Update CHANGELOG.md
- [ ] **File**: `CHANGELOG.md`
- [ ] **Change**: Add entry for early secret creation and endpoint handling improvements
- [ ] **Acceptance**: Users can find information about the changes

### Task 7.3: Final validation
- [x] **Command**: Run full test suite
- [x] **Acceptance**: All tests pass with the new implementation
- [x] **Command**: Test with real S3 configurations
- [x] **Acceptance**: Real-world S3 attachments work reliably

## Success Criteria Summary

1. S3 secrets with protocol-prefixed endpoints work automatically
2. Secret creation happens before attachment setup in all scenarios
3. S3 attachments requiring configured secrets work reliably
4. All existing configurations continue to work unchanged
5. Error messages are clearer for secret configuration issues
6. Build process performance is not negatively impacted
7. Documentation is updated to reflect new behavior
8. Full test coverage is updated to ensure new behavior and backward compatibility