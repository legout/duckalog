# CLI Reference

Complete reference for all Duckalog command-line interface commands, options, and usage patterns.

## Overview

Duckalog provides a comprehensive CLI for building, validating, and managing DuckDB catalogs. All commands support consistent patterns for help, configuration, and output formatting.

## Global Options

These options are available for all commands:

### Help and Version
```bash
# Show help
duckalog --help
duckalog <command> --help

# Show version
duckalog version
```

### Configuration Options
```bash
# Specify configuration file (positional argument)
duckalog build catalog.yaml

# Use remote configuration
duckalog build s3://bucket/config.yaml

# Enable verbose output
duckalog build catalog.yaml --verbose

# Suppress output
duckalog build catalog.yaml --quiet
```

### Output Formatting
```bash
# JSON output
duckalog validate catalog.yaml --format json

# Colored output (default)
duckalog build catalog.yaml --color

# No color
duckalog build catalog.yaml --no-color
```

## Commands

### build

Build or update a DuckDB catalog from configuration.

#### Syntax
```bash
duckalog build [OPTIONS] CONFIG_PATH
```

#### Options
```bash
--db-path, --database-path PATH
    Override database path from configuration
    
--dry-run, --dry
    Generate SQL only, don't execute
    
--verbose, -v
    Enable verbose logging
    
--quiet, -q
    Suppress output except errors
    
--color, --no-color
    Enable/disable colored output
    
--format FORMAT
    Output format (text, json)
    
--threads NUM
    Override thread count
    
--memory-limit SIZE
    Override memory limit (e.g., '2GB')
    
--filesystem fs
    Custom filesystem for remote configs
```

#### Examples
```bash
# Basic build
duckalog build catalog.yaml

# With custom database path
duckalog build catalog.yaml --db-path analytics.duckdb

# Dry run to generate SQL
duckalog build catalog.yaml --dry-run

# Verbose build with custom settings
duckalog build catalog.yaml --verbose --threads 8 --memory-limit '4GB'

# Remote configuration
duckalog build s3://bucket/config.yaml --verbose

# JSON output
duckalog build catalog.yaml --format json
```

#### Output
```bash
# Success
✅ Built catalog 'catalog.yaml' successfully
📊 Database: analytics.duckdb
📋 Views created: 15
🔗 Attachments: 3
⏱️ Build time: 2.3s

# With warnings
⚠️  Warning: View 'users' has no description
✅ Built catalog 'catalog.yaml' successfully

# JSON output
{
  "status": "success",
  "database": "analytics.duckdb",
  "views_created": 15,
  "attachments": 3,
  "build_time": "2.3s"
}
```

### validate

Validate configuration without building the catalog.

#### Syntax
```bash
duckalog validate [OPTIONS] CONFIG_PATH
```

#### Options
```bash
--format FORMAT
    Output format (text, json)
    
--verbose, -v
    Enable verbose logging
    
--filesystem fs
    Custom filesystem for remote configs
```

#### Examples
```bash
# Basic validation
duckalog validate catalog.yaml

# JSON output
duckalog validate catalog.yaml --format json

# Remote configuration
duckalog validate s3://bucket/config.yaml

# Verbose validation
duckalog validate catalog.yaml --verbose
```

#### Output
```bash
# Success
✅ Configuration 'catalog.yaml' is valid

# With warnings
⚠️  Warning: View 'users' has no description
✅ Configuration 'catalog.yaml' is valid

# JSON output
{
  "status": "valid",
  "warnings": [
    {
      "view": "users",
      "message": "No description provided"
    }
  ]
}

# Error
❌ Configuration 'catalog.yaml' is invalid:
  - Field required: version
  - Invalid YAML syntax at line 5
```

### generate-sql

Generate SQL statements without executing them.

#### Syntax
```bash
duckalog generate-sql [OPTIONS] CONFIG_PATH
```

#### Options
```bash
--output, -o FILE
    Output file for SQL (default: stdout)
    
--format FORMAT
    Output format (sql, json)
    
--verbose, -v
    Enable verbose logging
    
--filesystem fs
    Custom filesystem for remote configs
```

