# Design: Config Imports Implementation

## Overview
This document outlines the technical design for implementing **core config imports** in Duckalog,
allowing configuration files to import and merge content from other local files. Advanced
capabilities such as remote imports, selective imports, glob patterns, and dedicated CLI tooling
are intentionally deferred to follow-up changes so that this change can focus on a small, robust
core.

## Architecture

### 1. Configuration Loading Flow

```
load_config(path)
    ├── Detect if path is remote URI
    ├── Load main config file
    ├── If imports field exists:
    │   ├── For each import path:
    │   │   ├── Resolve path relative to current file
    │   │   ├── Check for circular imports
    │   │   ├── Recursively load imported config
    │   │   └── Merge into current config
    │   └── Validate merged config
    └── Return Config object
```

### 2. Data Structures

#### Config Model Update
```python
class Config(BaseModel):
    version: int
    duckdb: DuckDBConfig
    views: list[ViewConfig] = Field(default_factory=list)
    attachments: AttachmentsConfig = Field(default_factory=AttachmentsConfig)
    iceberg_catalogs: list[IcebergCatalogConfig] = Field(default_factory=list)
    semantic_models: list[SemanticModelConfig] = Field(default_factory=list)
    imports: list[str] = Field(default_factory=list)  # New field
    
    @model_validator(mode="after")
    def validate_imports(self) -> "Config":
        # Validate no circular imports
        # Validate unique names across imports
        return self
```

#### Import Context
```python
@dataclass
class ImportContext:
    """Tracks import state during loading."""
    visited_files: set[str]  # Set of resolved file paths
    import_stack: list[str]  # Current import chain for error messages
    config_cache: dict[str, Config]  # Cache of loaded configs
```

### 3. Merging Algorithm

#### Deep Merge Function
```python
def deep_merge_config(base: dict, override: dict) -> dict:
    """Deep merge two configuration dictionaries."""
    result = base.copy()
    
    for key, override_value in override.items():
        if key not in result:
            result[key] = override_value
        else:
            base_value = result[key]
            
            if isinstance(base_value, dict) and isinstance(override_value, dict):
                # Recursively merge dictionaries
                result[key] = deep_merge_config(base_value, override_value)
            elif isinstance(base_value, list) and isinstance(override_value, list):
                # Concatenate lists
                result[key] = base_value + override_value
            else:
                # Override scalar values
                result[key] = override_value
    
    return result
```

#### Special Handling for Named Lists
Certain lists contain named objects that must remain unique:
- `views`: Unique by `(schema, name)` tuple
- `semantic_models`: Unique by `name`
- `iceberg_catalogs`: Unique by `name`
- `attachments.duckdb`: Unique by `alias`
- `attachments.sqlite`: Unique by `alias`
- `attachments.postgres`: Unique by `alias`
- `attachments.duckalog`: Unique by `alias`

After merging, we need to validate uniqueness across all imported configs.

### 4. Path Resolution

#### Import Path Resolution
```python
def resolve_import_path(import_path: str, base_path: str) -> str:
    """Resolve an import path relative to the importing file."""
    if is_remote_uri(import_path):
        return import_path  # Remote URIs are absolute
    
    # Handle environment variable interpolation
    if "${env:" in import_path:
        import_path = interpolate_env_vars(import_path)
    
    # Resolve relative to base file
    if os.path.isabs(import_path):
        return import_path
    else:
        base_dir = os.path.dirname(base_path)
        return os.path.normpath(os.path.join(base_dir, import_path))
```

### 5. Circular Import Detection

#### Algorithm
1. Maintain a set of visited file paths
2. Maintain a stack of current import chain
3. Before loading a file, check if it's already in the visited set
4. If found in current chain, raise circular import error
5. If found but not in current chain, use cached config

#### Error Message Example
```
Circular import detected:
  main.yaml
  └── settings.yaml
      └── common.yaml
          └── settings.yaml (circular reference)
```

### 6. Error Handling

#### Import-Specific Errors
- `ImportError`: Base class for import-related errors
- `CircularImportError`: Circular import detected
- `ImportFileNotFoundError`: Imported file not found
- `ImportValidationError`: Imported file validation failed
- `DuplicateNameError`: Duplicate name across imports

