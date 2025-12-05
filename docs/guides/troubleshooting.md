# Troubleshooting Guide

This guide helps you diagnose and resolve common issues when working with Duckalog. Errors are organized by category with specific solutions and debugging techniques.

## Configuration Errors

### Config File Not Found

**Error:** `ConfigError: Config file not found: catalog.yaml`

**Causes:**
- File path is incorrect
- File doesn't exist
- Wrong working directory

**Solutions:**
```bash
# Check if file exists
ls -la catalog.yaml

# Use absolute path
duckalog build /full/path/to/catalog.yaml

# Check current working directory
pwd
```

**Prevention:**
- Use relative paths from config directory: `./catalog.yaml`
- Use absolute paths in CI/CD: `/app/config/catalog.yaml`

### Invalid YAML/JSON Syntax

**Error:** `ConfigError: Configuration validation failed`

**Causes:**
- YAML indentation errors
- Missing quotes around strings
- Invalid JSON structure

**Solutions:**
```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('catalog.yaml'))"

# Use YAML linter
yamllint catalog.yaml

# Validate JSON syntax
python -c "import json; json.load(open('catalog.json'))"
```

**Common YAML Issues:**
```yaml
# ❌ Wrong - inconsistent indentation
duckdb:
  database: db.duckdb
    threads: 4

# ✅ Correct - consistent indentation
duckdb:
  database: db.duckdb
  threads: 4

# ❌ Wrong - unquoted special characters
views:
  - name: user's data
    sql: SELECT * FROM users

# ✅ Correct - quoted strings
views:
  - name: "user's data"
    sql: "SELECT * FROM users"
```

### Missing Required Fields

**Error:** `ConfigError: Field required`

**Causes:**
- Missing `version` field
- Missing `duckdb` section
- Missing `views` list

**Solutions:**
```yaml
# ✅ Minimal valid configuration
version: 1
duckdb:
  database: catalog.duckdb
views: []  # Can be empty
```

### Environment Variable Issues

**Error:** `ConfigError: Environment variable not found: AWS_ACCESS_KEY_ID`

**Causes:**
- Environment variable not set
- Typo in variable name
- Variable not exported

**Solutions:**
```bash
# Check if variable is set
echo $AWS_ACCESS_KEY_ID

# Set variable
export AWS_ACCESS_KEY_ID=your_key_here

# Set in .env file
echo "AWS_ACCESS_KEY_ID=your_key_here" >> .env

# Use with direnv
echo "export AWS_ACCESS_KEY_ID=your_key_here" > .envrc
direnv allow
```

**Debugging:**
```bash
# Show all environment variables
env | grep AWS

# Test variable interpolation
duckalog validate catalog.yaml  # Shows missing variables
```

## Path Resolution Errors

### File Not Found

**Error:** `PathResolutionError: Failed to resolve import path: ./data.parquet`

**Causes:**
- Relative path from wrong directory
- File actually doesn't exist
- Path traversal outside allowed bounds

**Solutions:**
```bash
# Check resolved path
duckalog show-imports catalog.yaml --diagnostics

# Use absolute path
views:
  - name: data
    uri: "/absolute/path/to/data.parquet"

# Check file location relative to config
ls -la $(dirname catalog.yaml)/data/
```

### Path Traversal Security

**Error:** `PathResolutionError: Path traversal detected`

**Causes:**
- Using `../../../etc/passwd` patterns
- Symbolic links outside allowed directory
- Path normalization issues

**Solutions:**
```yaml
# ❌ Dangerous - blocked by security
views:
  - name: data
    uri: "../../../etc/passwd"

# ✅ Safe - use proper relative paths
views:
  - name: data
    uri: "./data/file.parquet"

# ✅ Safe - use absolute paths
views:
  - name: data
    uri: "/data/file.parquet"
```

## Import Errors

### Circular Import Detection

**Error:** `CircularImportError: Circular import detected: file_a.yaml -> file_b.yaml -> file_a.yaml`

**Causes:**
- File A imports File B
- File B imports File A
- Complex circular chains