#### Examples
```bash
# Output to stdout
duckalog generate-sql catalog.yaml

# Save to file
duckalog generate-sql catalog.yaml --output create_views.sql

# JSON format
duckalog generate-sql catalog.yaml --format json --output views.json

# Remote configuration
duckalog generate-sql s3://bucket/config.yaml --output remote_views.sql
```

#### Output
```bash
# SQL output
-- Creating view: users
CREATE OR REPLACE VIEW "users" AS SELECT * FROM 'data/users.parquet';

-- Creating view: orders
CREATE OR REPLACE VIEW "orders" AS SELECT * FROM 'data/orders.parquet';

# JSON output
{
  "sql": [
    "CREATE OR REPLACE VIEW \"users\" AS SELECT * FROM 'data/users.parquet';",
    "CREATE OR REPLACE VIEW \"orders\" AS SELECT * FROM 'data/orders.parquet';"
  ]
}
```

### query

Execute SQL queries against a DuckDB catalog and display results in tabular format.

#### Syntax
```bash
duckalog query [OPTIONS] SQL
```

#### Arguments
```bash
SQL
    SQL query to execute against catalog (required)
```

#### Options
```bash
--catalog, -c TEXT
    Path to DuckDB catalog file (optional, defaults to catalog.duckdb in current directory)
    
--verbose, -v
    Enable verbose logging
```

#### Examples
```bash
# Query with implicit catalog discovery
duckalog query "SELECT COUNT(*) FROM users"

# Query with explicit catalog path
duckalog query "SELECT * FROM active_users LIMIT 5" --catalog catalog.duckdb
duckalog query "SELECT * FROM active_users LIMIT 5" -c analytics.duckdb

# Query with specific conditions
duckalog query "SELECT name, email FROM users WHERE active = true" --catalog analytics.duckdb

# Aggregate queries
duckalog query "SELECT status, COUNT(*) FROM orders GROUP BY status"

# Complex joins
duckalog query "SELECT u.name, o.amount FROM users u JOIN orders o ON u.id = o.user_id WHERE o.amount > 100" --catalog catalog.duckdb

# Remote catalog (with filesystem options)
duckalog query "SELECT * FROM products WHERE category = 'electronics'" --catalog s3://my-bucket/catalog.duckdb --fs-key AKIA... --fs-secret wJalr...
```

#### Arguments
```bash
CATALOG_PATH
    Path to DuckDB catalog file (optional, defaults to catalog.duckdb in current directory)
    
SQL
    SQL query to execute against the catalog (required)
```

#### Options
```bash
--verbose, -v
    Enable verbose logging
```

#### Examples
```bash
# Query with implicit catalog discovery
duckalog query "SELECT COUNT(*) FROM users"

# Query with explicit catalog path
duckalog query catalog.duckdb "SELECT * FROM active_users LIMIT 5"

# Query with specific conditions
duckalog query analytics.duckdb "SELECT name, email FROM users WHERE active = true"

# Aggregate queries
duckalog query "SELECT status, COUNT(*) FROM orders GROUP BY status"

# Complex joins
duckalog query "SELECT u.name, o.amount FROM users u JOIN orders o ON u.id = o.user_id WHERE o.amount > 100"

# Remote catalog (with filesystem options)
duckalog query s3://my-bucket/catalog.duckdb "SELECT * FROM products WHERE category = 'electronics'" --fs-key AKIA... --fs-secret wJalr...
```

#### Output
```bash
# Tabular results
+----+---------+-------------------+
| id | name    | email             |
+----+---------+-------------------+
| 1  | Alice   | alice@example.com |
| 2  | Bob     | bob@example.com   |
+----+---------+-------------------+

# No results
Query executed successfully. No rows returned.

# Error cases
Catalog file not found: nonexistent.duckdb
SQL error: Catalog Error: Table with name invalid_table does not exist!
```

