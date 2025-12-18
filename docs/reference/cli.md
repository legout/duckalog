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
duckalog build catalog.yaml

# S3 with access key and secret
duckalog build s3://my-bucket/config.yaml --fs-key AKIA... --fs-secret wJalr...

# S3 with AWS profile
duckalog build s3://my-bucket/config.yaml --aws-profile my-profile

# GitHub with personal access token
duckalog build github://user/repo/config.yaml --fs-token ghp_xxxxxxxxxxxx

# Azure with connection string
duckalog build abfs://account@container/config.yaml --azure-connection-string "..."

# SFTP with key authentication
duckalog build sftp://server/config.yaml --sftp-host server.com --sftp-key-file ~/.ssh/id_rsa

# Anonymous S3 access (public bucket)
duckalog build s3://public-bucket/config.yaml --fs-anon
```

### Verbose Output

Verbose logging (`--verbose` or `-v` flag) provides detailed information about configuration loading and build process. This option is available on all commands and now includes enhanced diagnostics from the new architecture.

#### Configuration Loading
```bash
duckalog build catalog.yaml --verbose
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
duckalog build complex-catalog.yaml --verbose

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

### build

Build or update a DuckDB catalog from a config file or remote URI.

#### Syntax
```bash
duckalog build [OPTIONS] CONFIG_PATH
```

#### Options
```bash
--db-path PATH
    Override DuckDB database path. Supports local paths and remote URIs (s3://, gs://, gcs://, abfs://, adl://, sftp://).
    
--dry-run
    Generate SQL without executing against DuckDB.
    
--verbose, -v
    Enable verbose logging output.
    
--load-dotenv / --no-load-dotenv
    Enable/disable automatic .env file loading. (default: --load-dotenv)
```

#### Examples
```bash
# Local configuration file
duckalog build catalog.yaml

# With custom database path
duckalog build catalog.yaml --db-path analytics.duckdb

# Dry run to generate SQL
duckalog build catalog.yaml --dry-run

# Remote configuration with S3
duckalog build s3://my-bucket/config.yaml --fs-key AKIA... --fs-secret wJalr...

# Remote configuration with AWS profile
duckalog build s3://my-bucket/config.yaml --aws-profile my-profile

# Export catalog to remote storage
duckalog build config.yaml --db-path s3://my-bucket/catalog.duckdb
```

#### Output
```bash
# Success
Catalog build completed.

# Dry run SQL output
CREATE OR REPLACE VIEW "users" AS SELECT * FROM parquet_scan('data/users.parquet');
CREATE OR REPLACE VIEW "orders" AS SELECT * FROM parquet_scan('data/orders.parquet');
```

### validate

Validate a config file and report success or failure. Enhanced with new architecture diagnostics.

#### Syntax
```bash
duckalog validate [OPTIONS] CONFIG_PATH
```

#### Options
```bash
--format FORMAT
    Output format: text (default) or json for enhanced diagnostics
    
--diagnostics
    Show detailed loading and import resolution diagnostics
    
--cache-stats
    Show performance statistics for configuration loading
    
--verbose, -v
    Enable verbose logging output
```

#### Examples
```bash
# Basic validation
duckalog validate catalog.yaml

# Enhanced diagnostics
duckalog validate catalog.yaml --diagnostics

# JSON output with metrics
duckalog validate catalog.yaml --format json --cache-stats

# Remote configuration with diagnostics
duckalog validate s3://bucket/config.yaml --diagnostics
```

#### Output
```bash
# Basic validation
Config is valid.

# Enhanced diagnostics
✅ Configuration 'catalog.yaml' is valid

=== Loading Diagnostics ===
📁 Configuration file: catalog.yaml
🔄 Caching: Enabled (request-scoped)
📊 Load time: 0.089s
🔗 Import depth: 2 levels
📝 Views: 15, Attachments: 3

=== Import Resolution ===
├── ./base.yaml [cached]
├── ./shared/secrets.yaml [cached]
└── ./views/
    ├── users.yaml
    ├── orders.yaml
    └── analytics.yaml

# JSON output with metrics
{
  "status": "valid",
  "load_time_ms": 89,
  "cache_hits": 2,
  "cache_misses": 4,
  "import_depth": 2,
  "diagnostics": {
    "views": 15,
    "attachments": 3,
    "secrets": 2
  }
}
```

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

### Advanced Validation Options

The enhanced validation command leverages the new architecture for deeper insights:

#### Performance Analysis
```bash
# Analyze configuration loading performance
duckalog validate catalog.yaml --cache-stats --verbose

# Compare performance across runs
duckalog validate catalog.yaml --format json --cache-stats
```

#### Import Chain Analysis
```bash
# Show import resolution details
duckalog validate catalog.yaml --diagnostics --verbose

# Identify performance bottlenecks
duckalog validate catalog.yaml --diagnostics --cache-stats
```

#### Output Examples

**Performance Statistics:**
```bash
duckalog validate catalog.yaml --cache-stats

✅ Configuration is valid

=== Performance Statistics ===
⏱️  Total load time: 0.089s
💾 Cache hit ratio: 40% (2/5 files)
📊 Import depth: 3 levels
🔗 Files processed: 8 total
📝 SQL files loaded: 12
```

**JSON with Metrics:**
```bash
duckalog validate catalog.yaml --format json --cache-stats

{
  "status": "valid",
  "performance": {
    "load_time_ms": 89,
    "cache_hits": 2,
    "cache_misses": 3,
    "import_depth": 3,
    "files_processed": 8
  },
  "diagnostics": {
    "views": 15,
    "attachments": 3,
    "sql_files": 12
  }
}
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

### validate-paths

Validate config and check path accessibility.

#### Syntax
```bash
duckalog validate-paths [OPTIONS] CONFIG_PATH
```

#### Arguments
```bash
CONFIG_PATH
    Path to configuration file (must exist and be local)
