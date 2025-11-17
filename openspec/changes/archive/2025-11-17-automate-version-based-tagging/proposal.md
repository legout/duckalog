# Automate Version-Based Tagging and Publishing

## Why

The current publishing workflow requires manual tag creation to trigger releases, which can lead to inconsistencies between the version in `pyproject.toml` and the actual Git tag. Developers may forget to update the version in `pyproject.toml` before tagging, or create tags that don't match the package version, causing confusion and potential release failures.

Automating this process will:
- Ensure version consistency between `pyproject.toml` and Git tags
- Reduce manual steps in the release process
- Prevent version mismatches that can cause publishing failures
- Streamline the release workflow by detecting version changes automatically
- Maintain the existing publish.yml workflow capabilities while adding automation

## What Changes

- Add a new GitHub Actions workflow that monitors changes to `pyproject.toml`
- When the version field in `pyproject.toml` changes, automatically:
  - Extract the new version from the file
  - Create and push a corresponding Git tag (e.g., `v0.1.0`)
  - Trigger the existing `publish.yml` workflow
- Maintain backward compatibility with existing manual tagging and workflow_dispatch triggers
- Add validation to ensure version follows semantic versioning
- Include proper error handling and rollback capabilities if tagging fails

## Impact

- **Improved Developer Experience**: Developers only need to update `pyproject.toml` to trigger a release
- **Reduced Errors**: Automatic version synchronization prevents tag/version mismatches
- **Streamlined Process**: Eliminates manual tag creation step in the release workflow
- **Maintained Flexibility**: Existing manual triggers still work for special cases
- **Version Consistency**: Ensures published package version always matches Git tag
- **Automation**: Reduces human intervention in the release process while maintaining control

The change builds on the existing `publish.yml` workflow infrastructure and integrates with the current `package-distribution` requirements, enhancing the automated publishing capabilities without breaking existing functionality.