# Change: Add remote config loading (e.g., s3://) via fsspec/obstore

## Why
Users want to point Duckalog at config files stored on remote filesystems (e.g., S3/HTTPS/GCS) without manually downloading them first. Currently `load_config` only reads local paths, causing friction for cloud-first workflows and automation.

## What Changes
- Add a remote-aware config loader that can fetch YAML/JSON from URIs like `s3://bucket/path/config.yaml` (and optionally https://, gcs://, abfs:///adl://, sftp://, github read-only) using fsspec/obstore with minimal deps.
- Keep existing schema validation unchanged; only the retrieval mechanism changes.
- Provide CLI/SDK entry to accept remote config URIs, with clear error handling and auth guidance.

## Impact
- Affected capability: config (loading behavior)
- Affected code: config loader / CLI entrypoints
- Dependencies: optional filesystem/http extras (e.g., fsspec with backend extras or obstore; requests for https) guarded behind extras; avoid hard dependency for local-only users.
