# Implementation Tasks

## Tasks for Secrets Creation

### SQL Generation
- [x] Add `generate_secret_sql()` function to `src/duckalog/sql_generation.py`
  - Support `CREATE [PERSISTENT] SECRET name (TYPE type, [key_id = 'value'], ...)` syntax
  - Handle all secret types: s3, azure, gcs, http, postgres, mysql
  - Support SCOPE parameter when provided
  - Handle credential_chain provider variations
  - Add proper credential redaction in debug output

### Engine Integration
- [x] Modify `_create_secrets()` in `src/duckalog/engine.py` to execute secrets
  - Replace logging-only implementation with `conn.execute()` calls
  - Call `generate_secret_sql()` for each secret
  - Handle execution errors with clear error messages
  - Log successful secret creation

### Dry-Run Support
- [x] Update `generate_all_views_sql()` or equivalent to include secrets SQL
  - Add secrets generation for dry-run mode
  - Ensure CREATE SECRET statements appear in dry-run output

### Testing
- [x] Add integration test in `tests/test_engine_cli.py`
  - Test that secrets are actually created in DuckDB
  - Query `duckdb_secrets()` to verify presence
  - Test S3 secret access (if credentials available)
  - Test HTTP secret access (if test server available)
- [x] Add unit test in `tests/test_sql_generation.py` (new file)
  - Test `generate_secret_sql()` output for each secret type
  - Verify proper handling of persistence flag
  - Verify scope parameter generation
- [x] Add unit test in `tests/test_sql_generation.py` (new file)
  - Test `generate_secret_sql()` output for each secret type
  - Verify proper handling of persistence flag
  - Verify scope parameter generation
- [x] Add unit test in `tests/test_sql_generation.py` (new file)
  - Test `generate_secret_sql()` output for each secret type
  - Verify proper handling of persistence flag
  - Verify scope parameter generation
- [x] Add unit test in `tests/test_sql_generation.py` (new file)
  - Test `generate_secret_sql()` output for each secret type
  - Verify proper handling of persistence flag
  - Verify scope parameter generation
- [x] Add unit test in `tests/test_sql_generation.py` (new file)
  - Test `generate_secret_sql()` output for each secret type
  - Verify proper handling of persistence flag
  - Verify scope parameter generation
- [x] Add unit test in `tests/test_sql_generation.py` (new file)
  - Test `generate_secret_sql()` output for each secret type
  - Verify proper handling of persistence flag
  - Verify scope parameter generation
- [x] Add unit test in `tests/test_sql_generation.py` (new file)
  - Test `generate_secret_sql()` output for each secret type
  - Verify proper handling of persistence flag
  - Verify scope parameter generation
- [x] Add unit test in `tests/test_sql_generation.py` (new file)
  - Test `generate_secret_sql()` output for each secret type
  - Verify proper handling of persistence flag
  - Verify scope parameter generation
- [x] Add unit test in `tests/test_sql_generation.py` (new file)
  - Test `generate_secret_sql()` output for each secret type
  - Verify proper handling of persistence flag
  - Verify scope parameter generation
- [x] Add unit test in `tests/test_sql_generation.py` (new file)
  - Test `generate_secret_sql()` output for each secret type
  - Verify proper handling of persistence flag
  - Verify scope parameter generation

### Documentation
- [x] Update `docs/examples/duckdb-secrets.md`
  - Add note that secrets are now actually created in DuckDB
  - Add debugging tips for verifying secrets
  - Update any references to "future" functionality

- [x] Update CHANGELOG.md
  - Document that secrets are now functional

### Validation
- [x] Run `openspec validate implement-secrets-creation --strict`
  - Ensure all scenarios are covered
  - Verify no conflicts with existing specs
