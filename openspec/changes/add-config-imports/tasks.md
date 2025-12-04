# Implementation Tasks: Config Imports

## Phase 1: Core Implementation

### Task 1.1: Update Config Model
- [ ] Add `imports: list[str] = Field(default_factory=list)` field to `Config` model in `src/duckalog/config/models.py`
- [ ] Add validator to ensure `imports` is optional and defaults to empty list
- [ ] Update model documentation

### Task 1.2: Create Import Context Data Structure
- [ ] Create `ImportContext` dataclass in `src/duckalog/config/loader.py`
- [ ] Include fields: `visited_files`, `import_stack`, `config_cache`
- [ ] Add helper methods for path tracking and cycle detection

### Task 1.3: Implement Deep Merge Function
- [ ] Create `_deep_merge_dicts()` function in `src/duckalog/config/loader.py`
- [ ] Handle scalar values (last wins)
- [ ] Handle dictionary merging (recursive)
- [ ] Handle list concatenation
- [ ] Add unit tests for merge function

### Task 1.4: Implement Config Merging
- [ ] Create `_merge_configs()` function in `src/duckalog/config/loader.py`
- [ ] Convert Config objects to dictionaries, merge, then convert back
- [ ] Handle special cases for named lists (views, semantic_models, etc.)
- [ ] Add unit tests for config merging

### Task 1.5: Implement Import Loading
- [ ] Create `_load_config_with_imports()` function in `src/duckalog/config/loader.py`
- [ ] Modify `load_config()` to call new function
- [ ] Implement import path resolution
- [ ] Implement circular import detection
- [ ] Implement caching of loaded configs
- [ ] Add unit tests for import loading

### Task 1.6: Update Error Classes
- [ ] Add new error classes to `src/duckalog/errors.py`:
  - `ImportError` (base class)
  - `CircularImportError`
  - `ImportFileNotFoundError`
  - `ImportValidationError`
  - `DuplicateNameError`
- [ ] Ensure proper inheritance from `ConfigError`

### Task 1.7: Add Post-Merge Validation
- [ ] Create `_validate_merged_config()` function
- [ ] Validate unique view names across all imports
- [ ] Validate unique semantic model names
- [ ] Validate unique iceberg catalog names
- [ ] Validate unique attachment aliases
- [ ] Validate semantic model references
- [ ] Add unit tests for validation

## Phase 2: Integration and Testing

### Task 2.1: Update CLI Integration
- [ ] Ensure `duckalog build` works with imported configs
- [ ] Ensure `duckalog validate` works with imported configs
- [ ] Ensure `duckalog generate-sql` works with imported configs
- [ ] Test with various import scenarios

### Task 2.2: Add Environment Variable Support
- [ ] Update path resolution to support `${env:VAR}` in import paths
- [ ] Integrate with existing environment variable interpolation
- [ ] Add tests for environment variable interpolation in imports

### Task 2.3: Add Remote Import Support
- [ ] Extend import loading to support remote URIs
- [ ] Reuse existing remote config loading infrastructure
- [ ] Add tests for remote imports (S3, HTTP, etc.)

### Task 2.4: Create Comprehensive Test Suite
- [ ] Create `tests/test_config_imports.py` with unit tests
- [ ] Create `tests/test_config_imports_integration.py` with integration tests
- [ ] Create `tests/test_config_imports_security.py` with security tests
- [ ] Add test data files in `tests/data/imports/`

### Task 2.5: Performance Optimization
- [ ] Implement config caching
- [ ] Add import depth limit (e.g., 10 levels)
- [ ] Add total file limit (e.g., 100 files)
- [ ] Add performance tests

## Phase 3: Documentation and Examples

### Task 3.1: Update User Documentation
- [ ] Add "Modular Configuration" section to `docs/guides/usage.md`
- [ ] Document `imports` field syntax and examples
- [ ] Document merging behavior and conflict resolution
- [ ] Document error messages and troubleshooting

### Task 3.2: Create Examples
- [ ] Create `examples/05-config-organization/` directory
- [ ] Add basic imports example
- [ ] Add environment-specific example
- [ ] Add domain-based splitting example
- [ ] Add remote imports example