**Solutions:**
```bash
# Visualize import structure
duckalog show-imports catalog.yaml

# Identify circular dependency
duckalog show-imports catalog.yaml --diagnostics
```

**Fix Strategies:**
```yaml
# ❌ Circular dependency
# file_a.yaml
imports:
  - ./file_b.yaml

# file_b.yaml  
imports:
  - ./file_a.yaml

# ✅ Solution - extract common config
# common.yaml
version: 1
duckdb:
  database: shared.duckdb

# file_a.yaml
imports:
  - ./common.yaml

# file_b.yaml
imports:
  - ./common.yaml
```

### Import File Not Found

**Error:** `ImportFileNotFoundError: Imported file not found: ./missing.yaml`

**Causes:**
- Wrong import path
- File deleted/moved
- Relative path resolution issues

**Solutions:**
```bash
# Check import resolution
duckalog show-imports catalog.yaml

# Verify file exists
ls -la ./missing.yaml

# Use absolute paths
imports:
  - "/full/path/to/missing.yaml"
```

### Duplicate Names

**Error:** `DuplicateNameError: Duplicate view name(s) found: users`

**Causes:**
- Same view name in multiple files
- Name collision after imports
- Case sensitivity issues

**Solutions:**
```bash
# Find duplicates
duckalog show-imports catalog.yaml --diagnostics

# Use schema qualification
views:
  - name: analytics.users  # Schema qualified
  - name: legacy.users     # Different schema
```

**Fix Strategies:**
```yaml
# ❌ Duplicate names
# users.yaml
views:
  - name: users
    sql: "SELECT * FROM new_users"

# legacy.yaml
views:
  - name: users
    sql: "SELECT * FROM old_users"

# ✅ Solution - unique names
# users.yaml
views:
  - name: active_users
    sql: "SELECT * FROM new_users"

# legacy.yaml
views:
  - name: legacy_users
    sql: "SELECT * FROM old_users"
```

## Database Connection Errors

### DuckDB Connection Failed

**Error:** `EngineError: Failed to connect to DuckDB`

**Causes:**
- Database file permissions
- Disk space issues
- DuckDB version conflicts

**Solutions:**
```bash
# Check file permissions
ls -la catalog.duckdb

# Check disk space
df -h

# Test DuckDB directly
python -c "import duckdb; conn = duckdb.connect('test.duckdb'); print('OK')"
```

### Database Lock Errors

**Error:** `EngineError: Database is locked`

**Causes:**
- Another process has database open
- Previous build crashed
- File system issues

**Solutions:**
```bash
# Find processes using database
lsof catalog.duckdb

# Kill conflicting processes
pkill -f duckdb

# Remove lock file (if safe)
rm catalog.duckdb.wal
```

## SQL Execution Errors

### View Creation Failed

**Error:** `EngineError: Failed to create view: invalid_sql`

**Causes:**
- SQL syntax errors
- Missing tables/files
- Invalid column references

**Solutions:**
```bash
# Generate SQL to inspect
duckalog generate-sql catalog.yaml --output views.sql

# Test SQL manually
duckdb catalog.duckdb
# Then paste SQL to test

# Validate with dry run
duckalog build catalog.yaml --dry-run
```

**Common SQL Issues:**
```sql
-- ❌ Wrong - unquoted identifiers
CREATE VIEW daily users AS SELECT * FROM events;

-- ✅ Correct - quoted identifiers
CREATE VIEW "daily users" AS SELECT * FROM events;

-- ❌ Wrong - missing quotes for paths
COPY users FROM 'path/with spaces/data.parquet';

-- ✅ Correct - proper quoting
COPY users FROM 'path/with spaces/data.parquet';
```

### Attachment Errors

**Error:** `EngineError: Failed to attach database`

**Causes:**
- Attachment database doesn't exist
- Permission issues
- Invalid attachment configuration

**Solutions:**
```yaml
# Check attachment paths
attachments:
  duckdb:
    - alias: refdata
      path: "./reference.duckdb"  # Must exist
      read_only: true

# Test attachment manually
duckdb main.duckdb
ATTACH 'reference.duckdb' AS refdata;
```