#### Error Context
All import errors should include:
- File path where error occurred
- Import chain (for nested imports)
- Specific error details

### 7. Caching Strategy

#### Config Cache
```python
config_cache: dict[str, Config] = {}
```

Benefits:
- Avoid reloading the same file multiple times
- Essential for handling repeated imports
- Improves performance for complex import graphs

### 8. Validation After Merging

#### Post-Merge Validation
After all imports are merged, we need to validate:
1. Unique names across all merged content
2. Cross-references are valid (e.g., semantic models referencing views)
3. No conflicting configurations

#### Validation Functions
```python
def validate_merged_config(config: Config, import_context: ImportContext) -> None:
    """Validate configuration after all imports are merged."""
    validate_unique_view_names(config.views)
    validate_unique_semantic_model_names(config.semantic_models)
    validate_unique_iceberg_catalog_names(config.iceberg_catalogs)
    validate_unique_attachment_aliases(config.attachments)
    validate_semantic_model_references(config)
    # ... other validations
```

### 9. API Changes

#### Public API
No changes to public API. `load_config()` will transparently handle imports.

#### Internal API
New internal functions:
- `_load_config_with_imports()`: Main entry point with import support
- `_resolve_and_load_import()`: Load a single import
- `_merge_configs()`: Merge two config objects
- `_validate_imports()`: Validate import-specific constraints

### 10. Testing Strategy

#### Unit Tests
1. **Basic Import Tests**
   - Single import
   - Multiple imports
   - Nested imports
   - Empty imports list

2. **Merging Tests**
   - Scalar value overriding
   - Dictionary merging
   - List concatenation
   - Named list uniqueness validation

3. **Path Resolution Tests**
   - Relative paths
   - Absolute paths
   - Environment variable interpolation
   - Remote URIs

4. **Error Handling Tests**
   - Circular imports
   - Missing files
   - Invalid YAML in imports
   - Duplicate names
   - Security violations

#### Integration Tests
1. **CLI Integration**
   - `duckalog build` with imports
   - `duckalog validate` with imports
   - `duckalog generate-sql` with imports

2. **Python API Integration**
   - `load_config()` with imports
   - Import chain with environment variables
   - Remote imports

3. **Performance Tests**
   - Large import chains
   - Repeated imports
   - Caching effectiveness

#### Security Tests
1. **Path Security**
   - Path traversal attempts
   - Symlink resolution
   - Permission checks

2. **Remote Import Security**
   - Authentication handling
   - TLS verification
   - Timeout handling

### 11. Implementation Phases

#### Phase 1: Basic Import Support
1. Add `imports` field to `Config` model
2. Implement basic import loading in `loader.py`
3. Add simple merging (last-wins for scalars, list concatenation)
4. Add circular import detection
5. Basic unit tests

#### Phase 2: Advanced Features
1. Environment variable interpolation in import paths
2. Remote import support
3. Improved error messages with import chain
4. Caching for performance
5. Integration tests

#### Phase 3: Validation and Polish
1. Post-merge validation
2. CLI command to show import graph
3. Documentation updates
4. Performance optimizations
5. Security hardening

### 12. Performance Considerations

#### Optimizations
1. **Config Caching**: Cache loaded configs to avoid redundant parsing
2. **Lazy Validation**: Defer validation until after all imports are merged
3. **Early Exit**: Detect circular imports early
4. **Memory Management**: Clear cache after loading complete

#### Memory Usage
- Config cache stores parsed Config objects
- Import context tracks visited files and current chain
- Consider config size limits for very large import graphs

### 13. Security Considerations

#### Path Security
- Import paths must respect same security boundaries as other paths
- Use `validate_path_security()` for local file imports
- Remote imports use existing remote security checks

#### Resource Limits
- Maximum import depth (e.g., 10 levels)
- Maximum total imported files (e.g., 100 files)
- Timeout for remote imports

#### Sandboxing
- Consider sandboxing imported config evaluation
- Limit environment variable access in import paths
- Validate imported configs before merging

### 14. Backward Compatibility

#### No Breaking Changes
- `imports` field is optional
- Existing configs work unchanged
- All existing APIs continue to work
- No changes to Config model except adding optional field

