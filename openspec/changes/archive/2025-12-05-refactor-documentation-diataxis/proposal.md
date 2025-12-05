# Change: Refactor Documentation Following Diátaxis Framework

## Why

Current documentation analysis reveals several critical gaps and inconsistencies:

1. **Outdated UI documentation**: `docs/guides/ui-dashboard.md` incorrectly references "starhtml/starui" instead of Datastar and omits security features
2. **Missing feature documentation**: Config imports, connection API helpers, and SQL file templates lack comprehensive guides
3. **Poor Diátaxis alignment**: Strong in Explanation/Reference (7.5/10), weak in Tutorials/How-to Guides
4. **Incomplete API reference**: Connection helpers (connect_to_catalog_cm) and SQLFileLoader missing from reference docs
5. **Scattered examples**: Good content but no progressive learning path for beginners→intermediate→advanced

The refactoring will align documentation with the Diátaxis framework to provide balanced coverage across all four documentation types: Tutorials, How-to Guides, Reference, and Explanation.

## What Changes

### High Priority Updates
- **Update UI documentation** to reflect Datastar implementation, security features, and complete feature set
- **Add Config Imports guide** explaining import resolution, merge behavior, and diagnostics
- **Complete API Reference** with missing connection helpers and SQLFileLoader documentation
- **Create Troubleshooting Guide** as dedicated how-to for debugging common issues
- **Reorganize Examples** with clear beginner→intermediate→advanced progression

### Medium Priority Additions
- **Add How-to Guides**: environment management, migration patterns, performance optimization
- **Expand CLI Reference** with complete flag documentation, especially show-imports diagnostics
- **Create Configuration Schema Reference** as comprehensive YAML/JSON schema documentation

### Documentation Structure Improvements
- Create clear separation between Tutorials (learning) and How-to Guides (problem-solving)
- Add progressive learning path markers in examples
- Consolidate README/docs overlap to reduce duplication
- Cross-reference related documentation systematically

## Impact

### Affected Specs
- `docs` - Navigation updates, new examples structure
- `documentation` - Architecture doc cross-references, new guides
- `examples` - Reorganization with learning progression
- `dashboard-ui` - Complete rewrite of UI documentation

### Affected Files
- `docs/guides/ui-dashboard.md` - Complete rewrite
- `docs/guides/usage.md` - Expand with new how-to sections
- `docs/reference/api.md` - Add missing API documentation
- `docs/examples/index.md` - Add learning progression structure
- `docs/examples/config-imports.md` - Expand to comprehensive guide
- `mkdocs.yml` - Navigation restructure for Diátaxis alignment
- New files to create:
  - `docs/guides/troubleshooting.md`
  - `docs/guides/config-imports.md`
  - `docs/guides/migration.md`
  - `docs/reference/cli.md`
  - `docs/reference/config-schema.md`
  - `docs/tutorials/getting-started.md`
  - `docs/how-to/environment-management.md`
  - `docs/how-to/performance-optimization.md`

### Breaking Changes
None - This is documentation-only refactoring with no code changes.

### Migration Path
- Existing documentation remains accessible during transition
- Old links maintained via redirects or navigation
- Gradual rollout: high priority first, then medium priority
