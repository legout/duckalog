# Design: Documentation Refactoring Following Diátaxis

## Context

The Diátaxis framework divides documentation into four distinct types, each serving a different user need:

1. **Tutorials** (learning-oriented): Learning by doing, getting started
2. **How-to Guides** (problem-oriented): Solving specific problems
3. **Reference** (information-oriented): Technical descriptions, complete coverage
4. **Explanation** (understanding-oriented): Clarification, background, context

Current documentation analysis shows:
- Strong: Architecture (Explanation), API Reference (Reference)
- Weak: Tutorials, How-to Guides
- Issues: Outdated UI docs, missing config imports guide, incomplete API reference
- Structure: Not clearly organized by documentation type

## Goals / Non-Goals

### Goals
1. Align documentation structure with Diátaxis framework
2. Fix all outdated and incorrect documentation
3. Add missing documentation for implemented features
4. Create clear progressive learning path for new users
5. Provide problem-oriented guides for common tasks
6. Maintain comprehensive reference documentation
7. Improve documentation discoverability and navigation

### Non-Goals
1. Code changes or feature additions (documentation only)
2. Complete rewrite of working documentation (incremental improvements)
3. Removing or deprecating existing documentation (preserve + enhance)
4. API documentation automation (manual improvements only for now)

## Decisions

### Decision 1: Diátaxis as Primary Organization Principle
**What**: Reorganize documentation using Diátaxis framework with clear sections for each type
**Why**: 
- Industry-proven framework for technical documentation
- Addresses current imbalance (strong in Reference/Explanation, weak in Tutorials/How-to)
- Improves user experience by matching docs to user intent
**Alternatives considered**:
- Keep current organization: Doesn't address identified gaps
- Feature-based organization: Doesn't serve different user needs effectively

### Decision 2: Incremental Rollout with High Priority First
**What**: Implement in phases: Critical fixes → Structure → Enhancements
**Why**:
- Delivers value immediately (fixes broken docs)
- Reduces risk of massive change
- Allows validation at each stage
**Alternatives considered**:
- Big bang rewrite: Too risky, harder to review
- Piecemeal without plan: Lacks coherent vision

### Decision 3: Preserve Existing URLs and Navigation During Transition
**What**: Keep existing doc files in place, add new structure alongside
**Why**:
- Prevents breaking external links
- Maintains user familiarity during transition
- Enables gradual migration
**Alternatives considered**:
- Move/rename everything: Breaks existing links, confusing to users
- Duplicate content: Creates maintenance burden

### Decision 4: Single Source of Truth for Config Imports
**What**: Move config imports documentation from scattered mentions to comprehensive guide in docs/guides/
**Why**:
- Feature is implemented but poorly documented
- Users need clear explanation of import resolution
- Diagnostic flags need documentation
**Implementation**: Expand existing docs/examples/config-imports.md

### Decision 5: Separate Tutorial vs How-to Content
**What**: Create distinct Tutorial and How-to sections in navigation
**Why**:
- Tutorials are for learning (comprehensive, step-by-step)
- How-tos are for solving problems (task-focused, direct)
- Different user intents require different approaches
**Example split**:
- Tutorial: "Getting Started with Duckalog" (comprehensive learning path)
- How-to: "How to debug catalog build failures" (specific problem solution)

### Decision 6: Update UI Docs to Match Current Implementation
**What**: Completely rewrite docs/guides/ui-dashboard.md based on current code and README
**Why**:
- Current doc mentions wrong framework (starhtml vs Datastar)
- Missing security features documentation
- Incomplete feature list
**Source of truth**: README.md section on UI + actual dashboard code

## Architecture Changes

### Current Documentation Structure
```
docs/
├── index.md (mixed content)
├── architecture.md (Explanation)
├── guides/
│   ├── usage.md (mixed: Reference + How-to)
│   ├── path-resolution.md (mixed: Explanation + How-to)
│   └── ui-dashboard.md (outdated)
├── reference/
│   └── api.md (Reference, incomplete)
├── examples/
│   └── *.md (unstructured)
```

