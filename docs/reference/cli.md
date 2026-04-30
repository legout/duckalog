# CLI Reference

Complete reference for all Duckalog command-line interface commands, options, and usage patterns.

## Overview

Duckalog provides a comprehensive CLI for building, validating, and managing DuckDB catalogs. The CLI now supports the new modular architecture with enhanced configuration loading, dependency injection, and performance optimization features.

### New Architecture Features

The CLI has been enhanced to support:

- **Enhanced Configuration Loading**: Support for dependency injection and custom resolvers
- **Request-Scoped Caching**: Performance optimization for batch operations
- **Improved Error Reporting**: Better context and diagnostic information
- **Backward Compatibility**: All existing commands continue to work unchanged

All commands support filesystem options for remote configuration access and the new architecture features.

## Global Options

These options are available for all commands and are handled by the main callback:

### Help and Version
```bash
# Show help
duckalog --help
duckalog <command> --help

# Show version
duckalog version
```

### Remote Filesystem Options

All commands support these filesystem options for accessing remote configuration files:

```bash
# Protocol and authentication
--fs-protocol TEXT          Remote filesystem protocol: s3 (AWS), gcs (Google), abfs (Azure), sftp, github
--fs-key TEXT              API key, access key, or username for authentication
--fs-secret TEXT            Secret key, password, or token for authentication  
--fs-token TEXT             Authentication token for services like GitHub personal access tokens
--fs-anon                   Use anonymous access (no authentication required)

# Connection settings
--fs-timeout INTEGER        Connection timeout in seconds (default: 30)

# Provider-specific options
--aws-profile TEXT          AWS profile name for S3 authentication (overrides --fs-key/--fs-secret)
--gcs-credentials-file TEXT  Path to Google Cloud service account credentials JSON file
--azure-connection-string TEXT  Azure storage connection string (overrides --fs-key/--fs-secret for Azure)
--sftp-host TEXT           SFTP server hostname (required for SFTP protocol)
--sftp-port INTEGER        SFTP server port (default: 22)
--sftp-key-file TEXT       Path to SSH private key file for SFTP authentication
```

### Usage Examples
```bash
# Local configuration file
duckalog run catalog.yaml

# S3 with access key and secret
duckalog run s3://my-bucket/config.yaml --fs-key AKIA... --fs-secret wJalr...

# S3 with AWS profile
duckalog run s3://my-bucket/config.yaml --aws-profile my-profile

# GitHub with personal access token
duckalog run github://user/repo/config.yaml --fs-token ghp_xxxxxxxxxxxx

# Azure with connection string
duckalog run abfs://account@container/config.yaml --azure-connection-string "..."

# SFTP with key authentication
duckalog run sftp://server/config.yaml --sftp-host server.com --sftp-key-file ~/.ssh/id_rsa

# Anonymous S3 access (public bucket)
duckalog run s3://public-bucket/config.yaml --fs-anon
```

### Verbose Output

Verbose logging (`--verbose` or `-v` flag) provides detailed information about configuration loading and build process. This option is available on all commands and now includes enhanced diagnostics from the new architecture.

#### Configuration Loading
```bash
duckalog run catalog.yaml --verbose
```

**Shows:**
- Configuration file being processed
- Remote filesystem access details
- Environment variable resolution
- Import file processing (if any)
- SQL file loading and inlining
- **New**: Request-scoped cache utilization
- **New**: Dependency injection diagnostics
- **New**: Import resolution performance metrics

#### Enhanced Error Diagnosis

Verbose output now provides richer diagnostic information:
- Missing environment variables with context
- Remote authentication issues with detailed errors
- Configuration syntax errors with line numbers
- Import resolution problems with dependency chains
- SQL file loading failures with path resolution details
- **New**: Cache hit/miss statistics
- **New**: Import chain visualization
- **New**: Performance timing for each loading phase

