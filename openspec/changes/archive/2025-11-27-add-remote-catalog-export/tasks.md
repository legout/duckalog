## 1. Scope
- [x] 1.1 Define supported remote targets via fsspec/obstore (s3://, gcs://, abfs://|adl://, sftp://; github/https read-only); document minimum set for this change.
- [x] 1.2 Decide optional deps strategy (e.g., `fsspec[s3,gcs,adlfs,sftp]` or `obstore` extra) and how to pass auth (env/profile/config; reject secrets in URI).

## 2. Implementation
- [x] 2.1 Add a remote-aware sink to `build_catalog` using fsspec/obstore (upload of a local temp file or direct stream) when output path is remote.
- [x] 2.2 Expose CLI flag/parameter to accept remote output URIs.
- [x] 2.3 Emit clear errors for missing deps/creds/unsupported schemes.

## 3. Testing
- [x] 3.1 Unit/integration tests with mocked S3 uploads.
- [x] 3.2 CLI-level test for remote output path.

## 4. Docs
- [x] 4.1 Update README/usage to show remote output examples and auth guidance.
