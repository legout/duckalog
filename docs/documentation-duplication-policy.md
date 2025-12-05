# Documentation Duplication Policy

This document outlines the strategy for maintaining consistency between `README.md` and `docs/index.md` while avoiding content drift.

## Canonical Content Location

**Primary rule**: `docs/_snippets/intro-quickstart.md` is the **canonical source** for:
- Project introduction and overview
- Basic quickstart example  
- Core feature list
- Installation instructions

## Content Distribution Strategy

### README.md (GitHub Entry Point)
- **Audience**: GitHub visitors, quick evaluation, CI/CD systems
- **Content**: 
  - Project badges and metadata
  - **Imported** canonical intro + quickstart via `--8<--` snippet
  - Examples showcase
  - Full reference documentation (kept detailed for GitHub browsing)
  - Contributing guidelines

### docs/index.md (Documentation Site Entry Point)
- **Audience**: Users seeking comprehensive documentation
- **Content**:
  - **Imported** canonical intro + quickstart via `--8<--` snippet  
  - Extended quickstart with realistic multi-source example
  - Documentation navigation overview
  - Feature highlights with links to detailed sections
  - Next steps and learning paths

### docs/_snippets/intro-quickstart.md (Canonical Source)
- **Content**: Core introduction, minimal quickstart, features, installation
- **Maintenance**: Single source of truth for shared content
- **Updates**: Edit here to update both README and docs/index simultaneously

## Content Updating Rules

### When updating intro/quickstart content:
1. **Always** edit `docs/_snippets/intro-quickstart.md` first
2. Test both locations render correctly:
   - README.md renders properly on GitHub  
   - docs/index.md renders properly in MkDocs site
3. Never edit the same content in both places independently

### When updating README-only content:
- Badges and metadata in README.md header
- Examples showcase (specific to GitHub audience)
- Full reference documentation sections
- Contributing guidelines

### When updating docs/index-only content:
- Extended quickstart examples
- Documentation navigation structure
- Feature highlights that link to deeper sections
- Learning paths and next steps

## Technical Implementation

### Snippet Inclusion
Both files use MkDocs `pymdownx.snippets` syntax:
```markdown
--8<-- "docs/_snippets/intro-quickstart.md"
```

### Validation
- Run `mkdocs build` to verify docs site builds without warnings
- Check README.md renders properly on GitHub or local preview
- Ensure snippet paths are correct and content loads

## Benefits of This Approach

1. **No Content Drift**: Shared content stays synchronized automatically
2. **Single Source of Truth**: Edit once, update everywhere
3. **Audience-Appropriate**: Each location provides right level of detail
4. **Maintainable**: Clear rules reduce confusion about where to make changes
5. **Git-Friendly**: Changes are tracked in the canonical location

## Common Pitfalls to Avoid

- ❌ Editing the same content in both README and docs independently  
- ❌ Forgetting to test both locations after snippet updates
- ❌ Breaking snippet paths when reorganizing file structure
- ❌ Adding README-specific content to the canonical snippet

## Maintenance Checklist

When updating shared content:
- [ ] Edit `docs/_snippets/intro-quickstart.md`
- [ ] Verify README.md renders correctly
- [ ] Verify docs/index.md renders correctly  
- [ ] Run `mkdocs build` to ensure no warnings
- [ ] Check any internal links still work

This policy ensures consistency while allowing each location to serve its specific audience effectively.