#### Example Enhanced Output
```bash
duckalog run complex-catalog.yaml --verbose

=== Configuration Loading Diagnostics ===
📁 Loading: complex-catalog.yaml
🔄 Using request-scoped caching
⚡ Import cache hits: 3/5 files
📊 Resolution time: 0.142s
🔗 Import chain depth: 3 levels
📝 SQL files processed: 12

=== Import Resolution Details ===
complex-catalog.yaml
├── ./base.yaml [cached ✓]
├── ./shared/common.yaml [cached ✓] 
└── ./views/
    ├── analytics.yaml [loaded fresh]
    └── reports.yaml [loaded fresh]

=== Performance Metrics ===
- Config parsing: 0.023s
- Import resolution: 0.089s (with caching)
- SQL file loading: 0.030s
- Total load time: 0.142s
```

## Commands

### run - NEW: Primary Command

Connect, build, and query a DuckDB catalog using intelligent connection management. This is the new recommended primary workflow.

#### Syntax
```bash
duckalog run [OPTIONS] CONFIG_PATH
```

#### Options
```bash
--query TEXT
    Execute SQL query directly and exit. If not provided, starts interactive mode.
    
--force-rebuild
    Force rebuild all views instead of incremental updates.
    
--interactive
    Start interactive SQL shell with catalog ready (default behavior when --query not provided).
    
--db-path PATH
    Override DuckDB database path. Supports local paths and remote URIs (s3://, gs://, gcs://, abfs://, adl://, sftp://).
    
--verbose, -v
    Enable verbose logging output.
    
--load-dotenv / --no-load-dotenv
    Enable/disable automatic .env file loading. (default: --load-dotenv)
```

#### Examples
```bash
# Basic usage - connect and start interactive shell
duckalog run catalog.yaml

# Direct query execution
duckalog run catalog.yaml --query "SELECT COUNT(*) FROM users"

# Interactive mode with remote configuration
duckalog run s3://my-bucket/catalog.yaml --interactive

# Force rebuild all views
duckalog run catalog.yaml --force-rebuild

# Query with custom database path
duckalog run catalog.yaml --query "SELECT * FROM analytics" --db-path analytics.duckdb

# Remote configuration with authentication
duckalog run s3://my-bucket/catalog.yaml --fs-key AKIA... --fs-secret wJalr...
```

#### Output
```bash
# Interactive mode
🔗 Connected to catalog: catalog.duckdb
📊 15 views created (3 new, 12 cached)
💬 Starting interactive SQL shell...
Type 'exit' to quit, 'help' for available commands

catalog> SELECT COUNT(*) FROM users;
┌──────────────┐
│ count_star() │
├──────────────┤
│         1250 │
└──────────────┘

# Query mode
+----+---------+-------------------+
| id | name    | email             |
+----+---------+-------------------+
| 1  | Alice   | alice@example.com |
| 2  | Bob     | bob@example.com   |
+----+---------+-------------------+
```

#### Key Features
- **Smart Connection Management**: Automatic connection pooling and reuse
- **Session State Restoration**: Pragmas, settings, and attachments are automatically restored
- **Incremental Updates**: Only missing views are created for faster builds
- **Lazy Connections**: Database connections established only when needed
- **Remote Configuration Support**: Works with all remote filesystem options

### validate

Validate a config file and report success or failure.

#### Syntax
```bash
duckalog validate [OPTIONS] CONFIG_PATH
```

#### Options
```bash
--verbose, -v
    Enable verbose logging output.
```

#### Examples
```bash
# Basic validation
duckalog validate catalog.yaml

# Remote configuration
duckalog validate s3://bucket/config.yaml

# Verbose validation
duckalog validate catalog.yaml --verbose
```

#### Output
```bash
# Success
Config is valid.

# Error
Config error: [specific error message]
```

### generate-sql

Validate config and emit CREATE VIEW SQL only.

#### Syntax
```bash
duckalog generate-sql [OPTIONS] CONFIG_PATH
```

#### Options
```bash
--output, -o FILE
    Write SQL output to file instead of stdout.
    
--verbose, -v
    Enable verbose logging output.
```

#### Examples
```bash
# Output to stdout
duckalog generate-sql catalog.yaml

# Save to file
duckalog generate-sql catalog.yaml --output create_views.sql

# Remote configuration
duckalog generate-sql s3://bucket/config.yaml --output remote_views.sql
```

