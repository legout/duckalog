# How to Debug Build Failures

Diagnose and resolve common catalog build issues and errors with systematic debugging approaches.

## Problem

Your Duckalog catalog build is failing with errors, and you need to identify the root cause and fix it systematically.

## Prerequisites

- Basic Duckalog configuration knowledge
- Understanding of SQL and database concepts
- Familiarity with command line tools
- Access to configuration files

## Solution

### 1. Enable Verbose Logging

Get detailed information about what's happening during the build:

```bash
# Enable verbose output
duckalog build catalog.yaml --verbose

# Enable debug logging (more detailed)
export DUCKALOG_LOG_LEVEL=DEBUG
duckalog build catalog.yaml --verbose
```

### 2. Validate Configuration First

Check if your configuration is valid before attempting to build:

```bash
# Basic validation
duckalog validate catalog.yaml

# Validation with import diagnostics
duckalog show-imports catalog.yaml --diagnostics

# Show merged configuration
duckalog show-imports catalog.yaml --show-merged
```

### 3. Use Dry Run Mode

Generate SQL without executing to identify issues:

```bash
# Generate SQL to inspect
duckalog generate-sql catalog.yaml --output debug.sql

# Review generated SQL
cat debug.sql

# Check for obvious issues
grep -i "error\|warning\|undefined" debug.sql
```

### 4. Isolate Problematic Components

Test individual parts of your configuration:

```yaml
# Create minimal test config
# test_minimal.yaml
version: 1
duckdb:
  database: test.duckdb
views:
  - name: test_view
    sql: "SELECT 1 as test"
```

```bash
# Test minimal config
duckalog build test_minimal.yaml

# If this works, gradually add complexity
# Add one view at a time to identify the problematic one
```

### 5. Check Common Error Categories

#### Configuration Errors

**Missing Required Fields**
```yaml
# ❌ Missing version
duckdb:
  database: catalog.duckdb
views: []

# ✅ Complete configuration
version: 1
duckdb:
  database: catalog.duckdb
views: []
```

**Invalid YAML Syntax**
```yaml
# ❌ Wrong indentation
duckdb:
database: catalog.duckdb
  threads: 4

# ✅ Correct indentation
duckdb:
  database: catalog.duckdb
  threads: 4
```

**Environment Variable Issues**
```bash
# Check if variables are set
echo $AWS_ACCESS_KEY_ID
echo $PG_PASSWORD

# Set missing variables
export AWS_ACCESS_KEY_ID=your_key
export PG_PASSWORD=your_password

# Test with variables
duckalog validate catalog.yaml
```

#### Path Resolution Errors

**File Not Found**
```yaml
# ❌ Wrong relative path
views:
  - name: data
    uri: "../missing/data.parquet"

# ✅ Correct path (relative to config)
views:
  - name: data
    uri: "./data/data.parquet"

# ✅ Absolute path
views:
  - name: data
    uri: "/absolute/path/to/data.parquet"
```

**Path Traversal Security**
```yaml
# ❌ Dangerous path (blocked)
views:
  - name: data
    uri: "../../../etc/passwd"

# ✅ Safe path
views:
  - name: data
    uri: "./data/data.parquet"
```

#### SQL Syntax Errors

**Unquoted Identifiers**
```sql
-- ❌ Wrong - unquoted identifiers with spaces
CREATE VIEW daily users AS SELECT * FROM events;

-- ✅ Correct - quoted identifiers
CREATE VIEW "daily users" AS SELECT * FROM events;
```

**Invalid SQL Syntax**
```sql
-- ❌ Wrong - missing FROM clause
CREATE VIEW test_view AS SELECT;

-- ✅ Correct - complete SQL
CREATE VIEW test_view AS SELECT 1;
```

**Data Type Issues**
```sql
-- ❌ Wrong - incompatible types
CREATE VIEW test_view AS SELECT 'text' + 123;

-- ✅ Correct - type conversion
CREATE VIEW test_view AS SELECT 'text' || CAST(123 AS VARCHAR);
```