## Remote Configuration Errors

### S3 Authentication Failed

**Error:** `RemoteConfigError: Failed to load remote config: NoSuchKey`

**Causes:**
- Invalid AWS credentials
- Wrong bucket/object names
- Permission issues

**Solutions:**
```bash
# Test AWS credentials
aws s3 ls s3://your-bucket/

# Check specific object
aws s3 ls s3://your-bucket/config.yaml

# Set credentials properly
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
```

### Network Timeout

**Error:** `RemoteConfigError: Failed to load remote config: timeout`

**Causes:**
- Network connectivity issues
- Firewall blocking
- Slow remote servers

**Solutions:**
```bash
# Test connectivity
curl -I https://example.com/config.yaml

# Increase timeout
duckalog build https://example.com/config.yaml --timeout 120

# Use local copy for development
curl -o local-config.yaml https://example.com/config.yaml
duckalog build local-config.yaml
```

## Performance Issues

### Slow Build Times

**Symptoms:**
- Building catalog takes minutes
- High memory usage
- Slow query performance

**Solutions:**
```yaml
# Optimize DuckDB settings
duckdb:
  database: catalog.duckdb
  pragmas:
    - "SET memory_limit='2GB'"
    - "SET threads=4"
    - "SET enable_progress_bar=false"
```

**Large File Handling:**
```yaml
# Use efficient file formats
views:
  - name: events
    source: parquet  # Better than CSV
    uri: "s3://bucket/events/*.parquet"

# Filter early
views:
  - name: recent_events
    source: parquet
    uri: "s3://bucket/events/*.parquet"
    sql: |
      SELECT * FROM recent_events 
      WHERE event_date >= '2023-01-01'
```

## Debugging Techniques

### Enable Verbose Logging

```bash
# Enable verbose output
duckalog build catalog.yaml --verbose

# Enable debug logging
export DUCKALOG_LOG_LEVEL=DEBUG
duckalog build catalog.yaml
```

### Use Diagnostic Commands

```bash
# Validate configuration only
duckalog validate catalog.yaml

# Show import structure
duckalog show-imports catalog.yaml --diagnostics

# Generate SQL without executing
duckalog generate-sql catalog.yaml --output debug.sql

# Test with dry run
duckalog build catalog.yaml --dry-run
```

### Isolate Problems

```bash
# Create minimal config
cat > minimal.yaml << EOF
version: 1
duckdb:
  database: test.duckdb
views:
  - name: test
    sql: "SELECT 1 as test"
EOF

# Test minimal case
duckalog build minimal.yaml

# Gradually add complexity
# Then add your views one by one
```

## Getting Help

### Collect Debug Information

```bash
# System information
python --version
duckalog --version

# Configuration dump
duckalog show-imports catalog.yaml --format json > debug.json

# Generated SQL
duckalog generate-sql catalog.yaml --output generated.sql
```

### Report Issues

When reporting issues, include:

1. **Configuration file** (sanitized)
2. **Error message** (full traceback)
3. **Command used** (exact command)
4. **Environment details**:
   ```bash
   duckalog --version
   python --version
   uname -a
   ```

### Community Resources

- **GitHub Issues**: [Report bugs and request features](https://github.com/legout/duckalog/issues)
- **Documentation**: [Complete reference docs](../reference/api.md)
- **Examples**: [Working examples](../examples/index.md)

## Quick Reference

| Error Type | Common Cause | Quick Fix |
|-------------|---------------|-----------|
| `Config file not found` | Wrong path | Use `ls` to verify file exists |
| `Field required` | Missing `version` or `duckdb` | Add minimal required fields |
| `Circular import` | A imports B, B imports A | Extract common config to separate file |
| `Duplicate name` | Same view name in multiple files | Use unique names or schema qualification |
| `Database locked` | Another process using database | Kill conflicting processes |
| `SQL syntax error` | Invalid SQL in views | Use `generate-sql` to test SQL |
| `Authentication failed` | Invalid cloud credentials | Check environment variables |
| `Path traversal` | Security violation | Use proper relative/absolute paths |