#### Output
```bash
# SQL output to stdout
CREATE OR REPLACE VIEW "users" AS SELECT * FROM parquet_scan('data/users.parquet');
CREATE OR REPLACE VIEW "orders" AS SELECT * FROM parquet_scan('data/orders.parquet');

# File output confirmation (when using --output)
Wrote SQL to create_views.sql
```

### show-paths

Show resolved paths for a configuration file.

#### Syntax
```bash
duckalog show-paths [OPTIONS] CONFIG_PATH
```

#### Arguments
```bash
CONFIG_PATH
    Path to configuration file (must exist and be local)
```

#### Options
```bash
--check, -c
    Check if files are accessible.
    
--verbose, -v
    Enable verbose logging output.
```

#### Examples
```bash
# Show path resolution
duckalog show-paths catalog.yaml

# Check file accessibility
duckalog show-paths catalog.yaml --check

# Verbose output
duckalog show-paths catalog.yaml --verbose
```

#### Output
```bash
Configuration: catalog.yaml
Config directory: /path/to/config

View Paths:
--------------------------------------------------------------------------------
users:
  Original: data/users.parquet
  Resolved: /path/to/config/data/users.parquet
  Status: ✅ Accessible

orders:
  Original: ../shared/orders.parquet  
  Resolved: /path/to/../shared/orders.parquet
  Status: ❌ File not found
```


Execute SQL queries against an existing DuckDB catalog and display results in tabular format. **Note**: You can also run queries via `duckalog run CONFIG_PATH --query "SQL"`.

#### Syntax
```bash
duckalog query [OPTIONS] SQL
```

#### Arguments
```bash
SQL
    SQL query to execute against catalog.
```

#### Options
```bash
--catalog, -c TEXT
    Path to DuckDB catalog file (optional, defaults to catalog.duckdb in current directory).
    
--verbose, -v
    Enable verbose logging output.
```

#### Examples
```bash
# Query with implicit catalog discovery
duckalog query "SELECT COUNT(*) FROM users"

# Query with explicit catalog path
duckalog query "SELECT * FROM users" --catalog catalog.duckdb
duckalog query "SELECT * FROM users" -c analytics.duckdb

# Query a remote catalog (if filesystem options are configured)
duckalog query "SELECT name, email FROM users WHERE active = true" --catalog s3://my-bucket/catalog.duckdb

# Alternative: Use new 'run' command for config-driven queries
duckalog run catalog.yaml --query "SELECT * FROM users"
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
Columns: id, name, email

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

#### When to Use `query` vs `run`

```bash
# Use 'query' for existing databases
duckalog query "SELECT * FROM users" --catalog existing_catalog.duckdb

# Use 'run' for config-driven workflows (recommended)
duckalog run config.yaml --query "SELECT * FROM users"

# Use 'run' for interactive sessions with config
duckalog run config.yaml --interactive
```

**Key Differences:**
- `query`: Works with existing `.duckdb` files directly
- `run`: Builds catalog from config, manages connections, and queries in one workflow
- `run`: Supports incremental updates and session restoration
- `query`: Simpler for quick database queries without configuration

### show-imports

Show import graph for a configuration file.

#### Syntax
```bash
duckalog show-imports [OPTIONS] CONFIG_PATH
```

#### Options
```bash
--show-merged
    Also display fully merged configuration after imports are resolved.
    
--format FORMAT
    Output format: tree or json (default: tree)
    
--diagnostics
    Show import diagnostics (depth, duplicates, performance metrics).
    
--verbose, -v
    Enable verbose logging output.
```

#### Examples
```bash
# Basic import tree
duckalog show-imports catalog.yaml

# With diagnostics
duckalog show-imports catalog.yaml --diagnostics

# Show merged configuration
duckalog show-imports catalog.yaml --show-merged

# Export import graph as JSON
duckalog show-imports catalog.yaml --format json

# Remote configuration
duckalog show-imports s3://bucket/config.yaml --diagnostics
```

#### Output
```bash
# Tree format
Import Graph:
================================================================================
catalog.yaml
├── ./base.yaml
├── ./views/
│   ├── users.yaml
│   └── orders.yaml
└── ./analytics.yaml

Total files in import graph: 5

