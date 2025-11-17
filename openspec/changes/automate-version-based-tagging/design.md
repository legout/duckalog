# Automate Version-Based Tagging and Publishing - Design

## Architecture Overview

This change introduces a new GitHub Actions workflow that monitors version changes in `pyproject.toml` and automatically creates Git tags to trigger the existing publishing workflow. The design follows the principle of minimal changes while maximizing automation.

## System Components

### 1. Version Detection Workflow
- **Trigger**: Runs on pushes to main branch when `pyproject.toml` is modified
- **Version Extraction**: Parses `pyproject.toml` to extract the current version
- **Change Detection**: Compares current version with the last tagged version
- **Validation**: Ensures version follows semantic versioning format

### 2. Automated Tagging System
- **Tag Creation**: Creates Git tag in format `v{version}` (e.g., `v0.1.0`)
- **Tag Pushing**: Pushes the tag to trigger the existing `publish.yml` workflow
- **Error Handling**: Provides rollback mechanisms if tagging fails

### 3. Integration with Existing Workflow
- **Workflow Trigger**: Leverages existing tag-based trigger in `publish.yml`
- **Backward Compatibility**: Maintains all existing manual triggers
- **No Duplication**: Reuses existing publishing logic and validation

## Technical Implementation Details

### Version Extraction Strategy
```yaml
- name: Extract version from pyproject.toml
  run: |
    VERSION=$(python -c "
    import tomllib
    with open('pyproject.toml', 'rb') as f:
        data = tomllib.load(f)
    print(data['project']['version'])
    ")
    echo "version=$VERSION" >> $GITHUB_OUTPUT
```

### Version Comparison Logic
- Fetch all existing tags from repository
- Compare current version with latest tag version
- Only proceed if current version > latest tagged version

### Error Handling and Safety
- Validate version format before tagging
- Check if tag already exists to prevent conflicts
- Provide clear error messages for debugging
- Include dry-run mode for testing

## Workflow Triggers

### Primary Trigger
```yaml
on:
  push:
    branches: [main]
    paths: ['pyproject.toml']
```

### Manual Override
```yaml
workflow_dispatch:
  inputs:
    force_tag:
      description: "Force tag creation even if version hasn't changed"
      required: false
      default: false
      type: boolean
```

## Integration Points

### With Existing publish.yml
- Uses existing tag-based trigger: `tags: ["v*.*.*"]`
- Maintains all existing jobs: test, build, publish, create-github-release
- Preserves all environment variables and secrets configuration

### With package-distribution Spec
- Extends existing automated publishing requirements
- Adds new requirement for version-based automation
- Maintains all security and validation requirements

## Security Considerations

### Permissions Required
- `contents: write` for creating and pushing tags
- `actions: read` for triggering other workflows

### Safety Measures
- Only runs on main branch to prevent accidental releases
- Validates version format before proceeding
- Checks for existing tags to prevent conflicts
- Provides manual override for special cases

## Rollback Strategy

### If Tagging Fails
- Workflow fails gracefully without affecting existing tags
- Clear error messages guide manual resolution
- No partial releases or inconsistent state

### If Version is Invalid
- Workflow stops before any tag creation
- Provides feedback on version format requirements
- Allows developer to fix `pyproject.toml` and retry

## Testing Strategy

### Unit Testing
- Test version extraction from various `pyproject.toml` formats
- Validate version comparison logic
- Test error handling scenarios

### Integration Testing
- Test end-to-end workflow with sample version changes
- Verify integration with existing `publish.yml`
- Test manual override functionality

### Dry Run Mode
- Include workflow_dispatch input for dry-run testing
- Allows testing without creating actual tags
- Validates all logic before production use

## Future Extensibility

### Potential Enhancements
- Support for pre-release versions (alpha, beta, rc)
- Integration with changelog generation
- Support for multiple release channels
- Automated version bumping based on conventional commits

### Extension Points
- Modular version extraction logic for different project structures
- Configurable tag formats
- Pluggable validation rules