### Proposed Documentation Structure
```
docs/
├── index.md (overview + navigation guide)
├── tutorials/
│   ├── index.md
│   ├── getting-started.md (NEW)
│   └── dashboard-basics.md (NEW)
├── how-to/
│   ├── index.md (NEW)
│   ├── environment-management.md (NEW)
│   ├── debugging-builds.md (NEW)
│   ├── migration.md (NEW)
│   └── performance-tuning.md (NEW)
├── reference/
│   ├── index.md
│   ├── api.md (UPDATED)
│   ├── cli.md (NEW)
│   └── config-schema.md (NEW)
├── explanation/
│   ├── architecture.md (existing)
│   ├── philosophy.md (NEW)
│   └── performance.md (NEW)
├── guides/ (TRANSITION: gradually move to appropriate sections)
│   ├── usage.md (REFACTOR: split to how-to + reference)
│   ├── path-resolution.md (KEEP: good explanation)
│   ├── ui-dashboard.md (REWRITE)
│   └── config-imports.md (EXPAND)
└── examples/
    ├── index.md (UPDATED with progression)
    └── *.md (ADD metadata: difficulty, prerequisites)
```

### Navigation Structure (mkdocs.yml)
```yaml
nav:
  - Home: index.md
  - Getting Started:
      - Overview: tutorials/index.md
      - Tutorial: tutorials/getting-started.md
      - Dashboard Tutorial: tutorials/dashboard-basics.md
  - How-to Guides:
      - Overview: how-to/index.md
      - Environment Management: how-to/environment-management.md
      - Debugging Builds: how-to/debugging-builds.md
      - Migration: how-to/migration.md
      - Performance Tuning: how-to/performance-tuning.md
  - Reference:
      - Overview: reference/index.md
      - Python API: reference/api.md
      - CLI Commands: reference/cli.md
      - Configuration Schema: reference/config-schema.md
  - Understanding:
      - Architecture: explanation/architecture.md
      - Philosophy: explanation/philosophy.md
      - Performance: explanation/performance.md
  - Examples:
      - Overview: examples/index.md
      - [existing examples with difficulty ratings]
  - Legacy Guides:
      - User Guide: guides/usage.md
      - Path Resolution: guides/path-resolution.md
      - UI Dashboard: guides/ui-dashboard.md
```

## Risks / Trade-offs

### Risk: Documentation Fragmentation
- **Risk**: Creating too many small docs could fragment information
- **Mitigation**: Strong cross-referencing, clear navigation, index pages for each section
- **Trade-off**: Accept some redundancy for clarity in each documentation type

### Risk: Maintenance Burden
- **Risk**: More documentation files = more maintenance
- **Mitigation**: Single source of truth for each topic, automated link checking
- **Trade-off**: Short-term effort for long-term maintainability

### Risk: User Confusion During Transition
- **Risk**: Users might not find moved content
- **Mitigation**: Keep old links working, add "moved to" notices, gradual transition
- **Trade-off**: Temporary duplication during transition period

### Risk: Incomplete Implementation
- **Risk**: Starting but not finishing creates worse state than before
- **Mitigation**: Phased approach with high-priority items first, each phase is self-contained
- **Trade-off**: May not achieve perfect Diátaxis alignment immediately

## Migration Plan

### Phase 1: Critical Fixes (Week 1)
- Update ui-dashboard.md
- Expand config-imports.md
- Add missing API reference items
- Create troubleshooting guide
- **Validation**: All updated docs build without warnings, fixes verified

### Phase 2: Structure (Week 2)
- Create tutorial directory and getting-started tutorial
- Create how-to directory and first 2-3 guides
- Update examples/index.md with progression
- **Validation**: New structure navigable, existing docs unaffected

### Phase 3: Reference Completion (Week 3)
- Create cli.md reference
- Create config-schema.md reference
- Update API reference with complete coverage
- **Validation**: Reference docs comprehensive, no missing items

### Phase 4: Polish and Enhancement (Week 4)
- Create explanation docs (philosophy, performance)
- Consolidate README/docs overlap
- Add remaining how-to guides
- Final navigation cleanup
- **Validation**: Full documentation review, Diátaxis balance achieved

### Rollback Strategy
- Each phase is additive (doesn't remove existing docs)
- Can revert navigation changes in mkdocs.yml
- Git history preserves all previous states
- Critical fixes can be cherry-picked independent of structure changes

## Open Questions

1. **Should we use redirects for moved content or keep dual locations temporarily?**
   - Recommendation: Keep dual locations with "This doc has moved" notice for 1 release cycle

2. **How much detail in CLI reference vs examples?**
   - Recommendation: CLI reference = complete option list; Examples = common use cases

3. **Should examples stay in docs/ or move to top-level examples/ with README-only?**
   - Recommendation: Keep in docs/ for MkDocs integration, cross-reference to code examples/

4. **API reference: Auto-generate from docstrings or manual curation?**
   - Recommendation: Manual for now (mkdocstrings setup later as separate change)

5. **Treatment of path-resolution.md and best-practices-path-management.md overlap?**
   - Recommendation: Keep path-resolution.md as explanation, merge best-practices into how-to guide