# With diagnostics
Import Diagnostics:
--------------------------------------------------------------------------------
  Total files: 5
  Maximum import depth: 3
  Files with imports: 4
  Remote imports: 1
  Local imports: 3
  Duplicate imports: [shared.yaml]

# JSON output
{
  "import_chain": ["catalog.yaml", "./base.yaml", "./views/users.yaml"],
  "import_graph": {
    "catalog.yaml": ["./base.yaml", "./views/users.yaml"],
    "./base.yaml": []
  },
  "total_files": 5
}
```

### init

Initialize a new Duckalog configuration file.

#### Syntax
```bash
duckalog init [OPTIONS]
```

#### Options
```bash
--output, -o FILE
    Output file path. Defaults to catalog.yaml or catalog.json based on format.
    
--format FORMAT
    Output format: yaml or json (default: yaml)
    
--database, -d TEXT
    DuckDB database filename (default: analytics_catalog.duckdb)
    
--project, -p TEXT
    Project name used in comments (default: my_analytics_project)
    
--force
    Overwrite existing file without prompting.
    
--skip-existing
    Skip file creation if it already exists.
    
--verbose, -v
    Enable verbose logging output.
```

#### Examples
```bash
# Create a basic YAML config
duckalog init

# Create a JSON config with custom filename
duckalog init --format json --output my_config.json

# Create with custom database and project names
duckalog init --database sales.db --project sales_analytics

# Force overwrite existing file
duckalog init --force

# Verbose initialization
duckalog init --verbose
```

#### Output
```bash
# Success
✅ Created Duckalog configuration: catalog.yaml (default filename)
📁 Path: /path/to/catalog.yaml
📄 Format: YAML
💾 Database: analytics_catalog.duckdb

# With verbose output
🔧 Next steps:
   1. Edit catalog.yaml to customize views and data sources
   2. Run 'duckalog validate catalog.yaml' to check your configuration
   3. Run 'duckalog run catalog.yaml' to create your catalog
```

#### Options
```bash
--output, -o FILE
    Output file path. Defaults to catalog.yaml or catalog.json based on format.
    
--format, -f TEXT
    Output format: yaml or json (default: yaml)
    
--database, -d TEXT
    DuckDB database filename (default: analytics_catalog.duckdb)
    
--project, -p TEXT
    Project name used in comments (default: my_analytics_project)
    
--force
    Overwrite existing file without prompting.
    
--skip-existing
    Skip file creation if it already exists.
    
--verbose, -v
    Enable verbose logging output.
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

Launch local dashboard for a catalog.

#### Syntax
```bash
duckalog ui [OPTIONS] CONFIG_PATH
```

#### Arguments
```bash
CONFIG_PATH
    Path to configuration file (local or remote).
```

#### Options
```bash
--host HOST
    Host to bind (default: loopback).
    
--port PORT
    Port to bind (default: 8787).
    
--row-limit NUM
    Max rows to show in query results.
    
--db TEXT
    Path to DuckDB database file (optional).
    
--verbose, -v
    Enable verbose logging output.
```

#### Examples
```bash
# Basic usage with config file
duckalog ui config.yaml

# Specify a custom host and port
duckalog ui config.yaml --host 0.0.0.0 --port 8080

# Use with an existing database file
duckalog ui config.yaml --db catalog.duckdb
```

#### Output
```bash
Starting dashboard at http://127.0.0.1:8787
Warning: binding to a non-loopback host may expose dashboard to others on your network.
```


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
duckalog run s3://bucket/config.yaml --filesystem fs
```

## Remote Configuration Support

All commands support remote configuration files and databases using the global filesystem options. Common URI schemes:

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

# GitHub (for remote configs)
github://user/repo/config.yaml
```

### Authentication Patterns

#### AWS S3
```bash
# Using access keys
duckalog run s3://bucket/config.yaml --fs-key AKIA... --fs-secret wJalr...

# Using AWS profile (recommended)
duckalog run s3://bucket/config.yaml --aws-profile my-profile

# Anonymous access (public buckets)
duckalog run s3://public-bucket/config.yaml --fs-anon
```