#### Behavior
- **Read-only access**: Opens catalogs in read-only mode for safety
- **Automatic discovery**: Uses `catalog.duckdb` in current directory when no path provided
- **Tabular formatting**: Displays results in clean, readable table format
- **Error handling**: Provides clear error messages for missing catalogs and SQL errors
- **Exit codes**: Returns 0 on success, 2 for catalog errors, 3 for SQL errors

#### Use Cases
- **Data verification**: Quick checks of catalog contents and data quality
- **Debugging**: Verify views and data after building catalogs
- **Ad hoc analysis**: Run quick queries without external tools
- **Integration**: Use in scripts to extract specific data from catalogs

### show-imports

Display import graph and diagnostics for configuration with imports.

#### Syntax
```bash
duckalog show-imports [OPTIONS] CONFIG_PATH
```

#### Options
```bash
--diagnostics, -d
    Show import diagnostics
    
--show-merged
    Show fully merged configuration
    
--format FORMAT
    Output format (tree, json)
    
--verbose, -v
    Enable verbose logging
    
--filesystem fs
    Custom filesystem for remote configs
```

#### Examples
```bash
# Basic import tree
duckalog show-imports catalog.yaml

# With diagnostics
duckalog show-imports catalog.yaml --diagnostics

# Show merged configuration
duckalog show-imports catalog.yaml --show-merged

# JSON output
duckalog show-imports catalog.yaml --format json

# Remote configuration
duckalog show-imports s3://bucket/config.yaml --diagnostics
```

#### Output
```bash
# Tree format
catalog.yaml
├── ./base.yaml
├── ./views/
│   ├── users.yaml
│   └── orders.yaml
└── ./analytics.yaml

# Diagnostics
Import Graph Diagnostics:
- Total files: 5
- Import depth: 3 levels
- No circular imports detected
- No duplicate imports found
- Selective imports: 1 file with section-specific imports

# Merged configuration
{
  "version": 1,
  "duckdb": {
    "database": "analytics.duckdb",
    "pragmas": ["SET memory_limit='2GB'", "SET threads=4"]
  },
  "views": [...]
}
```

### init

Initialize a new Duckalog configuration file with educational examples.

#### Syntax
```bash
duckalog init [OPTIONS]
```

#### Options
```bash
--output, -o FILE
    Output file path (default: catalog.yaml)
    
--format FORMAT
    Configuration format (yaml, json)
    
--database, --database-name NAME
    Database name (default: catalog)
    
--project, --project-name NAME
    Project name for examples
    
--force, -f
    Overwrite existing file
    
--verbose, -v
    Enable verbose logging
```

#### Examples
```bash
# Basic initialization
duckalog init

# Custom filename and format
duckalog init --output my_config.json --format json

# With project and database names
duckalog init --project sales_analytics --database sales.db

# Force overwrite
duckalog init --force

# Verbose initialization
duckalog init --verbose
```

#### Output
```bash
# Success
✅ Created configuration file: catalog.yaml
📝 Database: catalog.duckdb
📊 Views: 3 example views
🔗 Attachments: 1 example attachment
💡 Tip: Edit the file to match your data sources

# File structure created
catalog.yaml
data/
├── users.parquet
├── orders.parquet
└── products.parquet
```

### ui

Start the Duckalog web dashboard for interactive catalog management with real-time capabilities.

#### Syntax
```bash
duckalog ui [OPTIONS] CONFIG_PATH
```

#### Architecture
The dashboard uses a modern stack for optimal performance and user experience:
- **Litestar Framework**: Modern async Python web framework with built-in security
- **Datastar.js Client-side**: Reactive UI framework for real-time updates without page refresh
- **Server-Sent Events**: Efficient real-time communication for query results and build status
- **Tailwind CSS**: Modern, responsive styling with dark/light theme support
- **Local-first**: All assets served locally, no external CDN dependencies

#### Options
```bash
--host HOST
    Bind to specific host (default: 127.0.0.1)

--port PORT
    Use specific port (default: 8787)

--row-limit NUM
    Limit ad-hoc query results (default: 500)

--db-path, --database-path PATH
    Override database path from configuration

--verbose, -v
    Enable verbose logging

--no-open
    Don't open browser automatically
```