#### Database Connection Errors

**Database File Issues**
```bash
# Check if database file exists
ls -la catalog.duckdb

# Check file permissions
ls -la catalog.duckdb

# Test database connection manually
duckdb catalog.duckdb
# Then: .tables
```

**Attachment Failures**
```yaml
# ❌ Attachment file doesn't exist
attachments:
  duckdb:
    - alias: reference
      path: "./missing.duckdb"

# ✅ Attachment file exists
attachments:
  duckdb:
    - alias: reference
      path: "./reference.duckdb"
```

### 6. Systematic Debugging Process

Follow this step-by-step approach:

#### Step 1: Reproduce the Error
```bash
# Ensure error is reproducible
duckalog build catalog.yaml
# Note the exact error message
```

#### Step 2: Isolate the Component
```yaml
# Create test configs for each section
# test_views.yaml - test views only
# test_attachments.yaml - test attachments only
# test_imports.yaml - test imports only
```

```bash
# Test each component
duckalog build test_views.yaml
duckalog build test_attachments.yaml
duckalog build test_imports.yaml
# Identify which component fails
```

#### Step 3: Examine Generated SQL
```bash
# Generate SQL for inspection
duckalog generate-sql catalog.yaml --output inspect.sql

# Look for:
# - Syntax errors
# - Missing table references
# - Invalid column names
# - Type mismatches
```

#### Step 4: Test Manual Execution
```bash
# Execute SQL manually in DuckDB
duckdb catalog.duckdb
# Then paste SQL from inspect.sql
# Note any errors
```

#### Step 5: Fix and Validate
```bash
# Fix identified issues
# Edit configuration file

# Validate fix
duckalog validate catalog.yaml

# Test build
duckalog build catalog.yaml
```

### 7. Advanced Debugging Techniques

#### Use DuckDB Directly
```bash
# Connect directly to database
duckdb catalog.duckdb

# Enable verbose output
.databases
.tables
.schema table_name

# Test problematic view manually
CREATE OR REPLACE VIEW "problem_view" AS SELECT * FROM source_table;
SELECT * FROM "problem_view" LIMIT 5;
```

#### Check Import Resolution
```bash
# Show import graph
duckalog show-imports catalog.yaml

# Check for circular imports
duckalog show-imports catalog.yaml --diagnostics

# Verify resolved paths
duckalog show-imports catalog.yaml --format json | jq '.import_graph'
```

#### Enable DuckDB Debugging
```yaml
# Add debugging pragmas
duckdb:
  database: catalog.duckdb
  pragmas:
    - "SET enable_progress_bar=true"      # Show progress
    - "SET enable_profiling=true"       # Profile queries
    - "SET preserve_insertion_order=true" # Maintain order
```

## Verification

### 1. Successful Build Test
```bash
# Build should complete without errors
duckalog build catalog.yaml

# Check exit code
echo $?
# Should be 0

# Verify database was created
ls -la catalog.duckdb

# Test basic query
duckdb catalog.duckdb -c "SELECT COUNT(*) FROM information_schema.tables"
```

### 2. View Creation Test
```bash
# Verify views were created
duckdb catalog.duckdb -c "SHOW TABLES"

# Test each view
duckdb catalog.duckdb -c "DESCRIBE your_view_name"
duckdb catalog.duckdb -c "SELECT * FROM your_view_name LIMIT 1"
```

### 3. Data Access Test
```bash
# Test data access
duckdb catalog.duckdb -c "SELECT COUNT(*) FROM your_view_name"

# Test joins if applicable
duckdb catalog.duckdb -c "SELECT * FROM view1 JOIN view2 ON view1.id = view2.id LIMIT 5"
```

## Common Variations

### 1. Large Configuration Debugging

For complex configurations with many views:

