# Change: Add Config Initialization Functionality

## Why
Users need an easy way to create basic Duckalog configuration files when getting started with the library. Currently, users must manually create YAML/JSON configuration files from scratch, which can be error-prone and time-consuming, especially for new users who aren't familiar with the configuration schema.

## What Changes
- **Python API**: Add `create_config_template()` function that generates a basic, valid Duckalog configuration
- **CLI Command**: Add `duckalog init` command with options for format (YAML/JSON), output path, and template customization
- **Template Content**: Generate a minimal but functional config with sensible defaults and example content
- **Format Support**: Support both YAML and JSON output formats
- **File Management**: Allow users to specify output path and handle file overwrite scenarios

## Impact
- **Affected specs**: config-init (new capability), cli (enhanced capability)
- **Affected code**: New Python module for config initialization, CLI command integration
- **User Experience**: Significantly improved onboarding experience for new users
- **Breaking Changes**: None - this is purely additive functionality