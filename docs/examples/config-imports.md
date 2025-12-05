# Config Imports

The config imports feature allows you to split your Duckalog configuration across multiple files, making it easier to organize, maintain, and reuse configuration components.

## Why Use Config Imports?

Config imports are useful when you want to:

- **Split configuration by domain** - Separate views, settings, and secrets into different files
- **Share common configuration** - Reuse the same settings across multiple projects
- **Organize by team or module** - Different teams can own their own config files
- **Environment-specific configs** - Easily switch between dev/staging/prod configurations
- **Version control friendly** - Smaller files result in clearer diffs

## Basic Usage

### Simple Split

Create a main catalog file that imports other config files:

```yaml
# catalog.yaml
version: 1
imports:
  - ./settings.yaml
  - ./views.yaml

duckdb:
  database: main.duckdb
```

```yaml
# settings.yaml
version: 1
duckdb:
  database: imported.duckdb
  install_extensions:
    - httpfs
  pragmas:
    - "SET threads = 4"

views:
  - name: imported_view
    sql: "SELECT 1"
```

```yaml
# views.yaml
version: 1
views:
  - name: another_view
    sql: "SELECT 2"
```

When you load `catalog.yaml`, Duckalog will:
1. Load the main config
2. Import `settings.yaml` and `views.yaml`
3. Merge them together (views are concatenated, scalar values are overridden)
4. Return a single, merged configuration

## Merge Behavior

Config imports use a **deep merge** strategy:

### Scalar Values
Later imports override earlier ones:

```yaml
# file1.yaml
version: 1
duckdb:
  database: file1.duckdb
  threads: 2
```

```yaml
# file2.yaml
version: 1
duckdb:
  threads: 4  # This overrides the value from file1
```

**Result:**
```yaml
duckdb:
  database: file1.duckdb  # From file1
  threads: 4              # From file2 (overrides file1)
```

### Dictionaries
Dictionaries are merged recursively:

```yaml
# base.yaml
duckdb:
  database: base.duckdb
  install_extensions:
    - httpfs
```

```yaml
# override.yaml
duckdb:
  extensions:
    - json  # Adds to extensions, doesn't replace
```

**Result:**
```yaml
duckdb:
  database: base.duckdb
  install_extensions:
    - httpfs
  extensions:
    - json
```

### Lists
Lists are concatenated (items from all imports are included):

```yaml
# file1.yaml
views:
  - name: view1
    sql: "SELECT 1"
```

```yaml
# file2.yaml
views:
  - name: view2
    sql: "SELECT 2"
```

**Result:**
```yaml
views:
  - name: view1  # From file1
  - name: view2  # From file2
```

## Environment Variables

You can use environment variables in import paths:

```yaml
# catalog.yaml
version: 1
imports:
  - ${env:CONFIG_DIR}/settings.yaml  # Uses CONFIG_DIR environment variable

duckdb:
  database: main.duckdb
```

Set the environment variable:
```bash
export CONFIG_DIR=/path/to/configs
```

## Import Order and Precedence

Imports are processed in the order they appear, and **later imports override earlier ones**. The main config file always has the final say:

```yaml
# catalog.yaml
imports:
  - ./base.yaml
  - ./production.yaml  # This can override settings from base.yaml

# Settings here override both imported files
duckdb:
  database: catalog.duckdb
```

## Uniqueness Validation

After merging, Duckalog validates that certain items are unique:

- **Views**: Must have unique `(schema, name)` tuples
- **Semantic Models**: Must have unique names
- **Iceberg Catalogs**: Must have unique names
- **Attachments**: Must have unique aliases

If duplicates are found, you'll get an error:

```
Duplicate view name(s) found: users
```

## Circular Import Detection

Duckalog automatically detects and prevents circular imports:

```yaml
# file_a.yaml
imports:
  - ./file_b.yaml

# file_b.yaml
imports:
  - ./file_a.yaml  # This creates a circular reference!
```

This will fail with an error:
```
Circular import detected in import chain: file_a.yaml -> file_b.yaml -> file_a.yaml
```

## Remote Imports

You can import configuration files from remote storage systems such as S3, GCS, Azure Blob Storage, or HTTPS endpoints. This allows you to share common configuration across multiple projects or load configuration from centralized locations.

### Supported URI Schemes

Duckalog supports the following remote URI schemes:

- **S3**: `s3://bucket/path/config.yaml`
- **Google Cloud Storage**: `gs://bucket/path/config.yaml` or `gcs://bucket/path/config.yaml`
- **Azure Blob Storage**: `abfs://account@container/path/config.yaml`
- **SFTP**: `sftp://user@host/path/config.yaml`
- **HTTPS**: `https://example.com/config.yaml`

### Example: Import from S3

```yaml
# catalog.yaml
version: 1
imports:
  - s3://my-bucket/shared/base-config.yaml
  - ./local-config.yaml

duckdb:
  database: my-project.duckdb
```

### Example: Import from HTTPS

```yaml
# catalog.yaml
version: 1
imports:
  - https://raw.githubusercontent.com/company/config-templates/main/base.yaml

duckdb:
  database: main.duckdb
```

### Authentication

Remote imports use the same authentication mechanisms as regular remote config loading:

