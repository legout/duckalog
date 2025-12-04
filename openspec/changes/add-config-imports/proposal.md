# Proposal: Add Config Imports for Modular Configuration

## Problem Statement

Currently, Duckalog requires all catalog configuration to be in a single YAML/JSON file. While this works well for small configurations, it becomes unwieldy for larger projects where:
- Teams want to split configuration by domain (e.g., `views.yml`, `settings.yml`, `secrets.yml`)
- Different environments need different configurations
- Reusable configuration fragments need to be shared across projects
- Configuration files become too large to manage effectively

The existing hierarchical attachment system (`attachments.duckalog[]`) allows building separate catalogs and attaching them, but this requires building each child catalog separately and doesn't support merging configuration sections.

## Proposed Solution

Add an `imports` field to the top-level configuration that allows importing other configuration files and merging their contents. This provides a clean way to split configuration across multiple files while maintaining backward compatibility.

### Key Features (Core Scope)

1. **Explicit imports**: Users explicitly list local files to import.
2. **Flexible merging**: Deep-merge strategy with list concatenation so sections from multiple files combine into a single config.
3. **Path resolution**: Relative paths resolved relative to the importing file's directory.
4. **Environment variable support**: Use `${env:VAR}` in import paths for local files.
5. **Cycle detection**: Prevent infinite import loops through circular-import detection.
6. **Backward compatibility**: Single-file configs continue to work unchanged when `imports` is omitted or empty.

## Design

### 1. Import Syntax

```yaml
# main.yaml
imports:
  - ./settings.yaml
  - ./views/users.yaml
  - ./views/products.yaml
  - ./secrets/${env:ENVIRONMENT}.yaml

duckdb:
  database: catalog.duckdb
  # settings imported from settings.yaml
  # secrets imported from secrets/${env:ENVIRONMENT}.yaml

views:
  # views imported from users.yaml and products.yaml
  # local views can also be defined here
  - name: combined_view
    sql: SELECT * FROM users JOIN products ON user_id = product_owner_id
```

### 2. Merging Strategy

The default merging strategy is **deep merge with list concatenation**:

- **Scalar values**: Later imports override earlier ones (last-wins)
- **Objects/dicts**: Deep merge (recursive combination)
- **Lists**: Concatenate (all items from all imports)
- **Special handling for views**: Ensure unique view names across all imports

### 3. Import Resolution Order

1. Load main config file
2. Process imports in order they appear
3. For each import:
   - Resolve path relative to importing file
   - Load imported config (recursively processing its imports)
   - Merge into current config
4. Apply main config on top (overriding imports)

### 4. Conflict Resolution

- **Duplicate view names**: Error by default, with option to override
- **Duplicate semantic model names**: Error by default
- **Duplicate attachment aliases**: Error by default
- **Duplicate iceberg catalog names**: Error by default

### 5. Advanced Features (Future, Out of Scope for This Change)

The following capabilities are intentionally deferred to follow-up OpenSpec changes so that
`add-config-imports` can focus on a small, robust core:

- **Remote imports**: Importing configuration from URIs such as `s3://` or `https://`.
- **Selective imports**: Syntax like `imports: {views: "./views.yaml", settings: "./settings.yaml"}`.
- **Import overrides**: Per-import override flags such as `override: true/false`.
- **Glob patterns and excludes**: Patterns such as `imports: ["./views/*.yaml", "!./views/legacy.yaml"]`.

## Implementation Plan

### Phase 1: Basic Import Support
1. Add `imports` field to `Config` model (list of strings)
2. Implement import loading in `config/loader.py`
3. Add import resolution and merging logic
4. Add cycle detection
5. Update validation to handle merged configs
6. Add tests for basic import scenarios

### Phase 2: Advanced Features
1. Support remote imports (S3, HTTP, etc.)
2. Add environment variable interpolation in import paths
3. Implement conflict resolution options
4. Add selective imports syntax
5. Add glob pattern support

### Phase 3: Tooling and Documentation
1. Add CLI command to show import graph
2. Add validation for import cycles
3. Update documentation with examples
4. Add migration guide from single-file to multi-file

## Benefits

1. **Cleaner organization**: Split configs by domain/team/environment
2. **Reusability**: Share common config fragments across projects
3. **Environment-specific configs**: Easy to switch between dev/staging/prod
4. **Version control friendly**: Smaller files, clearer diffs
5. **Gradual adoption**: Start with single file, split as needed
6. **Consistent with industry patterns**: Similar to Docker Compose extends, Kubernetes kustomize, etc.

## Alternatives Considered

1. **YAML anchors/aliases**: Limited to single file, doesn't solve file splitting
2. **YAML merge keys (`<<`)**: Non-standard, limited merging capabilities
3. **Template engines (Jinja2)**: Adds complexity, different skill requirement
4. **Build-time concatenation**: Requires external tools, breaks tooling integration
5. **Current hierarchical attachments**: Requires building separate catalogs, can't merge config sections

## Compatibility

- **Backward compatible**: Existing single-file configs work unchanged
- **Forward compatible**: New `imports` field is optional
- **CLI compatibility**: All existing commands work with imported configs
- **API compatibility**: `load_config()` returns merged config transparently

## Examples

### Simple Split
```yaml
# catalog.yaml
imports:
  - ./settings.yaml
  - ./views.yaml

# No other sections needed - all content imported
```

### Environment-Specific
```yaml
# catalog.yaml
imports:
  - ./base.yaml
  - ./environments/${env:ENV}.yaml
```

### Domain-Based
```yaml
# catalog.yaml
imports:
  - ./infrastructure/settings.yaml
  - ./data-sources/parquet.yaml
  - ./data-sources/postgres.yaml
  - ./views/customer-views.yaml
  - ./views/product-views.yaml
  - ./semantic-models/business.yaml
```

## Open Questions

1. Should we support JSON imports alongside YAML?
2. Should imports be processed before or after environment variable interpolation?
3. How to handle import errors (file not found, parse error)?
4. Should we support conditional imports based on environment variables?

## Next Steps

1. Create detailed specification
2. Implement Phase 1 (basic imports)
3. Add comprehensive tests
4. Update documentation
5. Gather feedback from users
6. Implement Phase 2/3 features based on feedback
