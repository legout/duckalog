# Change: Save built DuckDB catalogs to remote filesystems (e.g., s3://) via fsspec/obstore

## Why
Users who run `build_catalog` in cloud/CI environments want the resulting `.duckdb` file to be written directly to remote storage (e.g., S3) without staging locally and manually uploading. This reduces steps, lowers egress, and aligns with remote config loading.

## What Changes
- Add an option to build_catalog/CLI to write the output DuckDB file to remote URIs using fsspec/obstore so we can support multiple backends (start with `s3://`, include `gcs://`, `abfs://`/`adl://`, `sftp://`, and read-only github/https where feasible).
- Use a streaming/upload approach with clear auth/dependency handling; avoid breaking local-only users.
- Keep catalog contents/schema unchanged—only the destination changes.

## Impact
- Affected capability: catalog-build (output handling)
- Affected code: build_catalog and CLI flags; optional remote upload helper using fsspec/obstore
- Dependencies: optional filesystem extras (e.g., `fsspec[s3,gcs,adlfs,sftp]` or `obstore`); graceful errors when missing
