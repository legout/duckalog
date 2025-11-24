# Relative Path Resolution Design

## Architecture Overview

This design introduces path resolution capabilities to Duckalog's configuration processing pipeline, ensuring that relative paths in YAML configurations are automatically resolved to absolute paths before being passed to DuckDB.

## Current State Analysis

### Current Behavior
- Relative paths like `"data/users.parquet"` are passed directly to DuckDB
- DuckDB requires absolute paths for local file access
- Users must manually provide absolute paths or run from specific directories
- Inconsistent behavior across different execution contexts

### Problem Examples
```yaml
# Current problematic configuration
views:
  - name: users
    source: parquet
    uri: "data/users.parquet"  # Fails unless run from specific directory
  - name: events  
    source: parquet
    uri: "./data/events.parquet"  # Same issue
```

## Proposed Architecture

### Path Resolution Pipeline
```
Config File → Path Detection → Resolution → Validation → SQL Generation
```

### Components

#### 1. Path Detection Module (`src/duckalog/path_resolution.py`)
```python
def is_relative_path(path: str) -> bool:
    """Detect if a path is relative based on platform-specific rules"""
    
def is_absolute_path(path: str) -> bool:
    """Detect if a path is already absolute"""
    
def detect_path_type(path: str) -> PathType:
    """Categorize path as relative, absolute, or remote URI"""
```

#### 2. Resolution Module
```python
def resolve_relative_path(path: str, config_dir: Path) -> str:
    """Resolve relative path to absolute path"""
    
def validate_path_security(path: str, config_dir: Path) -> bool:
    """Validate path for security concerns"""
```

#### 3. Integration Points
- **Config Loading**: Add path resolution to `load_config()` function
- **SQL Generation**: Use resolved paths in `generate_view_sql()`
- **Validation**: Integrate path validation in Pydantic model validators

## Path Detection Logic

### Relative Path Definition
A path is considered relative if it:
- Does not start with a protocol (`http://`, `s3://`, etc.)
- Does not start with `/` on Unix systems
- Does not start with a drive letter on Windows (`C:`, `D:`, etc.)
- Does not start with `./` or `../` (these are explicitly relative)

### Algorithm
```python
import re
from pathlib import Path

def is_relative_path(path: str) -> bool:
    # Skip empty paths
    if not path or not path.strip():
        return False
        
    # Check for protocols (http, s3, gs, etc.)
    if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*://', path):
        return False
        
    # Platform-specific checks
    if Path(path).is_absolute():
        return False
        
    # Windows drive letter check (C:, D:, etc.)
    if re.match(r'^[a-zA-Z]:[\\\\/]', path):
        return False
        
    return True
```

## Security Considerations

### Directory Traversal Prevention
```python
def validate_path_security(path: str, config_dir: Path) -> bool:
    """Validate that resolved path stays within allowed boundaries"""
    try:
        resolved_path = resolve_relative_path(path, config_dir)
        config_dir = config_dir.resolve()
        
        # Check if resolved path tries to escape config directory
        resolved_path.resolve().relative_to(config_dir)
        return True
    except (ValueError, RuntimeError):
        # Path escapes config directory
        return False
```

### Security Rules
- Resolved paths must not escape the configuration file's directory or its subdirectories
- Symbolic links are validated to prevent link-based traversal
- Path components are checked for suspicious patterns (`..`, `~`, etc.)

## Cross-Platform Compatibility

### Path Handling Strategy
- Use `pathlib.Path` for cross-platform path operations
- Normalize path separators for SQL generation
- Handle Windows drive letters and UNC paths
- Preserve original path semantics while ensuring resolution

### Windows Specific Handling
```python
def is_windows_path_absolute(path: str) -> bool:
    """Check Windows-specific absolute path patterns"""
    # Drive letter: C:\path
    if re.match(r'^[a-zA-Z]:[\\\\/]', path):
        return True
    
    # UNC path: \\server\share
    if path.startswith('\\\\'):
        return True
        
    return False
```

## Integration Points

### Configuration Loading
```python
def load_config(
    config_path: str,
    resolve_paths: bool = True
) -> Config:
    """Load configuration with optional path resolution"""
    config_file = Path(config_path).resolve()
    config_dir = config_file.parent
    
    # Load YAML/JSON
    config_data = load_config_file(config_file)
    
    # Resolve paths if enabled
    if resolve_paths:
        config_data = resolve_config_paths(config_data, config_dir)
    
    return Config.model_validate(config_data)
```

### SQL Generation Updates
```python
def generate_view_sql(view: ViewConfig, config_dir: Path) -> str:
    """Generate SQL with resolved paths"""
    if view.source in {"parquet", "delta"} and view.uri:
        resolved_uri = resolve_relative_path(view.uri, config_dir)
        return f"SELECT * FROM {view.source}_scan('{resolved_uri}')"
    
    # ... existing logic for other sources
```

## Backward Compatibility

### Migration Strategy
1. **Opt-in Behavior**: Add `resolve_paths` parameter to `load_config()`
2. **Gradual Rollout**: Default to `False` initially, then switch to `True`
3. **Deprecation Path**: Provide clear migration warnings for users

### Configuration Examples
```yaml
# Old way (still supported)
views:
  - name: users
    source: parquet
    uri: "/absolute/path/to/data.parquet"

# New way (recommended)
views:
  - name: users  
    source: parquet
    uri: "data/users.parquet"  # Automatically resolved
```

## Error Handling

### Validation Errors
- **Invalid Path**: Clear error message with path context
- **Security Violation**: Detailed security violation explanation
- **Missing File**: Warning with resolution suggestions

### Runtime Errors
- **Permission Denied**: Graceful handling with actionable advice
- **Network Issues**: Timeout handling for remote URIs
- **Path Too Long**: Platform-specific error handling

## Performance Considerations

### Resolution Caching
- Cache resolved paths to avoid repeated filesystem operations
- Lazy resolution for views that might not be used
- Invalidate cache when configuration files change

### Filesystem Access
- Minimize filesystem calls during validation
- Use efficient path comparison algorithms
- Batch validate multiple paths when possible

## Testing Strategy

### Unit Tests
- Path detection algorithms for all platforms
- Security validation edge cases
- Cross-platform path handling
- Error condition handling

### Integration Tests
- Configuration loading with path resolution
- SQL generation with resolved paths
- End-to-end catalog building
- Windows/macOS/Linux compatibility

### Security Tests
- Directory traversal attempts
- Malicious path patterns
- Symbolic link attacks
- Permission boundary testing

## Documentation Requirements

### User Documentation
- Path resolution behavior explanation
- Configuration examples with relative paths
- Security considerations and best practices
- Migration guide from absolute paths

### Developer Documentation
- API documentation for path resolution functions
- Integration points and extension mechanisms
- Testing guidelines for path-related features
- Security validation requirements

## Future Extensions

### Potential Enhancements
- Environment variable support in paths (`${env:DATA_DIR}/file.parquet`)
- Pattern-based file resolution (`data/*.parquet`)
- Remote file caching and local mirroring
- Path resolution plugins for custom protocols

### Extension Points
- Custom path resolvers for specialized use cases
- Pluggable security validation rules
- Platform-specific optimizations
- Integration with external path management systems