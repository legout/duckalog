# DuckDB Settings Example

This example demonstrates how to use DuckDB settings in Duckalog to configure session behavior that goes beyond pragmas. Settings are applied after pragmas and allow you to control DuckDB's runtime behavior.

## When to Use Settings

Choose settings when you need to:
- Configure DuckDB session parameters that aren't pragmas
- Control memory allocation and threading behavior
- Enable/disable specific DuckDB features
- Set custom configuration parameters for performance tuning

## Basic Settings Configuration

### Single Setting Example

Create a file called `settings-example.yaml`:

```yaml
version: 1

duckdb:
  database: settings_catalog.duckdb
  
  # Extensions (optional)
  install_extensions:
    - httpfs
  
  # Pragmas (applied before settings)
  pragmas:
    - "PRAGMA enable_optimizer=true"
    - "PRAGMA enable_profiling=true"
  
  # Settings (applied after pragmas)
  settings: "SET enable_progress_bar = false"

views:
  - name: sample_data
    sql: |
      SELECT 
        'Settings Demo' as title,
        CURRENT_TIMESTAMP as demo_time
    description: "Simple demo view to test settings"
```

### Multiple Settings Example

For more comprehensive configuration:

```yaml
version: 1

duckdb:
  database: advanced_settings.duckdb
  install_extensions:
    - httpfs
    - fts
  
  pragmas:
    - "PRAGMA enable_optimizer=true"
    - "PRAGMA enable_profiling=true"
  
  # Multiple settings as a list
  settings:
    - "SET enable_progress_bar = false"
    - "SET threads = 4"
    - "SET memory_limit = '2GB'"
    - "SET enable_http_metadata_cache = true"

views:
  - name: analytics_data
    source: parquet
    uri: "s3://your-bucket/analytics/*.parquet"
    description: "Analytics data with optimized settings"
    
  - name: performance_metrics
    sql: |
      SELECT 
        COUNT(*) as total_rows,
        COUNT(DISTINCT user_id) as unique_users,
        AVG(session_duration) as avg_session
      FROM analytics_data
      WHERE event_date >= CURRENT_DATE - INTERVAL 30 DAYS
    description: "Performance metrics with optimized settings"
```

## Settings with Environment Variables

Just like pragmas, settings support environment variable interpolation:

```yaml
version: 1

duckdb:
  database: env_settings.duckdb
  
  settings:
    - "SET threads = ${env:THREAD_COUNT}"
    - "SET memory_limit = '${env:MEMORY_LIMIT}'"
    - "SET enable_progress_bar = ${env:ENABLE_PROGRESS:false}"

views:
  - name: config_demo
    sql: |
      SELECT 
        current_setting('threads') as threads,
        current_setting('memory_limit') as memory_limit,
        current_setting('enable_progress_bar') as progress_bar_enabled
    description: "Demo view showing current settings"
```

Set the environment variables:

```bash
export THREAD_COUNT="8"
export MEMORY_LIMIT="4GB"
export ENABLE_PROGRESS="false"
```

## Common DuckDB Settings

### Performance Settings

```yaml
duckdb:
  settings:
    # Threading and parallelism
    - "SET threads = 8"                    # Number of CPU threads
    - "SET enable_progress_bar = false"    # Disable progress output
    
    # Memory management
    - "SET memory_limit = '4GB'"           # Maximum memory usage
    
    # Network and caching
    - "SET enable_http_metadata_cache = true"   # Cache HTTP metadata
    - "SET enable_object_cache = true"          # Cache object files
```

### Query Optimization Settings

```yaml
duckdb:
  settings:
    # Query execution
    - "SET enable_progress_bar = false"
    - "SET preserve_insertion_order = false"    # Faster unordered results
    
    # Join performance
    - "SET force_parallelism = true"             # Force parallel execution
```

### Development and Debugging Settings

```yaml
duckdb:
  settings:
    # Debugging
    - "SET enable_progress_bar = true"           # Show progress for long queries
    - "SET enable_profiling = true"              # Enable query profiling
    
    # Output formatting
    - "SET max_width = 120"                     # Output width
    - "SET null_display = 'NULL'"                # How NULL values are displayed
```

