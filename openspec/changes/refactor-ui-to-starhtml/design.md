## Context

The current duckalog UI implementation uses manual HTML string generation with Datastar attributes embedded in f-strings. This creates maintainability issues, provides no type safety, and makes UI development error-prone. The existing implementation has 1,700+ lines of HTML string generation in a single method (`_generate_datastar_dashboard()`), making it difficult to modify and extend.

## Goals / Non-Goals

### Goals
- Improve code maintainability and developer experience with type-safe UI components
- Provide incremental migration path without breaking existing functionality
- Enable better IDE support with autocomplete and refactoring capabilities
- Reduce runtime errors through compile-time type checking
- Maintain all existing functionality and user workflows while enabling a clear deprecation path for the legacy UI once parity is reached

### Non-Goals
- Change UI appearance or user experience (preserve exact same interface)
- Modify backend API endpoints or authentication
- Change underlying data processing logic
- Add new UI features beyond framework migration
- Remove support for legacy HTML string implementation immediately (but plan a deprecation milestone once parity is achieved)

## Decisions

### Decision: Use StarHTML as the primary UI Framework
**Rationale**: StarHTML provides Pythonic DSL + Datastar integration, replacing the Starlette/HTPy HTML-string path with type-safe components. Legacy UI remains available until parity and planned deprecation.

**Alternatives considered**:
- Continue with manual HTML strings (poor maintainability)
- Switch to traditional SPA framework (heavyweight, loses Python-first approach)
- Use FastHTML directly (less mature ecosystem than StarHTML)
- Use htpy exclusively (limited reactive capabilities)

### Decision: Incremental Migration Strategy
**Rationale**: Preserve existing functionality and minimize risk by allowing both implementations to coexist, with explicit selection order (CLI flag > env var > auto-detect). Plan deprecation/removal of legacy after parity.

**Alternatives considered**:
- Complete rewrite (high risk, potential feature loss)
- Big-bang migration (disruptive to existing users)
- Phased feature removal (user confusion)

### Decision: Environment/CLI-controlled Framework Selection
**Rationale**: Administrators control migration timing via CLI flag or `DUCKALOG_UI_FRAMEWORK`; auto-detect prefers StarHTML when available, otherwise legacy.

**Alternatives considered**:
- Automatic detection only (no control for edge cases)
- Compile-time configuration only (inflexible deployment)
- Feature flags in config files (more complex configuration surface)

## Risks / Trade-offs

### Risk: StarHTML Learning Curve
**Impact**: Developers need to learn StarHTML DSL patterns and conventions
**Mitigation**: Provide parallel implementation period and documentation; patterns are straightforward Python functions

### Risk: Performance Characteristics
**Impact**: StarHTML component rendering may have different performance characteristics than HTML strings
**Mitigation**: Benchmark implementation and optimize hot paths; StarHTML should have minimal overhead

### Risk: Dependency Management
**Impact**: Adding StarHTML while keeping legacy deps raises complexity
**Mitigation**: Clear optional extras; selection order; plan to drop HTMX/HTPy/datastar_py when legacy is removed in a future major

### Trade-off: Code Complexity vs Maintainability
**Consideration**: Migration introduces temporary complexity with both implementations
**Resolution**: Short-term complexity justified by long-term maintainability gains; clear deprecation path

## Migration Plan

### Phase 1: Foundation
- Add StarHTML optional extra; keep legacy extras separate
- Implement framework selection order (CLI flag > env var > auto-detect)
- Graceful imports when either stack is missing; ensure tests pass

### Phase 2: Parallel Implementation
- Build StarHTML dashboard module (routes + components) reusing domain services
- Implement parity for views/query/schema/semantic/export
- Add component-level tests

### Phase 3: Integration
- Wire UI server/CLI to choose framework at startup
- Keep API endpoints stable for both modes
- Validate workflows in both modes

### Phase 4: Testing & Validation
- Comprehensive tests and benchmarks for StarHTML
- UAT and docs for usage + selection

### Phase 5: Cleanup / Deprecation
- Announce deprecation timeline for legacy UI
- Drop HTMX/HTPy/datastar_py deps when legacy is removed in a future major release

## Open Questions

- Should we provide a migration tool for custom UI modifications?
- What is the timeline for legacy implementation deprecation?
- Should we add performance monitoring for dashboard rendering?
- Do we need additional documentation for StarHTML component patterns?
