## 1. Remote Import Resolution
- [x] 1.1 Allow `imports` entries to be recognized as remote when they use a supported URI scheme (e.g. `s3://`, `gcs://`, `abfs://`, `https://`).
- [x] 1.2 Integrate remote import resolution with the existing remote config helpers (e.g. `is_remote_uri`, `fetch_remote_content`, `load_config_from_uri`).

## 2. Loading and Merging Behavior
- [x] 2.1 Extend the import-loading path so remote imports are fetched and parsed before being merged with local configs.
- [x] 2.2 Ensure remote-imported configs participate in the same deep-merge and uniqueness validation logic as local imports.
- [x] 2.3 Confirm that circular import detection works correctly when a remote config imports a local config (and vice versa).

## 3. Security and Error Handling
- [x] 3.1 Reuse existing security rules and authentication guidance from remote config loading for import URIs.
- [x] 3.2 Ensure remote-import failures surface as clear configuration errors that include the URI, operation (fetch/parse/validate), and underlying cause.
- [x] 3.3 Add tests for common failure modes (missing object, invalid YAML/JSON, permission errors).

## 4. Tests and Documentation
- [x] 4.1 Add unit tests that simulate remote imports using fake or in-memory filesystems / HTTP responses.
- [x] 4.2 Add at least one integration-style test that demonstrates a catalog using both local and remote imports.
- [x] 4.3 Update user documentation to include a short section on remote imports, including examples and security notes.
