## 1. Scope & design
- [x] 1.1 Decide supported schemes via fsspec/obstore (s3://, gcs://, abfs://|adl://, sftp://, https://, github read-only) and optional deps strategy.
- [x] 1.2 Define auth resolution order per backend (AWS env/profile; GCP ADC; Azure env/managed identity; SFTP key/pass); explicit creds in URI are disallowed.

## 2. Implementation
- [x] 2.1 Add a fetcher utility (e.g., `load_config_from_uri`) that streams remote content via fsspec/obstore and passes it to existing validation.
- [x] 2.2 Wire CLI/SDK to accept remote URIs transparently.
- [x] 2.3 Add clear error messages for missing deps/creds or unsupported schemes.

## 3. Testing
- [x] 3.1 Unit tests with mocked S3/HTTP fetch.
- [x] 3.2 CLI-level test for remote URI path.

## 4. Docs
- [x] 4.1 Update README/usage to show remote config URIs and auth guidance.
