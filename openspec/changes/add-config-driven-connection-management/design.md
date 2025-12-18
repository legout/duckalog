## Context
DuckDB settings (PRAGMAs) and database attachments are session-only and do not persist across database connections. The current duckalog architecture applies these configurations only during initial catalog building, which prevents the desired config-driven workflow where users can reconnect to existing catalogs with proper state restoration.

## Goals / Non-Goals
- Goals: Enable seamless reconnection to existing catalogs with automatic session state restoration
- Goals: Support both full rebuild and incremental update workflows  
- Goals: Maintain backward compatibility with existing build commands
- Non-Goals: Make secrets persistent by default (security-conscious design choice)
- Non-Goals: Completely eliminate rebuild capability (force rebuild remains available)
- Non-Goals: Real-time configuration monitoring (out of scope for this change)

## Decisions
- Decision: Introduce `CatalogConnection` class to manage session state restoration
- Decision: Use lazy connection pattern with automatic state restoration on first access
- Decision: Keep secrets temporary by default, add opt-in persistence flag
- Decision: Add new `run` CLI command as primary entry point, keep `build` for compatibility
- Decision: Implement incremental logic for views only (settings/attachments always reapplied)

Alternatives considered:
- Store settings in database metadata tables - Rejected: DuckDB doesn't support persistent settings storage
- Use connection pooling - Rejected: Overkill for current use case, adds complexity
- Auto-detect changes on every operation - Rejected: Performance impact, explicit rebuild is clearer

## Risks / Trade-offs
- Performance: Each new connection incurs setup overhead (200ms-2s depending on attachments)
- Memory: Persistent connections consume memory to avoid re-setup overhead
- Complexity: Connection management logic adds architectural complexity
- Compatibility: Potential breaking changes for existing workflows
- Risk: Connection state restoration could fail silently → Mitigation: Comprehensive logging and error handling

## Migration Plan
1. Introduce `CatalogConnection` alongside existing `build_catalog` function
2. Add `run` command to CLI and new function to Python API
3. Deprecate `build` command with clear migration guidance
4. Add deprecation warnings for direct `build_catalog` usage
5. Phase out `build` command in future major version

## Open Questions
- Connection caching strategy: Should we cache connections or recreate each time?
- Error handling: How to handle failed attachment setups on reconnection?
- Testing strategy: How to test session state restoration reliably across different DuckDB versions?