```bash
# Build specific views only
duckalog build catalog.yaml --include-views "view1,view2"

# Exclude problematic views
duckalog build catalog.yaml --exclude-views "problem_view"

# Build incrementally
for view in view1 view2 view3; do
  echo "Building view: $view"
  duckalog build catalog.yaml --include-views "$view"
done
```

### 2. Remote Configuration Debugging

For remote configurations:

```bash
# Test remote access
curl -I https://example.com/config.yaml

# Download and test locally
curl -o local_config.yaml https://example.com/config.yaml
duckalog build local_config.yaml

# Test with authentication
export AWS_ACCESS_KEY_ID=test_key
duckalog build s3://bucket/config.yaml
```

### 3. Performance Debugging

For builds that are slow or timeout:

```yaml
# Add performance monitoring
duckdb:
  database: catalog.duckdb
  pragmas:
    - "SET enable_progress_bar=true"   # Show progress
    - "SET profiling_mode=true"      # Enable profiling
    - "SET profiling_output='/tmp/profile.json'" # Save profile
```

```bash
# Monitor resource usage
time duckalog build catalog.yaml

# Check memory usage
/usr/bin/time -v duckalog build catalog.yaml

# Profile with DuckDB
duckdb catalog.duckdb -c "PRAGMA profiling_mode;"
# Run queries
# PRAGMA profiling_output;
```

## Troubleshooting

### Build Fails Silently

**Issue**: No error message, but build doesn't complete

**Solution**:
```bash
# Enable verbose logging
duckalog build catalog.yaml --verbose

# Check for hanging processes
ps aux | grep duckalog

# Use timeout
timeout 300 duckalog build catalog.yaml
```

### Memory Errors

**Issue**: "Out of memory" errors during build

**Solution**:
```yaml
# Reduce memory usage
duckdb:
  database: catalog.duckdb
  pragmas:
    - "SET memory_limit='1GB'"    # Reduce from default
    - "SET threads=2"             # Reduce parallelism
```

### Lock File Errors

**Issue**: "Database is locked" errors

**Solution**:
```bash
# Find and kill conflicting processes
lsof | grep catalog.duckdb
pkill -f duckdb

# Remove lock files
rm -f catalog.duckdb.wal catalog.duckdb.lock

# Build with different database name
duckalog build catalog.yaml --db-path catalog_new.duckdb
```

### Permission Errors

**Issue**: "Permission denied" errors

**Solution**:
```bash
# Check file permissions
ls -la catalog.yaml
ls -la data/

# Fix permissions
chmod 644 catalog.yaml
chmod 755 data/

# Check database directory
mkdir -p db
chmod 755 db
```

## Best Practices

### 1. Preventive Measures
- **Validate early and often** with `duckalog validate`
- **Use version control** to track configuration changes
- **Test in isolation** before integrating
- **Use meaningful names** for views and attachments

### 2. Debugging Workflow
- **Start simple** and add complexity gradually
- **Document your findings** as you debug
- **Use systematic approach** rather than random changes
- **Keep backup copies** of working configurations

### 3. Error Documentation
- **Record error messages** exactly as they appear
- **Note the context** when errors occur
- **Document solutions** that work for future reference
- **Share findings** with team and community

## Getting Help

When you're stuck:

1. **Check the troubleshooting guide** in the main documentation
2. **Search GitHub issues** for similar problems
3. **Create minimal reproduction** when asking for help
4. **Include configuration files** (sanitized of secrets)
5. **Provide exact error messages** and commands used

### Information to Include in Help Requests
```bash
# System information
duckalog --version
python3 --version
uname -a

# Configuration (sanitized)
duckalog show-imports catalog.yaml --show-merged

# Error details
# Full error message and stack trace
# Command used and exit code
# Steps to reproduce
```

You now have a systematic approach to diagnose and resolve any Duckalog catalog build issues that may arise.