# Implementation Tasks: Config Imports (Core)

## 1. Config Model and Loader

- [ ] 1.1 Add `imports: list[str] = Field(default_factory=list)` to the `Config` model and ensure it is optional and defaults to an empty list.
- [ ] 1.2 Implement core import loading in the config loader:
  - Resolve relative import paths against the importing file.
  - Perform `${env:VAR}` interpolation in import paths for local files.
  - Detect and fail on circular imports.
  - Merge imported configs into the main config using the deep-merge strategy.

## 2. Merging and Validation

- [ ] 2.1 Implement a deep-merge helper that:
  - Recursively merges dictionaries.
  - Concatenates lists.
  - Applies last-wins semantics for scalar values.
- [ ] 2.2 Add post-merge validation for uniqueness:
  - Validate unique view identifiers across all imports.
  - Validate unique semantic model names, attachment aliases, and iceberg catalog names.
- [ ] 2.3 Ensure existing semantic-model references (e.g. `base_view`) still validate correctly after merging.

## 3. Security and Error Handling

- [ ] 3.1 Reuse existing path-security helpers so import paths obey the same allowed-root and traversal rules as other paths.
- [ ] 3.2 Define or reuse appropriate error types (likely `ConfigError`) and ensure import failures produce clear messages including the file path and import chain.

## 4. CLI / API Integration and Tests

- [ ] 4.1 Confirm `load_config()` returns the merged `Config` transparently when imports are present.
- [ ] 4.2 Verify core CLI commands (`duckalog build`, `duckalog validate`, `duckalog generate-sql` if present) work against configs that use imports.
- [ ] 4.3 Add unit tests for:
  - Basic imports and merge behavior.
  - Circular import detection.
  - Duplicate-name validation across imported files.
  - Environment variable interpolation in local import paths.
- [ ] 4.4 Add at least one integration test that uses a small set of imported configs to build a catalog end-to-end.

## 5. Documentation (Core)

- [ ] 5.1 Add a short “Config imports” section to the docs describing:
  - The `imports` field syntax.
  - Merge semantics and uniqueness rules.
  - How imports interact with `load_config()` and CLI commands.
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
