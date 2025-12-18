# Change: Early Secret Creation and Endpoint Protocol Handling

## Why

The current duckalog build process creates DuckDB secrets **after** setting up database attachments, which causes connection failures when attachments require the same credentials. Additionally, S3 endpoint URLs containing protocol prefixes (`http://`, `https://`) are passed directly to DuckDB, but DuckDB expects endpoints without protocols.

### Current Issues

1. **Timing Issue**: Secret creation happens in `_apply_duckdb_settings()` which is called **after** `_setup_attachments()`, but attachments can point to remote locations (e.g., `s3://bucket/external-db.duckdb`) that require the same S3 credentials configured in secrets.

2. **Endpoint Protocol Issue**: When users specify endpoints like `${env:LODL_ENDPOINT_URL}` with values such as `https://lodl.nes.siemens.de:8333`, the protocol prefix is passed directly to DuckDB, but DuckDB's S3 secret endpoint parameter expects only the hostname and port without the protocol.

3. **Connection Failure Pattern**: This results in errors like:
   ```
   IO Error: Could not establish connection error for HTTP GET to '//lodl.nes.siemens.de:8333/ewn/?encoding-type=url&list-type=2&prefix=tracedata%2Fstage1%2Fproducts%2F'
   ```

## What Changes

### Core Functionality

1. **Early Secret Creation**: Extract secret creation from `_apply_duckdb_settings()` and create secrets **before** `_setup_attachments()` in the build process.

2. **Endpoint Protocol Normalization**: Automatically strip `http://` and `https://` prefixes from S3 endpoint values before passing to DuckDB.

3. **Enhanced Build Process Order**:
   ```
   OLD: setup_connection → apply_pragmas → setup_attachments → create_secrets → create_views
   NEW: setup_connection → apply_pragmas → create_secrets → setup_attachments → create_views
   ```

### Implementation Details

- **Secret Creation Extraction**: Pull `_create_secrets()` call out of `_apply_duckdb_settings()` to enable independent execution timing
- **Endpoint Cleaning**: Add protocol stripping logic in `generate_secret_sql()` for S3 endpoints
- **Validation Enhancement**: Add validation to ensure secrets are properly configured before attachment setup
- **Backward Compatibility**: Maintain existing behavior for all other use cases

### User Experience

- **Automatic Protocol Handling**: Endpoints with protocols work seamlessly without manual cleanup
- **Earlier Failure Detection**: Secret-related failures occur before attachment setup with clearer error context
- **No Configuration Changes**: Existing configurations continue to work without modification

## Impact

### Affected Specs
- `specs/catalog-build/spec.md` - Update build process requirements for early secret creation
- `specs/config/spec.md` - Add endpoint protocol normalization requirements (if not already covered)

### Affected Code
- `src/duckalog/engine.py`:
  - `CatalogBuilder.build()` - Reorder execution steps
  - `_apply_duckdb_settings()` - Extract secret creation
  - `_create_secrets()` - Extract from pragma application
- `src/duckalog/sql_generation.py`:
  - `generate_secret_sql()` - Add endpoint protocol stripping for S3 secrets
- `src/duckalog/config/loader.py` - Potential enhancements to secret validation
- `tests/test_engine.py` - Update tests for new build order and endpoint handling

### Breaking Changes
- **NONE** - This change is purely additive and maintains full backward compatibility
- Existing configurations work unchanged
- Only the internal execution order changes, not the external API

### User Experience Impact
- Remote attachments (especially S3-based) will work reliably when matching secrets are configured
- Endpoints with protocols will be automatically handled without manual cleanup
- Better error messages when secret configuration issues occur
- Faster failure detection during the build process

## Risks and Trade-offs

### Complexity Risk: Build Process Changes
- **Impact**: Low - Changes are isolated to internal execution order
- **Mitigation**: Clear separation of concerns with well-defined method boundaries

### Performance Risk: Extra Validation
- **Impact**: Minimal - Secret validation happens once per build
- **Mitigation**: Validation is lightweight and prevents more expensive failures later

### Regression Risk: Secret Creation Timing
- **Impact**: Medium - Changes when secrets are created could affect existing workflows
- **Mitigation**: Extensive testing with various attachment scenarios to ensure compatibility

### Alternative Considered: Keep Current Order with Endpoint Fixes
- Could fix only the endpoint protocol issue while keeping current timing
- **Rejected**: The timing issue is the root cause of many potential connection failures, not just protocol handling

### Alternative Considered: Separate Secret Creation Method
- Could create a completely separate secret management system
- **Rejected**: Over-engineering for a simple timing and normalization issue

## Success Criteria

1. Secret creation happens before attachment setup in all build scenarios
2. S3 endpoints with `http://` and `https://` protocols work without manual intervention
3. S3 attachments that require the same credentials as configured secrets work reliably
4. All existing configurations continue to work without modification
5. Error messages are clearer when secret configuration issues occur
6. Build process timing changes don't affect performance significantly
7. Both main catalog and child catalog builds follow the same improved order
8. Documentation is updated to reflect the new build process and endpoint handling