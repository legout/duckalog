## Context
We need remote catalog outputs without bespoke client code for each backend. Using a filesystem abstraction like fsspec or obstore lets us handle S3, GCS, ADLS/ABFS, SFTP, and potentially read-only Github/HTTPS with one interface and optional extras. Local-only users must remain unaffected.

## Goals / Non-Goals
- Goals: write built `.duckdb` catalogs to remote URIs; support at least s3:// plus other common backends via fsspec/obstore; keep auth aligned with provider defaults; clear errors and optional deps.
- Non-Goals: change catalog contents; add persistent caches; manage credentials beyond provider-standard mechanisms; implement presigned URL flows for this change.

## Decisions
- Abstraction: prefer fsspec (with appropriate extras) and accept obstore as an alternative if already present; detect at runtime and fail with guidance if neither is installed.
- Supported schemes (initial): s3://, gcs://, abfs://|adl://, sftp://; github/https allowed only when writable or when backend supports PUT; otherwise fail read-only destinations.
- Auth: rely on backend-standard resolution (AWS env/profile/IAM; GCP ADC; AZURE env/managed identity; SFTP user/pass or key); never accept secrets embedded in URIs.
- Data path: build to a temp local file, then stream upload via filesystem to reduce memory; allow direct streaming only if backend supports efficient write.
- Error model: explicit messages for unsupported schemes, missing extras, and auth failures; keep local builds identical when remote is not requested.

## Open Questions
- Should we expose a `--fs-extra` flag to force a specific fsspec implementation when multiple are installed?
- Do we need multipart/resumable uploads for very large catalogs (>5GB), or is single-shot sufficient for now?
