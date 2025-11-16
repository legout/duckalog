# Change: Add DuckDB Secrets Manager Support

## Why
Users need to configure DuckDB secrets for accessing cloud storage services (S3, Azure, GCS, etc.) and databases through DuckDB's secrets manager. Currently, secrets must be created manually via SQL after catalog build, but they should be definable in the catalog configuration file for reproducible deployments.

## What Changes
- Add `secrets` field to `DuckDBConfig` to accept secret definitions
- Support temporary and persistent secrets with scoping
- Support all DuckDB secret types (s3, azure, gcs, http, postgres, mysql, etc.)
- Support different secret providers (CONFIG, credential_chain)
- **BREAKING**: None - this is additive functionality

## Impact
- Affected specs: config
- Affected code: src/duckalog/config.py, src/duckalog/engine.py