#### Google Cloud Storage
```bash
# Using service account file
duckalog run gs://bucket/config.yaml --gcs-credentials-file /path/to/creds.json

# Using application default credentials
duckalog run gs://bucket/config.yaml
```

#### Azure Blob Storage
```bash
# Using connection string
duckalog run abfs://account@container/config.yaml --azure-connection-string "..."

# Using account key and secret
duckalog run abfs://account@container/config.yaml --fs-key accountname --fs-secret accountkey
```

#### SFTP
```bash
# Using SSH key file
duckalog run sftp://server/config.yaml --sftp-host server.com --sftp-key-file ~/.ssh/id_rsa

# Using password authentication
duckalog run sftp://server/config.yaml --sftp-host server.com --fs-key username --fs-secret password
```

#### GitHub
```bash
# Using personal access token
duckalog run github://user/repo/config.yaml --fs-token ghp_xxxxxxxxxxxx
```

## Error Handling and Exit Codes

Commands use these exit codes:
- `0` - Success
- `1` - Unexpected error
- `2` - Configuration/file not found
- `3` - Database/SQL error  
- `4` - Filesystem/authentication error

## Environment Variables

Duckalog automatically discovers and loads `.env` files in the configuration directory and parent directories. No special environment variables are required for basic operation.

## Advanced Features and Patterns

### Dependency Injection in CLI Context

The CLI now supports advanced configuration patterns through the underlying architecture:

#### Custom Filesystem Integration
```bash
# Use with custom filesystem (Python API pattern)
# While CLI doesn't directly expose DI, it uses the same enhanced loading

# The CLI benefits from:
# - Request-scoped caching for multiple operations
# - Enhanced error reporting with context
# - Performance optimizations for complex configurations
# - Better import resolution diagnostics
```

#### Batch Operations with Caching
```bash
# Multiple commands benefit from shared internal caching
# When processing multiple related files:

duckalog show-imports base.yaml --diagnostics
duckalog show-imports analytics.yaml --diagnostics  # Reuses base imports
duckalog show-imports reports.yaml --diagnostics    # Reuses common imports
```

### Performance Optimization Features

#### Configuration Caching
The CLI automatically uses request-scoped caching for:
- Import resolution across related configurations
- Environment variable resolution
- Path normalization and security checks
- SQL file loading and template processing

#### Diagnostic Capabilities
Enhanced diagnostics provide insights into:
- **Import Chain Analysis**: Visualize configuration dependencies
- **Performance Profiling**: Identify slow-loading components
- **Cache Utilization**: Optimize for repeated operations
- **Error Context**: Rich error information with resolution suggestions

### Migration and Compatibility

#### Backward Compatibility
- All existing CLI commands work unchanged
- All existing options and flags preserved
- No breaking changes to command syntax
- Enhanced output is additive, not destructive

#### Gradual Feature Adoption
```bash
# Continue using existing patterns
duckalog run catalog.yaml

# Use verbose output for diagnostics
duckalog run catalog.yaml --verbose

duckalog show-imports catalog.yaml --diagnostics
```

## Best Practices

### Configuration Management
- **Use version control** for all configuration files
- **Environment-specific configs** for different deployment stages
- **Sensitive data in environment variables**, never in configuration files
- **Validate configurations** before deployment
- **Use diagnostic flags** for complex configurations to understand performance

### Performance Optimization
- **Leverage caching**: Run multiple operations together for cache benefits
- **Monitor performance**: Use verbose output (`--verbose`) for insights
- **Optimize imports**: Structure imports for efficient resolution
- **Use verbose output** for troubleshooting complex configurations

### Security
- **Use read-only database connections** where possible
- **Restrict dashboard access** in production environments
- **Keep credentials secure**: Use AWS profiles, service account files, or environment variables
- **Never commit credentials** to version control
- **Use authentication** consistently across remote configurations

### Advanced Usage
- **Complex configurations**: Use `show-imports --diagnostics` to understand import chains
- **Performance tuning**: Monitor cache statistics and load times
- **Batch operations**: Run multiple related operations together
- **Error handling**: Use enhanced output for faster problem resolution

This CLI reference covers all available Duckalog commands for effective catalog management, with enhanced features from the new modular architecture.