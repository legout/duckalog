## 1. Core Connection Management
- [ ] 1.1 Create `CatalogConnection` class in src/duckalog/connection.py
- [ ] 1.2 Implement session state restoration (_restore_session_state method)
- [ ] 1.3 Add settings reapplication on connection (DuckDB pragmas)
- [ ] 1.4 Add attachment re-setup on connection (ATTACH DATABASE statements)
- [ ] 1.5 Add lazy connection with automatic state restoration

## 2. Smart Catalog Updates
- [ ] 2.1 Implement existing views detection (query information_schema)
- [ ] 2.2 Add missing views identification logic
- [ ] 2.3 Implement incremental view creation (only create what's missing)
- [ ] 2.4 Add force rebuild flag support for full rebuild capability

## 3. Update Entry Points
- [ ] 3.1 Modify `build_catalog` in engine.py to use connection manager
- [ ] 3.2 Update CLI to add `run` command (duckalog run config.yaml)
- [ ] 3.3 Update Python API to use connection manager
- [ ] 3.4 Maintain backward compatibility for existing `build` command

## 4. Secrets Configuration
- [ ] 4.1 Add `persistent` option to SecretConfig (default: false)
- [ ] 4.2 Update secret creation to respect persistence setting
- [ ] 4.3 Add documentation for secrets persistence implications
- [ ] 4.4 Ensure secrets are recreated if temporary and missing

## 5. Testing and Documentation
- [ ] 5.1 Add unit tests for CatalogConnection class
- [ ] 5.2 Add integration tests for session state restoration
- [ ] 5.3 Update user documentation with new workflow
- [ ] 5.4 Add migration guide for existing users

## 6. Error Handling and Performance
- [ ] 6.1 Add connection error handling and retry logic
- [ ] 6.2 Implement connection timeouts for attachments
- [ ] 6.3 Add logging for session state restoration
- [ ] 6.4 Optimize reconnection for multiple attachments