#### Migration Path
Users can gradually adopt imports by:
1. Starting with single-file config
2. Splitting into multiple files
3. Adding `imports` field to main file
4. Testing merged configuration

### 15. Future Extensions

#### Selective Imports
```yaml
imports:
  views: ./views.yaml
  settings: ./settings.yaml
```

#### Import Overrides
```yaml
imports:
  - file: ./base.yaml
    override: false  # Don't allow main file to override
```

#### Glob Patterns
```yaml
imports:
  - ./config/*.yaml
  - !./config/secrets.yaml  # Exclude secrets
```

#### Conditional Imports
```yaml
imports:
  - if: ${env:ENVIRONMENT} == "production"
    file: ./prod.yaml
  - else:
    file: ./dev.yaml
```

## Implementation Details

### File: `src/duckalog/config/loader.py`

#### New Functions
```python
def _load_config_with_imports(
    file_path: str,
    content: str,
    format: str,
    filesystem: Optional[Any] = None,
    resolve_paths: bool = True,
    load_sql_files: bool = True,
    import_context: Optional[ImportContext] = None,
) -> Config:
    """Load config with import support."""
    
def _resolve_and_load_import(
    import_path: str,
    base_path: str,
    filesystem: Optional[Any],
    resolve_paths: bool,
    load_sql_files: bool,
    import_context: ImportContext,
) -> Config:
    """Resolve and load an imported config file."""
    
def _merge_configs(base: Config, override: Config) -> Config:
    """Merge two Config objects."""
    
def _validate_imports(config: Config, import_context: ImportContext) -> None:
    """Validate configuration after imports are merged."""
```

### File: `src/duckalog/config/models.py`

#### Model Updates
```python
class Config(BaseModel):
    # ... existing fields ...
    imports: list[str] = Field(default_factory=list)
    
    @model_validator(mode="after")
    def validate_no_circular_imports(self) -> "Config":
        # Circular import validation happens during loading, not here
        return self
```

### File: `src/duckalog/config/__init__.py`

#### Public API
```python
# No changes to public API
# load_config() will internally use _load_config_with_imports()
```

### File: `src/duckalog/errors.py`

#### New Error Classes
```python
class ImportError(ConfigError):
    """Base class for import-related errors."""

class CircularImportError(ImportError):
    """Circular import detected."""

class ImportFileNotFoundError(ImportError):
    """Imported file not found."""

class ImportValidationError(ImportError):
    """Imported file validation failed."""

class DuplicateNameError(ImportError):
    """Duplicate name across imported configs."""
```

## Testing Plan

### Test Files
1. `tests/test_config_imports.py`: Unit tests for import functionality
2. `tests/test_config_imports_integration.py`: Integration tests
3. `tests/test_config_imports_security.py`: Security tests

### Test Data
Create test directory structure:
```
tests/data/imports/
├── simple/
│   ├── main.yaml
│   ├── settings.yaml
│   └── views.yaml
├── nested/
│   ├── main.yaml
│   ├── a.yaml
│   ├── b.yaml
│   └── c.yaml
├── circular/
│   ├── a.yaml
│   └── b.yaml
└── remote/
    ├── main.yaml
    └── remote-settings.yaml
```

## Documentation Updates

### User Guide
1. Add "Modular Configuration" section to docs
2. Examples of splitting configs
3. Best practices for organization
4. Migration guide from single-file

### API Documentation
1. Update `load_config()` documentation
2. Document `imports` field
3. Error handling guide

### Examples
Create example directory:
```
examples/05-config-organization/
├── 01-basic-imports/
│   ├── catalog.yaml
│   ├── settings.yaml
│   └── views/
│       ├── users.yaml
│       └── products.yaml
├── 02-environment-specific/
│   ├── catalog.yaml
│   ├── base.yaml
│   ├── dev.yaml
│   └── prod.yaml
└── 03-remote-imports/
    ├── catalog.yaml
    └── README.md
```

## Rollout Plan

### Phase 1: Implementation
1. Implement basic import support
2. Add unit tests
3. Internal code review

### Phase 2: Testing
1. Integration tests
2. Security review
3. Performance testing

### Phase 3: Documentation
1. Update user guide
2. Create examples
3. Update API documentation

### Phase 4: Release
1. Merge to main
2. Update changelog
3. Announce feature
