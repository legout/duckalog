# How to Manage Paths in Duckalog

This guide provides practical recommendations for managing file paths in Duckalog configurations to ensure security, portability, maintainability, and cross-platform compatibility.

## Quick Reference

- **Use relative paths** for local data files
- **Organize data logically** relative to your configuration
- **Validate path accessibility** regularly
- **Implement security boundaries** with reasonable limits
- **Consider cross-platform compatibility** in all paths
- **Use environment variables** for external dependencies

## Choose a Relative-First Path Strategy

Relative paths are automatically resolved against the configuration file's directory. This makes configurations portable and independent of the working directory.

### ✅ Recommended

```yaml
version: 1

views:
  - name: users
    source: parquet
    uri: "data/users.parquet"

  - name: shared_events
    source: parquet
    uri: "../shared/events/*.parquet"

  - name: cloud_backup
    source: parquet
    uri: "s3://company-bucket/data/*.parquet"
```

### ❌ Avoid

```yaml
views:
  - name: users
    source: parquet
    uri: "/home/user/project/data/users.parquet"

  - name: events
    source: parquet
    uri: "C:\\Projects\\Analytics\\Data\\events.parquet"
```

## Organize Your Project Directory

A consistent project structure makes relative paths predictable and easy to maintain:

```
project-root/
├── catalog.yaml
├── data/
│   ├── raw/
│   ├── processed/
│   └── reference/
├── reference/
│   └── lookup-dbs/
└── sql/
```

Map your configuration to this structure:

```yaml
version: 1

duckdb:
  database: "analytics.duckdb"

attachments:
  duckdb:
    - alias: lookups
      path: "reference/lookup-dbs/main-reference.duckdb"
      read_only: true

views:
  - name: raw_users
    source: parquet
    uri: "data/raw/users.parquet"

  - name: daily_metrics
    source: parquet
    uri: "data/processed/daily/*.parquet"
```

## Keep Paths Cross-Platform

Use forward slashes in all paths. Duckalog handles platform-specific translation internally.

```yaml
# ✅ Works on Windows, macOS, and Linux
uri: "data/subdirectory/files.parquet"

# ❌ Windows only
uri: "data\\subdirectory\\files.parquet"
```

For environment-specific paths, use environment variables with sensible defaults:

```yaml
views:
  - name: production_data
    source: parquet
    uri: "${env:DATA_DIR:data}/*.parquet"
```

## Apply Security Boundaries

Duckalog validates all paths against security rules. Design your paths to stay within safe boundaries.

### Safe Patterns

```yaml
views:
  - name: local_data
    source: parquet
    uri: "data/safe-data.parquet"

  - name: shared_data
    source: parquet
    uri: "../shared/safe-data.parquet"
```

### Patterns That Will Be Blocked

```yaml
views:
  - name: dangerous
    source: parquet
    uri: "../../../../etc/passwd"  # Excessive traversal

  - name: system_file
    source: parquet
    uri: "/etc/shadow"  # System directory access
```

## Standardize Conventions for Your Team

Document your project's path conventions so all team members follow the same patterns:

```yaml
version: 1

views:
  - name: customer_data
    source: parquet
    uri: "data/customers/current/*"
    description: |
      Current customer data from CRM system.
      Location: data/customers/current/
      Owner: data-engineering-team
```

## Validate Paths Regularly

Run validation commands as part of your workflow:

```bash
# Validate configuration
uv run duckalog validate catalog.yaml

# Check path accessibility
uv run duckalog show-paths catalog.yaml --check

# Test from a different working directory
cd /tmp
uv run duckalog validate /path/to/project/catalog.yaml
```

## See Also

- [Path Resolution](../path-resolution.md) — Conceptual explanation of how path resolution works
- [Path Resolution Examples](../examples/path-resolution-examples.md) — Detailed configuration examples
- [Migration Guide: Path Resolution](../migration-path-resolution.md) — Migrating from absolute to relative paths