- **S3**: AWS credentials via environment variables, `~/.aws/credentials`, or IAM role
- **GCS**: Google Cloud credentials via `GOOGLE_APPLICATION_CREDENTIALS` or ADC
- **Azure**: Azure credentials via environment variables or managed identity
- **SFTP**: SSH credentials via SSH config or environment variables
- **HTTPS**: No authentication required for public URLs

For S3, you can use environment variables:
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
```

### Environment Variables in Remote Paths

You can use environment variables in remote import paths:

```yaml
# catalog.yaml
version: 1
imports:
  - https://${env:COMPANY}.s3.amazonaws.com/configs/base.yaml

duckdb:
  database: main.duckdb
```

### Error Handling

Remote import failures include clear error messages with the URI and operation:

```
Failed to load remote config 's3://bucket/config.yaml': NoSuchKey: The specified key does not exist
```

### Security Notes

- Remote imports follow the same security rules as remote config loading
- Credentials should be provided via environment variables or secure credential stores
- For HTTPS URLs, ensure you're using trusted endpoints
- Consider using signed URLs for temporary access to private resources

## Best Practices

### 1. Organize by Domain
```
config/
├── catalog.yaml          # Main file with imports
├── settings.yaml         # Database settings, extensions
├── views/
│   ├── users.yaml
│   ├── products.yaml
│   └── orders.yaml
└── environments/
    ├── dev.yaml
    └── prod.yaml
```

### 2. Use Empty Lists for Optional Sections
If a file only contains imports and no views, add an empty views list:

```yaml
# settings-only.yaml
version: 1
duckdb:
  database: db.duckdb
views: []  # Explicitly empty to avoid required field errors
```

### 3. Document Your Imports
Add comments explaining why files are imported:

```yaml
# catalog.yaml
imports:
  - ./settings.yaml        # Base database configuration
  - ./views/users.yaml     # User-related views
  - ./views/products.yaml  # Product catalog views
```

### 4. Version Control
- Keep import files in version control
- Use consistent naming conventions
- Add `.gitignore` for generated databases (`.duckdb` files)

## Common Patterns

### Environment-Specific Configuration

```yaml
# catalog.yaml
version: 1
imports:
  - ./base.yaml
  - ./environments/${env:ENVIRONMENT}.yaml  # dev.yaml, prod.yaml, etc.
```

### Shared Base Configuration

```yaml
# base.yaml
version: 1
duckdb:
  database: analytics.duckdb
  install_extensions:
    - httpfs
    - iceberg
```

Then import this in all your projects:
```yaml
# project1.yaml
imports:
  - ../shared/base.yaml
```

### Team Ownership

```
config/
├── catalog.yaml
├── infrastructure/        # Ops team owns this
│   └── database.yaml
├── analytics/             # Data team owns this
│   └── views.yaml
└── reporting/             # BI team owns this
    └── reports.yaml
```

## Migration from Single File

To migrate an existing single-file configuration:

1. Create a new main file:
```yaml
# catalog.yaml
version: 1
imports:
  - ./migrated-config.yaml
```

2. Rename your existing config:
```bash
mv old-catalog.yaml migrated-config.yaml
```

3. Test that it works:
```bash
duckalog build catalog.yaml
```

4. Gradually split `migrated-config.yaml` into smaller files

## Troubleshooting

### Debugging Import Issues

Use the `show-imports` command to visualize and debug your import graph:

```bash
# View the import tree
duckalog show-imports catalog.yaml

# Show import diagnostics (depth, file counts, duplicates)
duckalog show-imports catalog.yaml --diagnostics

# Export import graph as JSON for programmatic analysis
duckalog show-imports catalog.yaml --format json

# Preview the fully merged configuration
duckalog show-imports catalog.yaml --show-merged
```

This helps you:
- **Visualize the import structure** - See which files import which others
- **Detect circular imports** - Identify problematic import chains
- **Count total files** - Understand the complexity of your configuration
- **Find duplicate imports** - Catch redundant file references
- **Preview merged config** - Verify the final configuration before building

### File Not Found
If you see "Imported file not found", check:
- The path is correct and relative to the importing file
- The file exists and is readable
- Environment variables in paths are set correctly
- Use `duckalog show-imports catalog.yaml` to see the resolved paths

### Validation Errors
If you see "Field required" errors:
- Make sure all imported files have required fields (`version`, `duckdb`, `views`)
- Add empty lists for sections that don't apply: `views: []`
- Use `duckalog show-imports catalog.yaml --show-merged` to see the merged config

### Duplicate Names
If you see duplicate name errors:
- Check that view names are unique across all imported files
- Use schema-qualified names if needed: `schema.view_name`
- Use `duckalog show-imports catalog.yaml --diagnostics` to identify where duplicates come from

### Circular Imports
If you see a circular import error:
- Duckalog will show you the import chain where the cycle occurs
- Use `duckalog show-imports catalog.yaml` to visualize the structure
- Refactor your imports to eliminate the cycle (e.g., move common config to a separate file)

## See Also

- [Configuration Guide](../guides/usage.md)
- [Environment Variables](./environment-vars.md)
- [Path Resolution](./path-resolution-examples.md)
