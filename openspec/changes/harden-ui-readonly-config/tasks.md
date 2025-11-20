## 1. Implementation
- [x] Enforce read-only SQL for `/api/query` and `/api/export` (reject DDL/DML/multi-statement; safe identifier quoting/parameterization)
- [x] Wire view-based SQL construction to use escaped identifiers and optional LIMIT without corrupting statements
- [x] Preserve on-disk config format (YAML/JSON) when writing; reload config into memory after successful saves
- [x] Offload DuckDB/catalog rebuild/export/query work to background threads to keep the event loop responsive
- [x] Replace fallback dashboard with a single Datastar path that exercises the Python SDK for streaming updates/banners
- [x] Tighten CORS defaults to localhost/same-origin and disable credentials by default (with opt-in escape hatch)

## 2. Testing
- [ ] Add tests for read-only enforcement and rejection of multi-statement/DDL SQL
- [ ] Add tests that config writes keep YAML formatting and refresh in-memory config
- [ ] Add concurrency/timeout-focused tests for background execution pathways
- [ ] Update dashboard tests to assert Datastar path is served (no fallback)
- [ ] Add tests for default CORS policy and opt-in overrides

## 3. Documentation
- [ ] Document read-only query/export constraints and error messaging
- [ ] Document config write semantics (format preservation, reload) and CORS defaults
- [ ] Note Datastar runtime requirements and removal of legacy fallback
