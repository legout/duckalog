# Add Changelog-Based Version Updates - Design

## Architecture Overview

This change extends the existing automated version tagging system to include automated changelog generation. The design builds upon the existing workflow infrastructure and adds intelligent git history analysis to automatically generate meaningful changelog entries.

## System Components

### 1. Enhanced Version Detection Workflow
- **Extended Triggers**: Runs on `pyproject.toml` changes AND on merge to main branch
- **Git History Analysis**: Analyzes git diff and commit history since last version tag
- **Change Categorization**: Automatically categorizes changes (Added, Changed, Fixed, Deprecated, Security, Breaking)
- **Changelog Generation**: Creates structured changelog entries in Keep a Changelog (KCH) format

### 2. Changelog Generation Engine
- **Template System**: Uses configurable templates for different change types
- **Git Integration**: Links changelog entries to specific commits and tags
- **Format Validation**: Ensures compliance with Keep a Changelog standards
- **CHANGELOG.md Updates**: Automatically updates existing changelog with new entries

### 3. Integration Points
- **Version Tagging**: Changelog generation occurs after tag creation, before publishing
- **Existing Workflows**: Integrates with current `auto-tag-version.yml` and `publish.yml` workflows
- **Backward Compatibility**: Maintains all existing manual changelog processes

## Technical Implementation Details

### Enhanced Workflow Triggers
```yaml
on:
  push:
    branches: [main]
    paths: ['pyproject.toml']
  merge:
    branches: [main]
  workflow_dispatch:
    inputs:
      generate_changelog:
        description: "Generate changelog for version range"
        required: false
        type: boolean
      force_changelog:
        description: "Force changelog generation"
        required: false
        type: boolean
```

### Git History Analysis Strategy
```python
# Analyze git history since last tag
git fetch --tags
git log --oneline --since=v{last_tag} --pretty=format:"%h|%s"

# Parse commits for change detection
for commit in git_history:
    analyze commit message for change type
    extract affected files and scope
    categorize based on conventional commits or heuristics
```

### Changelog Template System
```python
# Template engine for different change types
CHANGELOG_TEMPLATES = {
    'added': "### Added\n- {description}\n",
    'changed': "### Changed\n- {description}\n", 
    'fixed': "### Fixed\n- {description}\n",
    'deprecated': "### Deprecated\n- {description}\n",
    'security': "### Security\n- {description}\n",
    'breaking': "### Breaking Changes\n- {description}\n"
}
```

### CHANGELOG.md Integration
```python
# Update existing changelog with new entries
with open('CHANGELOG.md', 'r') as f:
    existing_content = f.read()
    new_entries = generate_changelog_entries(git_history, version_range)
    updated_content = merge_changelog_entries(existing_content, new_entries)
    f.write(updated_content)
```

## Integration with Existing Systems

### With Version Tagging Workflow
- **Sequential Execution**: Changelog generation runs after tag creation
- **Shared State**: Passes version information and git analysis between workflows
- **Artifact Sharing**: Chelog entries available to publishing workflow for release notes

### With Documentation System
- **README Updates**: Document new automated changelog process
- **Examples**: Provide examples of changelog entries and git history analysis
- **Troubleshooting**: Guide for resolving common changelog generation issues

## Security Considerations

### Git Operations
- **Read Access**: Requires read access to entire repository history
- **No Secret Exposure**: Changelog generation doesn't expose sensitive information
- **Audit Trail**: All changelog operations logged and traceable

### Workflow Security
- **Minimal Permissions**: Only requests necessary permissions for git operations
- **Input Validation**: Validates all user inputs before processing
- **Error Handling**: Graceful failure with clear error messages

## Performance Considerations

### Git History Analysis
- **Efficient History Traversal**: Uses `git log --since` to limit analysis scope
- **Smart Caching**: Caches git analysis results between workflow runs
- **Parallel Processing**: Analyzes multiple commits concurrently when possible

### Changelog Generation
- **Template Caching**: Pre-compiles and caches changelog templates
- **Incremental Updates**: Only processes new commits since last analysis
- **Memory Efficient**: Streams changelog generation for large repositories

## Testing Strategy

### Unit Testing
- **Git Analysis**: Test commit message parsing and change categorization
- **Template Engine**: Test changelog template generation and formatting
- **Change Detection**: Validate version range analysis logic

### Integration Testing
- **End-to-End Workflow**: Test complete changelog generation process
- **Multi-Workflow**: Verify interaction between version tagging and changelog generation
- **Performance**: Test with repositories of various sizes and histories

## Future Extensibility

### Template Customization
- **Project-Specific Templates**: Support for project-specific changelog formats
- **Category Templates**: Custom templates for different types of changes
- **Multi-Language Support**: Extensible to support internationalization

### Advanced Analysis
- **Conventional Commit Detection**: Enhanced parsing of conventional commit formats
- **Impact Analysis**: Automatic assessment of change impact and scope
- **Dependency Analysis**: Detection of dependency changes and version implications

This design ensures that the changelog automation enhances rather than replaces the existing version tagging system, providing developers with comprehensive release documentation while maintaining all current functionality.