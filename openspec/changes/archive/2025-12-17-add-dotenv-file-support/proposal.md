# Change: Add .env File Support for Configuration

## Why

The current duckalog configuration system supports environment variable interpolation using `${env:VAR_NAME}` syntax, but only reads from `os.environ`. This creates friction for developers who want to:

1. **Local Development**: Store project-specific credentials and configuration in `.env` files that aren't committed to version control
2. **Environment Management**: Separate development, staging, and production configurations without complex environment setup
3. **Security**: Keep sensitive credentials in local files rather than system-wide environment variables
4. **Team Collaboration**: Allow team members to have different local configurations without interfering with each other

Currently, users must manually set environment variables before running duckalog commands or rely on shell-specific mechanisms (`.bashrc`, `.zshrc`, etc.), which is cumbersome and error-prone.

## What Changes

### Core Functionality
- **Automatic .env Loading**: When loading configuration files, duckalog will automatically search for and load `.env` files from:
  - The root directory (where duckalog is run)
  - The directory containing the configuration file
  - Parent directories (up to the filesystem root)
- **Environment Variable Precedence**: Loaded .env variables are added to `os.environ` before configuration parsing, making them available to the existing `${env:VAR}` interpolation system
- **Backward Compatibility**: All existing environment variable usage continues to work unchanged

### Implementation Details
- **Smart Search**: Implement hierarchical .env file discovery starting from the config file directory and moving upward
- **File Format Support**: Support standard `.env` format with `KEY=value` pairs, including quoted values and comments
- **Security**: Ensure .env files are never logged and validate file permissions before loading
- **Error Handling**: Gracefully handle missing .env files and malformed entries without breaking configuration loading

### User Experience
- **Zero Configuration**: .env files work automatically without additional setup
- **Clear Feedback**: Informative messages when .env files are found and loaded
- **Debug Support**: Allow users to see which .env files were loaded via verbose logging

## Impact

### Affected Specs
- `specs/config/spec.md` - Add requirements for .env file loading and environment variable precedence

### Affected Code
- `src/duckalog/config/loader.py` - Add .env file discovery and loading logic
- `src/duckalog/config/interpolation.py` - Update environment variable resolution (if needed)
- `src/duckalog/cli.py` - Add .env file awareness to configuration loading
- `tests/test_config.py` - Add tests for .env file loading behavior
- `docs/guides/configuration.md` - Document .env file usage patterns

### Breaking Changes
- **NONE** - This change is purely additive and maintains full backward compatibility

### User Experience Impact
- Developers can use local `.env` files for credentials and configuration
- Reduced setup friction for new team members
- Better separation of concerns between system and project environment variables
- Enhanced security by keeping sensitive data in project-specific files

## Risks and Trade-offs

### Security Risk: Credential Exposure
- **Impact**: Low - .env files typically contain sensitive data that shouldn't be committed
- **Mitigation**: Ensure .gitignore patterns are documented and automatic; provide clear warnings about file contents

### Performance Risk: File System Operations
- **Impact**: Minimal - .env file searches are limited to a few directory levels
- **Mitigation**: Cache loaded .env files and implement reasonable search depth limits

### Complexity Risk: Debugging Environment Variables
- **Impact**: Medium - Users may be confused about variable precedence between .env and system environment
- **Mitigation**: Add verbose logging to show which .env files were loaded and from where variables originate

### Alternative Considered: Manual .env Loading
- Could require explicit .env file specification in each command
- **Rejected**: Less user-friendly and doesn't follow common Python conventions

### Alternative Considered: Package-Specific .env
- Could limit .env files to configuration file directory only
- **Rejected**: Doesn't support monorepo layouts where config is in subdirectories

## Success Criteria

1. .env files are automatically discovered and loaded when configuration files are processed
2. Environment variables from .env files are available to `${env:VAR}` interpolation
3. .env file loading works for both local and remote configuration files
4. Configuration loading fails gracefully if .env files are malformed
5. Verbose logging shows which .env files were found and loaded
6. All existing environment variable usage continues to work unchanged
7. Documentation includes .env file patterns and security best practices