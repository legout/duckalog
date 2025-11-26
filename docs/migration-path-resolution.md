# Migration Guide: Path Resolution

This guide helps existing Duckalog users migrate from absolute paths to relative paths to take advantage of the new automatic path resolution feature.

## What's Changed

### Before (Legacy Behavior)
- Relative paths like `"data/file.parquet"` were passed directly to DuckDB
- Users had to ensure they ran commands from the correct working directory
- Paths would fail if the working directory changed
- Absolute paths were required for reliable operation

### After (New Behavior)
- Relative paths are automatically resolved relative to the configuration file's directory
- Commands work consistently regardless of working directory
- Paths are resolved securely with validation
- Both relative and absolute paths continue to work

## Migration Benefits

### ✅ Portability
```yaml
# Old way: Required specific working directory
views:
  - name: users
    source: parquet
    uri: "/home/project/data/users.parquet"  # Only works from specific location

# New way: Works from anywhere
views:
  - name: users
    source: parquet
    uri: "data/users.parquet"  # Works from any working directory
```

### ✅ Simplified Project Structure
```yaml
# Recommended structure:
# my-project/
# ├── catalog.yaml       # Configuration
# └── data/              # Data files
#     ├── users.parquet
#     └── events.parquet

# In catalog.yaml:
views:
  - name: users
    source: parquet
    uri: "data/users.parquet"  # Simple and clear
```

### ✅ Better Collaboration
- Team members can work from different locations
- No need to coordinate working directories
- Version control friendly paths

## Migration Process

### Step 1: Assess Current Configuration

First, identify all absolute paths in your configuration:

```bash
# Search for absolute paths (Unix/Linux/macOS)
grep -r "\"uri.*:/" your-config.yaml

# Search for absolute paths (Windows)
grep -r "\"uri.*[A-Z]:" your-config.yaml
```

### Step 2: Plan Path Changes

Create a mapping of old to new paths:

| Old Path | New Path | Notes |
|----------|----------|-------|
| `/home/user/data/users.parquet` | `data/users.parquet` | Move data relative to config |
| `C:\project\data\users.parquet` | `data/users.parquet` | Same structure, different separator |
| `/absolute/reference.db` | `../shared/reference.db` | If shared with other projects |

### Step 3: Reorganize Data Files

Move your data files to be relative to your configuration:

```bash
# Create data directory structure
mkdir -p data processed reference

# Move files to appropriate locations
mv /path/to/users.parquet data/
mv /path/to/events.parquet processed/
mv /path/to/reference.db reference/
```

### Step 4: Update Configuration

Update your configuration file with relative paths:

**Before:**
```yaml
version: 1
views:
  - name: users
    source: parquet
    uri: "/home/user/project/data/users.parquet"

  - name: events
    source: parquet
    uri: "/home/user/project/data/events.parquet"

attachments:
  duckdb:
    - alias: reference
      path: "/home/user/project/reference/reference.db"
```

**After:**
```yaml
version: 1
views:
  - name: users
    source: parquet
    uri: "data/users.parquet"

  - name: events
    source: parquet
    uri: "processed/events.parquet"

attachments:
  duckdb:
    - alias: reference
      path: "reference/reference.db"
```

### Step 5: Test Migration

Validate that your updated configuration works:

```bash
# Test from the configuration directory
cd /path/to/config
duckalog validate catalog.yaml

# Test from a different working directory
cd /tmp
duckalog validate /path/to/config/catalog.yaml
```

Both should work identically.

## Advanced Migration Scenarios

### Scenario 1: Shared Data Between Projects

**Challenge**: You have data shared between multiple projects

**Solution**: Use relative paths with reasonable parent directory traversal

```yaml
# Project A
views:
  - name: shared_lookup
    source: parquet
    uri: "../shared-data/lookup.parquet"  # Relative to project A

# Project B
views:
  - name: shared_lookup
    source: parquet
    uri: "../shared-data/lookup.parquet"  # Same path, works from both
```

### Scenario 2: Environment-Specific Paths

**Challenge**: Different paths for dev/staging/production

**Solution**: Use environment variables with relative path defaults

```yaml
# For development (default to relative paths)
attachments:
  duckdb:
    - alias: reference
      path: "${env:REFERENCE_DB_PATH:./reference.duckdb}"
      read_only: true

# For production (can override with absolute path if needed)
# export REFERENCE_DB_PATH=/var/data/reference.duckdb
```

### Scenario 3: Windows to Cross-Platform

**Challenge**: Moving from Windows absolute paths to cross-platform relative paths

**Before (Windows):**
```yaml
views:
  - name: users
    source: parquet
    uri: "C:\\Users\\User\\project\\data\\users.parquet"
```

**After (Cross-platform):**
```yaml
views:
  - name: users
    source: parquet
    uri: "data/users.parquet"  # Works on Windows, macOS, Linux
```

## Rollback Plan

If you encounter issues during migration:

1. **Keep backups**: Save your original configuration before making changes
2. **Test incrementally**: Migrate one path at a time and test each change
3. **Verify functionality**: Run your full workflow after each change

To rollback:
```bash
# Restore original configuration
cp catalog.yaml.backup catalog.yaml

# Restore original data organization
mv data/* /original/data/location/
```

## Verification Checklist

After migration, verify:

- [ ] `duckalog validate` works from any working directory
- [ ] `duckalog build` creates the expected views
- [ ] `duckalog generate-sql` produces correct SQL with absolute paths
- [ ] Web UI (if used) loads and functions correctly
- [ ] All data sources are accessible
- [ ] No security violations are reported

## Troubleshooting

### Issue: "File does not exist"

**Cause**: Data files not moved to correct relative location

**Solution**: 
```bash
# Check where paths resolve to
python3 -c "
from duckalog.config import load_config
config = load_config('catalog.yaml')
for view in config.views:
    if view.uri:
        print(f'{view.name}: {view.uri}')
"
```

### Issue: "Path resolution violates security rules"

**Cause**: Path tries to escape reasonable boundaries

**Solution**: Avoid excessive parent directory traversal:
```yaml
# Bad
uri: "../../../etc/passwd"  # Blocked for security

# Good
uri: "../shared/data.parquet"  # Reasonable parent traversal
```

### Issue: Cross-platform compatibility

**Cause**: Using platform-specific path separators

**Solution**: Use forward slashes for cross-platform compatibility:
```yaml
# Good (cross-platform)
uri: "data/users.parquet"

# Platform-specific
uri: "data\\users.parquet"  # Windows only
```

## Getting Help

If you encounter issues during migration:

1. **Check logs**: Look for path resolution debug messages
2. **Validate step by step**: Test each change individually
3. **Use absolute paths temporarily**: You can always fall back to absolute paths
4. **Consult examples**: See `examples/` directory for reference patterns

## Examples for Reference

See these working examples of relative path usage:

- **Simple Parquet**: `examples/simple_parquet/catalog.yml`
- **Multi-Source Analytics**: `examples/data-integration/multi-source-analytics/catalog.yaml`
- **DuckDB Performance**: `examples/production-operations/duckdb-performance-settings/catalog-*.yaml`

Each example demonstrates different patterns for organizing and referencing data files with relative paths.