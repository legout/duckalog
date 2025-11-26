# Refactor UI to StarHTML Framework

## Why
- The current dashboard implementation uses 1,700+ lines of manual HTML string generation with f-strings, making it error-prone and difficult to maintain
- Manual Datastar attribute embedding in strings provides no type safety or IDE support, leading to runtime errors and poor developer experience
- Adding StarHTML provides Pythonic DSL, type safety, and better maintainability while preserving all existing functionality
- Incremental migration minimizes risk while dramatically improving code quality and developer experience

## What Changes
- Add StarHTML as an optional UI dependency (preferred when available) and keep legacy dependencies for fallback only.
- Build a new StarHTML-first UI app (routing + components) that reuses existing domain services (config load, query/exports, catalog build) instead of layering on Starlette/HTPy.
- Implement feature parity (views list, query interface, schema inspection, semantic models, data export) with StarHTML components and Datastar signals; no UX change required.
- Add explicit framework selection order: CLI flag (if added) > `DUCKALOG_UI_FRAMEWORK` env > auto-detect (use StarHTML if installed, otherwise legacy).
- Keep the legacy UI as a selectable fallback during migration; plan deprecation/removal once parity is validated.
- Update dependencies to drop HTMX/HTPy/datastar_py when legacy mode is retired (future cleanup milestone).

## Impact
- **Affected specs**: web-ui (enhanced implementation, same functionality)
- **Affected code**: UI app/routing/rendering, CLI selection logic, `pyproject.toml` (dependencies/extras)
- **Breaking changes**: None during migration; legacy kept as fallback until deprecation milestone.
- **Developer experience**: Significantly improved with type safety, IDE support, and maintainable Python code.
- **Testing**: Existing backend/domain tests remain; new StarHTML component tests added. Legacy UI tests remain until removal.