## Step-by-Step Usage

### 1. Create Configuration

Save one of the examples above as `settings-example.yaml`.

### 2. Set Environment Variables (if using interpolation)

```bash
export THREAD_COUNT="4"
export MEMORY_LIMIT="2GB"
```

### 3. Validate Configuration

```bash
duckalog validate settings-example.yaml
```

### 4. Build Catalog

```bash
duckalog build settings-example.yaml
```

### 5. Verify Settings Applied

```bash
# Connect to the created database
duckdb settings_catalog.duckdb

# Check current settings
SELECT name, value FROM duckdb_settings() WHERE name LIKE '%thread%' OR name LIKE '%memory%';

# Or use the current_setting function
SELECT current_setting('threads') as thread_count;
SELECT current_setting('memory_limit') as memory_limit;
SELECT current_setting('enable_progress_bar') as progress_enabled;
```

## Settings vs Pragmas

### When to Use Pragmas

- **Database-level configuration** that affects the entire database file
- **Persistent settings** that should be saved with the database
- **Low-level optimizations** like `PRAGMA enable_optimizer`

### When to Use Settings

- **Session-level configuration** for the current connection
- **Runtime behavior** like progress bars and threading
- **Temporary configuration** that shouldn't persist
- **Feature toggles** like `SET enable_http_metadata_cache`

### Execution Order

1. **Extensions** are installed and loaded
2. **Pragmas** are executed (database-level)
3. **Settings** are executed (session-level)
4. **Views** are created

## Advanced Examples

### Conditional Settings Based on Environment

```yaml
version: 1

duckdb:
  database: conditional_settings.duckdb
  
  # Use different settings based on environment
  settings: "${env:DUCKDB_SETTINGS:SET enable_progress_bar = false}"

views:
  - name: environment_info
    sql: |
      SELECT 
        'Environment: ${env:ENV_NAME:development}' as environment,
        current_setting('enable_progress_bar') as progress_bar
    description: "Show environment and settings"
```

### Settings for Different Workloads

```yaml
# Production configuration - optimized for performance
version: 1

duckdb:
  database: production_catalog.duckdb
  settings:
    - "SET enable_progress_bar = false"
    - "SET threads = 16"
    - "SET memory_limit = '8GB'"
    - "SET enable_object_cache = true"

# Development configuration - more verbose
version: 1

duckdb:
  database: dev_catalog.duckdb
  settings:
    - "SET enable_progress_bar = true"
    - "SET threads = 2"
    - "SET memory_limit = '1GB'"
    - "SET enable_profiling = true"
```

## Troubleshooting

### Common Settings Issues

**1. Invalid Setting Name:**
```
Error: Catalog Error: unrecognized configuration parameter
```
Solution: Check DuckDB documentation for valid setting names, or use `PRAGMA table_info(duckdb_settings())` to see available settings.

**2. Setting Value Type Mismatch:**
```
Error: Parser Error: Expected type
```
Solution: Ensure the value type matches what the setting expects (string, integer, boolean).

**3. Settings Not Applied:**
- Check that settings are in the correct format (must start with "SET ")
- Verify settings are applied after pragmas in the execution order
- Use `current_setting('setting_name')` to verify the value

### Debugging Settings

```sql
-- List all current settings
SELECT name, value FROM duckdb_settings();

-- Check specific setting
SELECT current_setting('threads') as thread_count;

-- Show settings that were changed from defaults
SELECT name, value, default_value 
FROM duckdb_settings() 
WHERE value != default_value;
```

## Best Practices

1. **Use Environment Variables**: For sensitive values or deployment-specific settings
2. **Document Settings**: Add comments explaining why each setting is needed
3. **Test Settings**: Verify settings work as expected in your environment
4. **Separate Configs**: Use different configs for development vs production
5. **Monitor Performance**: Check that settings actually improve performance

This example shows how DuckDB settings in Duckalog provide fine-grained control over DuckDB's behavior, complementing the existing pragmas system for comprehensive configuration management.