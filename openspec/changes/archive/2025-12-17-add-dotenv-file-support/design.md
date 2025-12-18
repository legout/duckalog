# Design: .env File Support Implementation

## Architecture Overview

The .env file support will be implemented as an enhancement to the existing configuration loading system, specifically within `src/duckalog/config/loader.py`. The design follows the principle of minimal invasiveness while providing maximum utility.

## Core Components

### 1. .env File Discovery Engine
**Location**: `src/duckalog/config/loader.py` (new functions)

```python
def _find_dotenv_files(config_path: str) -> list[str]:
    """Discover .env files in the directory hierarchy."""
    
def _load_dotenv_file(file_path: str) -> dict[str, str]:
    """Load and parse a single .env file."""
    
def _merge_dotenv_variables(dotenv_vars: dict[str, str]) -> None:
    """Merge .env variables into os.environ with proper precedence."""
```

**Design Decisions**:
- Search starts from config file directory and moves upward
- Maximum search depth of 10 directories to prevent infinite loops
- Uses `python-dotenv` library for robust parsing
- Maintains order precedence: later files override earlier ones

### 2. Integration Point
**Location**: `_load_config_with_imports()` function

The .env loading will be integrated early in the configuration loading process, before environment variable interpolation occurs:

```python
def _load_config_with_imports(...):
    # Load .env files first
    _load_dotenv_files_for_config(file_path)
    
    # Continue with existing logic
    raw_text = _load_config_content(...)
    parsed = yaml.safe_load(raw_text)
    
    # Now ${env:VAR} interpolation will include .env variables
    interpolated = _interpolate_env(parsed)
```

### 3. Security Layer
**Location**: New security functions in `src/duckalog/config/security.py`

```python
def _validate_dotenv_file_security(file_path: str) -> bool:
    """Check file permissions and content for security issues."""
    
def _sanitize_dotenv_content(content: str) -> str:
    """Remove potentially dangerous content from .env files."""
```

## File Search Algorithm

### Search Strategy
1. **Starting Point**: Directory containing the configuration file
2. **Search Path**: Each parent directory up to filesystem root
3. **Depth Limit**: Maximum 10 directory levels to prevent issues
4. **File Priority**: `.env` files closer to the config file take precedence

### Search Example
For config file `/project/subdir/config.yaml`:
```
/project/subdir/.env     (checked first - highest priority)
/project/.env            (checked second)
/.env                    (checked last - lowest priority)
```

## Environment Variable Precedence

### Precedence Order (highest to lowest)
1. **System Environment**: Variables already in `os.environ`
2. **Loaded .env Files**: Variables from .env files (later files override earlier)
3. **Default Values**: `${env:VAR:default}` syntax still works

### Precedence Example
```bash
# System environment
export DATABASE_URL="system_db"

# .env file contains:
DATABASE_URL="file_db"
API_KEY="secret123"

# Result:
DATABASE_URL="file_db"     # .env overrides system
API_KEY="secret123"        # .env provides new variable
OTHER_VAR="default"        # Can still use ${env:OTHER_VAR:default}
```

## Error Handling Strategy

### Graceful Degradation
- Missing .env files: Log debug message, continue normally
- Malformed .env files: Log warning, skip that file, continue
- Permission errors: Log debug message, continue with other files
- Encoding issues: Log warning, attempt UTF-8 fallback

### User Feedback
```python
# Verbose logging output
DEBUG: Loading .env file: /project/.env
DEBUG: Loaded 5 variables from .env file
DEBUG: Skipping malformed .env file: /parent/.env (line 10: invalid syntax)
```

## Security Considerations

### File Permission Checks
- Check that .env files are not world-readable
- Warn if file permissions are too permissive (0o644 or more open)
- Skip files with suspicious permissions

### Content Validation
- Validate key names follow environment variable conventions
- Reject keys that could interfere with system operation
- Log warnings for suspicious content patterns

### No Logging of Sensitive Data
- Never log .env file contents
- Never log variable values from .env files
- Only log file paths and variable count for debugging

## Testing Strategy

### Unit Tests
- `.env` file discovery algorithm
- File parsing with various formats
- Environment variable precedence
- Security validation functions

### Integration Tests
- End-to-end configuration loading with .env files
- Interaction with existing import system
- Remote configuration file scenarios
- Error handling edge cases

### Test Data
```python
# Test .env files
test_envs = [
    # Basic key-value
    "KEY=value\n",
    
    # Quoted values
    'DB_URL="postgresql://localhost/db"\n',
    
    # Comments
    "# Comment\nKEY=value\n",
    
    # Empty values
    "EMPTY_KEY=\n",
]
```

## Performance Considerations

### Caching Strategy
- Cache loaded .env files by directory path
- Invalidate cache when file modification time changes
- Share cache across multiple configuration loads

### Search Optimization
- Limit directory depth to prevent excessive filesystem access
- Cache directory existence checks
- Use `os.path.realpath()` to resolve symbolic links

### Lazy Loading
- Only load .env files when configuration parsing begins
- Skip .env loading for dry-run operations (if implemented)

## Backward Compatibility

### Zero Breaking Changes
- All existing `${env:VAR}` usage continues to work
- System environment variables maintain same precedence
- Configuration file formats unchanged
- CLI interface unchanged

### Enhancement Only
- New functionality is purely additive
- Users can ignore .env files entirely
- No new required configuration options
- No changes to existing error messages

## Implementation Phases

### Phase 1: Core Functionality
- Basic .env file discovery and loading
- Integration with existing configuration system
- Minimal error handling

### Phase 2: Enhanced Features
- Comprehensive error handling
- Security validation
- Verbose logging
- Performance optimization

### Phase 3: Polish
- Documentation updates
- Developer experience improvements
- Advanced use cases

This design ensures that .env file support integrates seamlessly with existing functionality while providing a robust, secure, and user-friendly experience.