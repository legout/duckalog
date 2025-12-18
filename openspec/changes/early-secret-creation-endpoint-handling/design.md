# Design Document: Early Secret Creation and Endpoint Protocol Handling

## Technical Analysis

### Current Problem
The duckalog build process has a timing issue where DuckDB secrets are created **after** database attachments are set up. This causes failures when attachments require the same credentials configured in secrets.

**Root Cause**: 
- `_apply_duckdb_settings()` calls `_create_secrets()` 
- `_setup_attachments()` is called after `_apply_duckdb_settings()`
- Attachments to remote locations (especially S3) need the same credentials as configured secrets

**Secondary Issue**: 
- S3 endpoint URLs with protocol prefixes (`http://`, `https://`) are passed directly to DuckDB
- DuckDB expects endpoints without protocol prefixes
- This results in malformed endpoint values and connection failures

## Design Decisions

### 1. Extraction Strategy
**Decision**: Extract `_create_secrets()` from `_apply_duckdb_settings()` rather than duplicating code.

**Rationale**:
- Maintains separation of concerns
- Allows independent execution timing
- Preserves existing method interfaces
- Easier to test and maintain

**Implementation**:
```python
# OLD: Mixed responsibilities
def _apply_duckdb_settings(conn, config, verbose):
    _create_secrets(conn, config, verbose)  # ❌ Mixed in
    # other setup...

# NEW: Separated concerns  
def _apply_duckdb_settings(conn, config, verbose):
    # Extensions, pragmas, settings only
    pass

def _create_secrets(conn, config, verbose):
    # Secret creation only
    pass
```

### 2. Execution Order Strategy
**Decision**: Create secrets **before** attachments in the main build flow.

**Rationale**:
- Secrets are foundational - other operations depend on them
- Earlier failure detection with clearer error context
- Aligns with dependency hierarchy (credentials → connections → operations)

**Implementation**:
```python
def CatalogBuilder.build(self):
    self._setup_connection()        # 1. Database connection
    self._apply_pragmas()           # 2. Basic setup (no secrets)
    self._create_secrets()          # 3. Create credentials FIRST
    self._setup_attachments()       # 4. Attachments can use secrets
    self._create_views()            # 5. Create views
```

### 3. Protocol Stripping Strategy
**Decision**: Automatically strip `http://` and `https://` prefixes from S3 endpoints.

**Rationale**:
- User-friendly: works with common URL formats
- DuckDB compatibility: expects clean endpoints
- Automatic: no manual intervention required
- Safe: only strips known protocol prefixes

**Implementation**:
```python
if secret.endpoint:
    clean_endpoint = secret.endpoint
    if clean_endpoint.startswith(('http://', 'https://')):
        clean_endpoint = clean_endpoint.split('://', 1)[1]
    params.append(f"ENDPOINT {quote_literal(clean_endpoint)}")
```

## Architecture Changes

### Engine Layer Changes
- **File**: `src/duckalog/engine.py`
- **Classes**: `CatalogBuilder`, `ConfigDependencyGraph`
- **Methods**: `build()`, `_apply_duckdb_settings()`, `_create_secrets()`
- **Impact**: Internal execution order only, no API changes

### SQL Generation Changes  
- **File**: `src/duckalog/sql_generation.py`
- **Function**: `generate_secret_sql()`
- **Change**: Add endpoint protocol stripping for S3 secrets
- **Impact**: Automatic protocol handling, no configuration changes needed

### Testing Strategy
- **Unit Tests**: Individual method behavior
- **Integration Tests**: Full build process scenarios  
- **Regression Tests**: Existing configurations continue to work
- **Edge Cases**: Missing environment variables, malformed endpoints

## Validation and Error Handling

### Enhanced Validation
- **Environment Variable Resolution**: Clear errors for unresolved `${env:VAR}` placeholders
- **Secret Configuration**: Validate required fields before DuckDB operations
- **Endpoint Format**: Warn when protocols are stripped (verbose mode)

### Error Message Improvements
- **Early Detection**: Fail fast when secret configuration is invalid
- **Clear Context**: Indicate which secret and field has issues
- **Actionable Guidance**: Suggest solutions for common problems

## Performance Considerations

### Minimal Performance Impact
- **Execution Order**: No additional operations, just reordering
- **Protocol Stripping**: Simple string operation, negligible overhead
- **Validation**: Lightweight checks that prevent expensive failures

### Caching and Optimization
- **Secret Reuse**: Created once per build, used by all attachments
- **Environment Loading**: Reuse existing .env file caching
- **Connection Pooling**: Leverage DuckDB's built-in connection management

## Security Implications

### No Security Regression
- **Credential Handling**: Same secure practices as before
- **Logging**: Continue to redact sensitive values in logs
- **Error Messages**: Avoid leaking credential details in errors

### Enhanced Security
- **Earlier Validation**: Catch misconfigurations before attempting connections
- **Clear Separation**: Secrets managed independently from other operations
- **Protocol Handling**: Reduces user error in endpoint configuration

## Backward Compatibility

### Full Compatibility Maintained
- **Configuration Schema**: No changes to YAML/JSON config structure
- **API Interface**: All public methods and classes unchanged
- **Existing Workflows**: Current usage patterns continue to work

### Gradual Migration
- **Zero Configuration Changes**: Users don't need to update configs
- **Automatic Benefits**: Protocol stripping works transparently
- **Opt-in Validation**: Enhanced validation provides better errors without breaking existing usage

## Testing Strategy

### Test Categories
1. **Protocol Stripping Tests**: Endpoints with/without protocols
2. **Build Order Tests**: Verify secrets created before attachments  
3. **S3 Integration Tests**: Real S3 attachment scenarios
4. **Backward Compatibility Tests**: Existing configurations work
5. **Error Handling Tests**: Clear messages for misconfigurations

### Test Data
- **S3 Endpoints**: With/without protocols, valid/invalid formats
- **Attachment Types**: S3 DuckDB files, local files, database attachments
- **Configuration Scenarios**: Simple secrets, complex multi-source setups

## Future Considerations

### Extensibility
- **Additional Protocols**: Framework for handling other protocol prefixes if needed
- **Secret Types**: Easy to extend protocol handling to other secret types
- **Validation Rules**: Pluggable validation system for different secret configurations

### Monitoring and Observability
- **Build Metrics**: Track secret creation timing and success rates
- **Error Analytics**: Monitor common configuration issues
- **Performance Monitoring**: Ensure build process efficiency

## Implementation Risks and Mitigation

### Low Risk Changes
- **Isolated Impact**: Changes contained to engine and SQL generation modules
- **Clear Boundaries**: Method extraction maintains clear interfaces
- **Comprehensive Testing**: Extensive test coverage prevents regressions

### Rollback Plan
- **Feature Flags**: Could implement temporary flags to revert to old behavior if needed
- **Incremental Deployment**: Changes can be deployed incrementally by component
- **Configuration Preservation**: No config schema changes means easy rollback

This design ensures the early secret creation and endpoint protocol handling improvements are implemented safely, maintain backward compatibility, and provide immediate benefits to users working with S3-based attachments and configurations.