#### Examples
```bash
# Basic dashboard with real-time features
duckalog ui catalog.yaml

# Custom host and port for team sharing
duckalog ui catalog.yaml --host 0.0.0.0 --port 8000

# With custom row limit for large datasets
duckalog ui catalog.yaml --row-limit 1000

# Production deployment with security
export DUCKALOG_ADMIN_TOKEN="your-secure-token"
duckalog ui catalog.yaml --host 0.0.0.0 --port 8000

# Development with verbose logging
duckalog ui catalog.yaml --verbose --row-limit 100
```

#### Features
**Real-time Capabilities:**
- Live query execution with streaming results
- Real-time build status updates without page refresh
- Reactive UI elements that update automatically
- Live loading indicators and error feedback

**Security Features:**
- Read-only SQL enforcement (blocks DDL/DML operations)
- Row limit protection to prevent resource exhaustion
- DuckDB read-only mode for additional database security
- Admin token authentication for production deployments

**User Experience:**
- Dark/light theme toggle with system preference detection
- Responsive design for mobile and desktop
- Progressive loading for large result sets
- Intuitive error messages and guidance

#### Output
```bash
# Success
🚀 Starting Duckalog dashboard...
🌐 Dashboard URL: http://127.0.0.1:8787
📊 Database: catalog.duckdb
👥 Views: 15
🔗 Attachments: 3
⚡ Real-time features enabled
💡 Press Ctrl+C to stop the server

# Production mode
🔐 Admin token authentication enabled
🌐 Dashboard URL: http://0.0.0.0:8000
🔑 Use admin token for mutating operations
🛡️ Security mode: read-only queries only
```

#### Dashboard Sections
The dashboard provides four main sections:

1. **Home**: Catalog overview with statistics and build management
2. **Views**: Browse and inspect catalog views with search functionality
3. **Query**: Ad-hoc SQL execution with real-time results streaming
4. **Semantic Layer**: Explore business-friendly semantic models

#### Performance Characteristics
- **Fast startup**: < 2 seconds to launch with configuration loading
- **Query streaming**: Results appear as they execute, no waiting
- **Memory efficient**: Row limits and connection pooling prevent resource issues
- **Responsive design**: Works on mobile, tablet, and desktop devices

## Remote Configuration Support

All commands support remote configuration files with these URI schemes:

### Supported URI Schemes
```bash
# Amazon S3
s3://bucket/path/config.yaml

# Google Cloud Storage
gs://bucket/path/config.yaml
gcs://bucket/path/config.yaml

# Azure Blob Storage
abfs://account@container/path/config.yaml

# SFTP/SSH
sftp://user@host/path/config.yaml

# HTTPS/HTTP
https://example.com/config.yaml
http://example.com/config.yaml
```

### Authentication

#### Environment Variables (Recommended)
```bash
# AWS S3
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-west-2

# Google Cloud Storage
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Azure Blob Storage
export AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;..."

# SFTP
export SFTP_HOST=server.com
export SFTP_USER=username
export SFTP_PASSWORD=password
```

#### Custom Filesystem
```python
import fsspec

# Create custom filesystem
fs = fsspec.filesystem(
    protocol="s3",
    key="your_access_key",
    secret="your_secret_key"
)

# Use with any command
duckalog build s3://bucket/config.yaml --filesystem fs
```

## Exit Codes

| Code | Meaning | Common Causes |
|-------|---------|---------------|
| 0 | Success | Command completed successfully |
| 1 | Configuration Error | Invalid YAML, missing fields, validation failed |
| 2 | File Not Found | Configuration file doesn't exist |
| 3 | Permission Error | Can't read configuration or write database |
| 4 | Database Error | DuckDB connection or execution failed |
| 5 | Network Error | Remote configuration download failed |
| 130 | Interrupted | User pressed Ctrl+C |

## Environment Variables