```

#### Options
```bash
--verbose, -v
    Enable verbose logging output.
```

#### Examples
```bash
# Validate configuration and check paths
duckalog validate-paths catalog.yaml

# Verbose validation
duckalog validate-paths catalog.yaml --verbose
```

#### Output
```bash
✅ Configuration is valid.

Checking file accessibility...
--------------------------------------------------
✅ users: /path/to/config/data/users.parquet
❌ orders: File not found: /path/to/orders.parquet

❌ Found 1 inaccessible files:
  - orders: File not found
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
    
--database, --database-name NAME
    DuckDB database filename (default: analytics_catalog.duckdb)
    
--project, --project-name NAME
    Project name used in comments (default: my_analytics_project)
    
--force, -f
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
   3. Run 'duckalog build catalog.yaml' to create your catalog
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
    
--db-path TEXT
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

### init-env

Generate .env file templates for common use cases.

#### Syntax
```bash
duckalog init-env [OPTIONS]
```

#### Options
```bash
--template, -t TEMPLATE
    Template to use: basic, development, production, cloud, or custom (default: basic).
    
--output, -o FILE
    Output file path. Defaults to .env for basic template, or template-specific name for others.
    
--force, -f
    Overwrite existing files without prompting.
    
--verbose, -v
    Enable verbose output.
```

#### Templates
```bash
basic       - Basic .env file with common variables (default)
development - Development environment variables
production  - Production environment variables
cloud       - Cloud service configuration variables
```

#### Examples
```bash
# Generate basic .env template
duckalog init-env

# Generate development template
duckalog init-env --template development

# Generate production template with custom output
duckalog init-env --template production --output .env.production

# Force overwrite existing file
duckalog init-env --force
```

#### Output
```bash
✅ Created basic .env template: .env

Next steps:
   1. Edit .env and fill in your actual values
   2. Run 'duckalog build catalog.yaml' to test your configuration
   3. Add .env to your .gitignore file to avoid committing secrets
```

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
# Basic dashboard
duckalog ui catalog.yaml

# Custom host and port
duckalog ui catalog.yaml --host 0.0.0.0 --port 8000

# With row limit
duckalog ui catalog.yaml --row-limit 1000

# Production deployment
export DUCKALOG_ADMIN_TOKEN="your-secure-token"
duckalog ui catalog.yaml --host 0.0.0.0 --port 8000
```

#### Output
```bash
# Success
🚀 Starting Duckalog dashboard...
🌐 Dashboard URL: http://127.0.0.1:8787
📊 Database: catalog.duckdb
👥 Views: 15
🔗 Attachments: 3
💡 Press Ctrl+C to stop the server

# With admin token
🔐 Admin token authentication enabled
🌐 Dashboard URL: http://0.0.0.0:8000
🔑 Use admin token for mutating operations
```

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
duckalog build s3://bucket/config.yaml --fs-key AKIA... --fs-secret wJalr...

# Using AWS profile (recommended)
duckalog build s3://bucket/config.yaml --aws-profile my-profile

# Anonymous access (public buckets)
duckalog build s3://public-bucket/config.yaml --fs-anon
```

#### Google Cloud Storage
```bash
# Using service account file
duckalog build gs://bucket/config.yaml --gcs-credentials-file /path/to/creds.json

# Using application default credentials
duckalog build gs://bucket/config.yaml
```

#### Azure Blob Storage
```bash
# Using connection string
duckalog build abfs://account@container/config.yaml --azure-connection-string "..."

# Using account key and secret
duckalog build abfs://account@container/config.yaml --fs-key accountname --fs-secret accountkey
```

#### SFTP
```bash
# Using SSH key file
duckalog build sftp://server/config.yaml --sftp-host server.com --sftp-key-file ~/.ssh/id_rsa

# Using password authentication
duckalog build sftp://server/config.yaml --sftp-host server.com --fs-key username --fs-secret password
```

#### GitHub
```bash
# Using personal access token
duckalog build github://user/repo/config.yaml --fs-token ghp_xxxxxxxxxxxx
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

duckalog validate base.yaml --diagnostics
duckalog validate analytics.yaml --diagnostics  # Reuses base imports
duckalog validate reports.yaml --diagnostics    # Reuses common imports
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
duckalog build catalog.yaml

# Gradually adopt new features
duckalog validate catalog.yaml --diagnostics
duckalog build catalog.yaml --verbose  # Enhanced diagnostics

# Use advanced features for complex scenarios
duckalog validate complex-catalog.yaml --diagnostics --cache-stats
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
- **Monitor performance**: Use `--diagnostics` and `--cache-stats` for insights
- **Optimize imports**: Structure imports for efficient resolution
- **Use verbose output** for troubleshooting complex configurations

### Security
- **Use read-only database connections** where possible
- **Restrict dashboard access** in production environments
- **Keep credentials secure**: Use AWS profiles, service account files, or environment variables
- **Never commit credentials** to version control
- **Use authentication** consistently across remote configurations

### Advanced Usage
- **Complex configurations**: Use `--diagnostics` to understand import chains
- **Performance tuning**: Monitor cache statistics and load times
- **Batch operations**: Run multiple related operations together
- **Error handling**: Use enhanced output for faster problem resolution

This CLI reference covers all available Duckalog commands for effective catalog management, with enhanced features from the new modular architecture.