### Task 3.3: Update API Documentation
- [ ] Update `load_config()` documentation in `src/duckalog/config/__init__.py`
- [ ] Document import behavior in docstrings
- [ ] Update type hints if needed

### Task 3.4: Create Migration Guide
- [ ] Create guide for migrating from single-file to multi-file configs
- [ ] Add examples of common splitting patterns
- [ ] Document best practices for organization

## Phase 4: Advanced Features (Optional)

### Task 4.1: Selective Imports
- [ ] Support `imports: {views: "./views.yaml", settings: "./settings.yaml"}`
- [ ] Update merging logic for selective imports
- [ ] Add tests for selective imports

### Task 4.2: Import Overrides
- [ ] Support `override: false` flag for imports
- [ ] Allow main file to not override imported values
- [ ] Add tests for override behavior

### Task 4.3: CLI Tool for Import Analysis
- [ ] Add `duckalog show-imports` command
- [ ] Display import graph and dependencies
- [ ] Show merged configuration summary

### Task 4.4: Glob Pattern Support
- [ ] Support `imports: ["./config/*.yaml"]`
- [ ] Support exclude patterns `imports: ["./config/*.yaml", "!./config/secrets.yaml"]`
- [ ] Add tests for glob patterns

## Testing Tasks

### Unit Tests
- [ ] Test basic import loading
- [ ] Test merging strategies
- [ ] Test path resolution
- [ ] Test circular import detection
- [ ] Test duplicate name validation
- [ ] Test environment variable interpolation
- [ ] Test error handling

### Integration Tests
- [ ] Test CLI commands with imports
- [ ] Test Python API with imports
- [ ] Test with hierarchical attachments
- [ ] Test with remote configs
- [ ] Test with semantic models

### Security Tests
- [ ] Test path traversal prevention
- [ ] Test import depth limits
- [ ] Test file count limits
- [ ] Test remote import security
- [ ] Test environment variable security

### Performance Tests
- [ ] Test large import chains
- [ ] Test repeated imports
- [ ] Test caching effectiveness
- [ ] Test memory usage

## Code Review Checklist

### Before Implementation
- [ ] Review design with team
- [ ] Confirm merging strategy
- [ ] Confirm error handling approach
- [ ] Confirm backward compatibility

### During Implementation
- [ ] Follow existing code style
- [ ] Add comprehensive docstrings
- [ ] Add type hints
- [ ] Write tests alongside implementation

### After Implementation
- [ ] Run existing test suite
- [ ] Run new import tests
- [ ] Check for performance regressions
- [ ] Update documentation
- [ ] Create examples

## Dependencies

### Required Dependencies
- No new external dependencies
- Uses existing YAML/JSON parsing
- Uses existing remote config loading
- Uses existing environment variable interpolation

### Optional Dependencies
- For glob pattern support: `glob` module (standard library)
- For advanced path matching: `fnmatch` module (standard library)

## Risk Assessment

### High Risk Areas
1. **Circular import detection**: Must be robust to prevent infinite recursion
2. **Merging logic**: Complex, must handle all edge cases
3. **Error messages**: Must be clear and actionable
4. **Backward compatibility**: Must not break existing configs

### Mitigation Strategies
1. **Thorough testing**: Comprehensive test suite for edge cases
2. **Incremental rollout**: Start with basic features, add advanced features later
3. **User feedback**: Gather feedback from early adopters
4. **Fallback behavior**: Clear error messages with suggestions

## Success Criteria

### Functional Requirements
- [ ] Configs with imports load correctly
- [ ] Merging works as specified
- [ ] Circular imports are detected
- [ ] Duplicate names are detected
- [ ] Environment variables work in import paths
- [ ] Remote imports work
- [ ] All existing functionality continues to work

### Non-Functional Requirements
- [ ] Performance: No significant slowdown for configs without imports
- [ ] Memory: Reasonable memory usage for large import chains
- [ ] Security: No new security vulnerabilities
- [ ] Usability: Clear error messages and documentation

### Quality Requirements
- [ ] Code coverage: >90% for new code
- [ ] Documentation: Complete and accurate
- [ ] Examples: Comprehensive and working
- [ ] Backward compatibility: 100% maintained