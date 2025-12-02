# Tasks: Refactor Consolidate Config Layer

## Implementation Order

### Phase 1: Merge Path Resolution
- [ ] 1.1. Review path_resolution.py to identify public API surface
- [ ] 1.2. Copy path resolution functions to config.py (as private `_resolve_*`)
- [ ] 1.3. Update config.py exports to include path resolution
- [ ] 1.4. Update imports in modules that use path_resolution
- [ ] 1.5. Run tests to verify path handling still works
- [ ] 1.6. Remove path_resolution.py
- [ ] 1.7. Update documentation

### Phase 2: Merge SQL File Loader
- [ ] 2.1. Review sql_file_loader.py to identify public API surface
- [ ] 2.2. Integrate SQL file loading into load_config() pipeline
- [ ] 2.3. Convert TemplateProcessor class to pure functions
- [ ] 2.4. Remove SQLFileLoader class, convert to module-level functions
- [ ] 2.5. Update config.py exports
- [ ] 2.6. Update imports in modules that use sql_file_loader
- [ ] 2.7. Run tests to verify SQL file loading still works
- [ ] 2.8. Remove sql_file_loader.py
- [ ] 2.9. Update documentation

### Phase 3: Simplify Logging
- [ ] 3.1. Move simple redaction logic into config.py
- [ ] 3.2. Replace logging_utils usage with stdlib logging
- [ ] 3.3. Remove loguru dependency from requirements
- [ ] 3.4. Remove logging_utils.py
- [ ] 3.5. Update all logging calls to use stdlib logging
- [ ] 3.6. Run tests to verify logging still works correctly

### Phase 4: Final Integration
- [ ] 4.1. Run full test suite to ensure no regressions
- [ ] 4.2. Update imports across all modules
- [ ] 4.3. Verify no circular imports remain
- [ ] 4.4. Update type hints and docstrings
- [ ] 4.5. Run mypy type checking
- [ ] 4.6. Run ruff linting

### Phase 5: Documentation
- [ ] 5.1. Update module documentation in config.py
- [ ] 5.2. Update README.md if needed
- [ ] 5.3. Update migration guide if needed
- [ ] 5.4. Verify all public APIs still documented