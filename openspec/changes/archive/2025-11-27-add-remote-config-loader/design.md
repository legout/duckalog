## Context
Remote configs should be fetchable from common object/file stores without per-backend code. fsspec (or obstore) provides a uniform interface for S3, GCS, ADLS/ABFS, SFTP, and can fall back to HTTPS/Github read-only. We must keep local users unaffected.

## Goals / Non-Goals
- Goals: load YAML/JSON configs from remote URIs; support multiple schemes via one abstraction; keep validation unchanged; optional deps only.
- Non-Goals: caching/downloading for offline use; embedding credentials in URIs; managing auth lifecycles beyond provider defaults.

## Decisions
- Abstraction: prefer fsspec; allow obstore if present. Require explicit extras for cloud backends (e.g., `fsspec[s3]`, `fsspec[gcs]`, `adlfs`, `fsspec[sftp]`).
- Supported schemes (initial): s3://, gcs://, abfs://|adl://, sftp://, https://; github read-only via raw/https if allowed.
- Auth: follow backend defaults (AWS env/profile/IAM; GCP ADC; Azure env/managed identity; SFTP user/pass or key); reject secrets in URI.
- Fetch path: stream read into memory or temp buffer, then pass to existing validation; keep size/timeouts sensible (config files are small).
- Errors: clear messages for unsupported schemes, missing extras, and auth failures; preserve local path behavior unchanged.

## Open Questions
- Should we add a CLI flag to force a specific fsspec implementation when multiple are available?
- Do we need a small cache to avoid refetching the same config within a run?
