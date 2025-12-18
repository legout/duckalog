## Context
The current configuration architecture has evolved organically and now contains several anti-patterns that make the system difficult to maintain and extend. The `loader.py` module (1670 lines) handles multiple responsibilities, creating tight coupling and making testing challenging.

## Goals / Non-Goals
- Goals: Break down complexity, eliminate circular imports, improve maintainability
- Goals: Establish clean architectural boundaries with dependency injection
- Goals: Maintain 100% API compatibility during transition
- Non-Goals: Change configuration schema or user-facing behavior
- Non-Goals: Add new features (focus on refactoring existing functionality)

## Decisions

### Decision: Split loader.py into focused modules
**What**: Break `loader.py` into specialized modules following single responsibility principle
**Why**: Current 1670-line module handles too many concerns making it unmaintainable
**Alternatives considered**:
- Keep monolithic structure (rejected: too complex)
- Split into 2 modules (rejected: not granular enough)
- Split into 4 modules (chosen: good balance of focus vs. complexity)

### Decision: Use dependency injection for filesystem abstraction
**What**: Pass filesystem objects as parameters instead of importing directly
**Why**: Enables better testing, reduces coupling, supports custom authentication
**Implementation**: Update function signatures to accept optional filesystem parameters

### Decision: Request-scoped caching strategy
**What**: Implement caching within load operation context, not global
**Why**: Avoid memory leaks, ensure thread safety, improve performance
**Implementation**: Context manager pattern for caching during single load operation

## Risks / Trade-offs
- **Risk**: Breaking existing code through import changes → Mitigation: Comprehensive deprecation strategy
- **Risk**: Circular dependency introduction during refactoring → Mitigation: Careful dependency analysis
- **Risk**: Performance regression → Mitigation: Performance testing and optimization
- **Trade-off**: Short-term complexity for long-term maintainability

## Migration Plan
1. **Phase 1**: Create new module structure alongside existing code
2. **Phase 2**: Migrate functionality incrementally with backward compatibility
3. **Phase 3**: Remove deprecated code in major version release
4. **Rollback**: Git branches for each phase, feature flags for new implementation

## Open Questions
- How to handle testing of the new architecture without breaking existing test patterns?
- Should we introduce async variants of config loading functions?
- What's the best strategy for deprecation warnings to guide users?