### Duckalog Configuration
```bash
# Log level
export DUCKALOG_LOG_LEVEL=DEBUG

# Disable colors
export DUCKALOG_NO_COLOR=1

# Custom config directory
export DUCKALOG_CONFIG_DIR=/path/to/configs
```

### DuckDB Integration
```bash
# These are used by DuckDB and can be set in Duckalog pragmas
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-west-2
export AZURE_STORAGE_CONNECTION_STRING="..."
export GCS_SERVICE_ACCOUNT_KEY=your_key
```

## Advanced Usage

### Command Chaining
```bash
# Validate then build
duckalog validate catalog.yaml && duckalog build catalog.yaml

# Generate SQL then review
duckalog generate-sql catalog.yaml --output review.sql && less review.sql

# Build with error handling
duckalog build catalog.yaml || echo "Build failed, check configuration"
```

### Batch Processing
```bash
# Process multiple configurations
for config in config1.yaml config2.yaml config3.yaml; do
  echo "Building $config..."
  duckalog build "$config" || echo "Failed to build $config"
done
```

### Integration with CI/CD

```yaml
# GitHub Actions
- name: Build Duckalog Catalog
  run: |
    duckalog build catalog.yaml --verbose
    duckalog validate catalog.yaml --format json

# Dockerfile
FROM python:3.12
RUN pip install duckalog
COPY catalog.yaml /app/
WORKDIR /app
CMD ["duckalog", "build", "catalog.yaml", "--verbose"]
```

## Performance Considerations

### Memory Usage
```bash
# Limit memory for large builds
duckalog build catalog.yaml --memory-limit '2GB'

# Monitor memory usage
/usr/bin/time -v duckalog build catalog.yaml
```

### Parallel Processing
```bash
# Control thread usage
duckalog build catalog.yaml --threads 2

# For multi-core systems
duckalog build catalog.yaml --threads $(nproc)
```

### I/O Optimization
```bash
# Reduce I/O for remote configs
duckalog build s3://bucket/config.yaml --filesystem cached_fs

# Use local caching
export DUCKALOG_CACHE_DIR=/tmp/duckalog_cache
```

## Troubleshooting

### Common Issues

#### Configuration Not Found
```bash
# Check file exists
ls -la catalog.yaml

# Use absolute path
duckalog build /full/path/to/catalog.yaml

# Check working directory
pwd
```

#### Permission Errors
```bash
# Check file permissions
ls -la catalog.yaml

# Fix permissions
chmod 644 catalog.yaml

# Check database directory permissions
ls -la $(dirname catalog.yaml)
```

#### Remote Configuration Issues
```bash
# Test remote access
curl -I s3://bucket/config.yaml

# Check credentials
aws s3 ls s3://bucket/

# Use verbose output for debugging
duckalog build s3://bucket/config.yaml --verbose
```

#### Database Lock Errors
```bash
# Find conflicting processes
lsof | grep duckdb

# Remove lock files
rm -f *.duckdb.wal *.duckdb.lock

# Use different database name
duckalog build catalog.yaml --db-path catalog_new.duckdb
```

## Best Practices

### Configuration Management
- **Use version control** for all configuration files
- **Environment-specific configs** for different deployment stages
- **Sensitive data in environment variables**, never in configuration files
- **Validate configurations** before deployment

### Performance Optimization
- **Set appropriate memory limits** based on available RAM and data size
- **Configure thread count** based on CPU cores and workload
- **Use remote configuration caching** for frequently accessed configs
- **Monitor resource usage** during builds

### Security
- **Use read-only database connections** where possible
- **Restrict dashboard access** in production with admin tokens
- **Rotate credentials regularly** and use environment variables
- **Audit configuration changes** and access logs

### CI/CD Integration
- **Fail fast** on configuration validation errors
- **Use specific versions** rather than latest for stability
- **Cache dependencies** for faster builds
- **Generate artifacts** for deployment and debugging

This comprehensive CLI reference covers all Duckalog commands and options for effective catalog management and automation.