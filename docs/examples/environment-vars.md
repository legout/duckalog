# Environment Variables and .env Files Example

This example demonstrates how to use environment variables and `.env` files effectively in Duckalog configurations. You'll learn security best practices, automatic `.env` file loading, environment-specific configurations, and credential management patterns that keep your configs portable and secure.

## When to Use This Example

Choose this example if:
- You need to keep credentials out of configuration files
- You want automatic `.env` file loading for local development
- You need different configs for development, staging, and production
- You're deploying Duckalog across multiple environments
- You need to comply with security policies (no hardcoded secrets)
- You want to make configs

## Prerequisites reusable across different setups

1. **Duckalog installed:**
   ```bash
   pip install duckalog
   ```

2. **Basic understanding of environment variables and .env files:**
   ```bash
   # Check if a variable exists
   echo $AWS_ACCESS_KEY_ID
   
   # Set a variable
   export DATABASE_PASSWORD="my-secret-password"
   
   # Create a .env file
   echo "API_KEY=secret123" > .env
   echo "DATABASE_URL=postgres://localhost/mydb" >> .env
   
   # Load .env file (optional - Duckalog loads automatically)
   source .env
   ```

## Environment Variable Syntax

Duckalog supports environment variable interpolation using the `${env:VAR_NAME}` syntax:

```yaml
# Basic syntax
some_field: "${env:VARIABLE_NAME}"

# With default values (Duckalog specific feature)
some_field: "${env:VARIABLE_NAME:default_value}"

# Nested references
config:
  host: "${env:DB_HOST}"
  connection_string: "postgresql://${env:DB_USER}:${env:DB_PASSWORD}@${env:DB_HOST}:${env:DB_PORT}/${env:DB_NAME}"
```

**Important Notes:**
- Variable names are case-sensitive
- Undefined variables will cause validation errors (unless default is provided)
- Variables are resolved during configuration loading
- No quotes needed around the `${env:...}` syntax
- `.env` files are automatically discovered and loaded

## Automatic .env File Loading

Duckalog now includes automatic `.env` file discovery and loading:

### How It Works

1. **Automatic Discovery**: When loading any configuration file, Duckalog automatically searches for `.env` files
2. **Hierarchical Search**: Searches from the config file directory upward (up to 10 levels)
3. **No Configuration Needed**: Works automatically without any setup
4. **Secure Handling**: Sensitive data is never logged, malformed files are handled gracefully

### Creating .env Files

```bash
# Basic .env file
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
DATABASE_PASSWORD=dev-password
ENVIRONMENT=development

# Comments and empty lines are supported
# This is a comment
API_KEY=secret123

EMPTY_VAR=
NORMAL_VAR=normal_value
```

### .env File Format

- **Key-Value Pairs**: `KEY=value` or `KEY="value"`
- **Comments**: Lines starting with `#`
- **Empty Lines**: Ignored
- **Inline Comments**: Supported with `#`
- **Quoted Values**: Both single and double quotes supported
- **Special Characters**: Handled properly in quoted values

```bash
# Example .env with various formats
DATABASE_URL="postgresql://user:pass@localhost:5432/db"
MESSAGE=Hello World
JSON_DATA='{"key": "value"}'
# Comment line
API_KEY=secret123  # inline comment
EMPTY_KEY=
```

### Using .env Files

**Step 1: Create .env file**
```bash
cat > .env << EOF
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
DATABASE_URL=postgres://localhost:5432/mydb
ENVIRONMENT=development
EOF
```

**Step 2: Use in configuration**
```yaml
# catalog.yaml - variables automatically available from .env
version: 1
duckdb:
  database: "${env:DATABASE_URL}.duckdb"
  pragmas:
    - "SET s3_access_key_id='${env:AWS_ACCESS_KEY_ID}'"
    - "SET s3_secret_access_key='${env:AWS_SECRET_ACCESS_KEY}'"

attachments:
  postgres:
    - alias: main_db
      host: "${env:DB_HOST:localhost}"
      port: 5432
      database: "${env:DB_NAME:mydb}"
      user: "${env:DB_USER:user}"
      password: "${env:DB_PASSWORD:pass}"

views:
  - name: data_view
    source: postgres
    database: main_db
    table: users
    description: "View using .env variables"
```

**Step 3: Use with Duckalog**
```bash
# No need to manually load .env - it's automatic!
duckalog build catalog.yaml

# Check verbose output to see .env loading
duckalog build catalog.yaml --verbose
```

### .env File Discovery Examples

**Example 1: Simple directory structure**
```
my-project/
├── .env              # ← Found and loaded
└── catalog.yaml
```

**Example 2: Nested configuration**
```
my-project/
├── .env              # ← Found and loaded
├── configs/
│   ├── catalog.yaml  # ← Uses parent .env
│   └── subdir/
│       └── config.yaml # ← Also uses parent .env
└── data/
```

**Example 3: Multiple .env files (closest wins)**
```
project/
├── .env                 # ← Loaded if no closer .env exists
├── subdir/
│   ├── .env             # ← Loaded first (highest priority)
│   └── config.yaml      # ← Uses subdir/.env
└── another-level/
    └── config.yaml      # ← Uses project/.env
```

## Security Best Practices

### 1. Never Commit Secrets

**❌ Wrong - Don't do this:**
```yaml
# This config file should NEVER be committed to version control
duckdb:
  pragmas:
    - "SET s3_access_key_id='AKIA...'"  # Hardcoded credentials
    - "SET s3_secret_access_key='real-secret-key'"
postgres:
  password: "super-secret-password"      # Hardcoded password
```

**✅ Correct - Use environment variables or .env files:**
```yaml
# This config file is safe to commit
duckdb:
  pragmas:
    - "SET s3_access_key_id='${env:AWS_ACCESS_KEY_ID}'"
    - "SET s3_secret_access_key='${env:AWS_SECRET_ACCESS_KEY}'"
postgres:
  password: "${env:DATABASE_PASSWORD}"
```

### 2. Use `.gitignore`

Create a `.gitignore` file to prevent accidentally committing sensitive files:

```gitignore
# Environment files
.env
.env.local
.env.production
.env.development

# Generated catalogs
*.duckdb
*.db

# Logs
*.log

# Temporary files
tmp/
temp/
```

### 3. Environment-Specific .env Files

Use different `.env` files for different environments:

```bash
# .env.development (for local development)
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
DATABASE_PASSWORD=dev-password
ENVIRONMENT=development

# .env.production (for production deployment)
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
DATABASE_PASSWORD=production-password
ENVIRONMENT=production

# Load specific environment
source .env.development  # for development
source .env.production   # for production
```

### 4. .env File Security

- **Keep .env files out of version control** - Always add to `.gitignore`
- **Use descriptive names** - `.env.local`, `.env.staging`, `.env.production`
- **Limit file permissions** - `chmod 600 .env` on Unix systems
- **Regular rotation** - Update secrets regularly
- **Environment isolation** - Different .env files for different environments

```bash
# Secure .env file handling
chmod 600 .env                    # Read/write for owner only
echo ".env" >> .gitignore         # Never commit
echo ".env.*" >> .gitignore       # Never commit any .env variants
```

## Basic Environment Configuration

### Development Configuration

Create `config-development.yaml`:

```yaml
version: 1

duckdb:
  database: dev_catalog.duckdb
  pragmas:
    # Development settings - less restrictive
    - "SET memory_limit='512MB'"
    - "SET threads=2"
    - "SET search_path='public'"

# Development database (local or dev environment)
attachments:
  postgres:
    - alias: dev_db
      host: "${env:DEV_DB_HOST:localhost}"
      port: 5432
      database: "${env:DEV_DB_NAME:analytics_dev}"
      user: "${env:DEV_DB_USER:dev_user}"
      password: "${env:DEV_DB_PASSWORD:dev_password}"

# S3 development bucket
views:
  - name: dev_data
    source: parquet
    uri: "s3://${env:DEV_S3_BUCKET:my-dev-bucket}/data/*.parquet"
```

### Production Configuration

Create `config-production.yaml`:

```yaml
version: 1

duckdb:
  database: prod_catalog.duckdb
  pragmas:
    # Production settings - more restrictive and performant
    - "SET memory_limit='8GB'"
    - "SET threads=8"
    - "SET temp_directory='/tmp/duckdb_temp'"
    
    # Cloud storage for production
    - "SET s3_region='${env:AWS_REGION:us-east-1}'"
    - "SET s3_access_key_id='${env:AWS_ACCESS_KEY_ID}'"
    - "SET s3_secret_access_key='${env:AWS_SECRET_ACCESS_KEY}'"
    - "SET s3_session_token='${env:AWS_SESSION_TOKEN}'"

# Production databases
attachments:
  postgres:
    - alias: prod_db
      host: "${env:PROD_DB_HOST}"
      port: 5432
      database: "${env:PROD_DB_NAME}"
      user: "${env:PROD_DB_USER}"
      password: "${env:PROD_DB_PASSWORD}"
      sslmode: require

# Production data sources
views:
  - name: production_data
    source: parquet
    uri: "s3://${env:PROD_S3_BUCKET}/data/*.parquet"
    
  - name: prod_metrics
    sql: |
      SELECT 
        DATE(created_at) as metric_date,
        COUNT(*) as total_records,
        AVG(value) as avg_value
      FROM production_data
      GROUP BY DATE(created_at)
      ORDER BY metric_date DESC
```

## Common Environment Variable Patterns

### 1. AWS and Cloud Configuration

```yaml
# AWS credentials and region
duckdb:
  pragmas:
    - "SET s3_region='${env:AWS_REGION:us-east-1}'"
    - "SET s3_access_key_id='${env:AWS_ACCESS_KEY_ID}'"
    - "SET s3_secret_access_key='${env:AWS_SECRET_ACCESS_KEY}'"
    - "SET s3_session_token='${env:AWS_SESSION_TOKEN}'"

# S3 buckets by environment
views:
  - name: events
    source: parquet
    uri: "s3://${env:S3_BUCKET_PREFIX}-events/${env:ENVIRONMENT:dev}/data/*.parquet"
```

**Required environment variables:**
```bash
export AWS_REGION="us-west-2"
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_SESSION_TOKEN="..."  # For temporary credentials
export S3_BUCKET_PREFIX="company"
export ENVIRONMENT="prod"
```

### 2. Database Connections

```yaml
attachments:
  postgres:
    - alias: primary
      host: "${env:DB_HOST}"
      port: "${env:DB_PORT:5432}"
      database: "${env:DB_NAME}"
      user: "${env:DB_USER}"
      password: "${env:DB_PASSWORD}"
      sslmode: "${env:DB_SSL_MODE:require}"
      
  - alias: analytics
      host: "${env:ANALYTICS_DB_HOST}"
      port: 5432
      database: "${env:ANALYTICS_DB_NAME}"
      user: "${env:ANALYTICS_DB_USER}"
      password: "${env:ANALYTICS_DB_PASSWORD}"

  duckdb:
    - alias: reference
      path: "${env:REFERENCE_DB_PATH:./reference.duckdb}"
      read_only: true
```

**Database environment variables:**
```bash
export DB_HOST="prod-db.example.com"
export DB_PORT="5432"
export DB_NAME="analytics"
export DB_USER="analytics_user"
export DB_PASSWORD="secure_password"
export DB_SSL_MODE="require"

export ANALYTICS_DB_HOST="analytics-db.example.com"
export ANALYTICS_DB_NAME="analytics_warehouse"
export ANALYTICS_DB_USER="warehouse_user"
export ANALYTICS_DB_PASSWORD="warehouse_password"

export REFERENCE_DB_PATH="/data/reference.duckdb"
```

### 3. Iceberg and Data Lake Configuration

```yaml
iceberg_catalogs:
  - name: production_catalog
    catalog_type: rest
    uri: "${env:ICEBERG_URI}"
    warehouse: "s3://${env:ICEBERG_WAREHOUSE_BUCKET}/production/"
    options:
      token: "${env:ICEBERG_TOKEN}"
      region: "${env:AWS_REGION:us-east-1}"

  - name: staging_catalog
    catalog_type: rest
    uri: "${env:ICEBERG_STAGING_URI}"
    warehouse: "s3://${env:ICEBERG_WAREHOUSE_BUCKET}/staging/"
    options:
      token: "${env:ICEBERG_STAGING_TOKEN}"
      region: "${env:AWS_REGION:us-east-1}"
```

**Iceberg environment variables:**
```bash
export ICEBERG_URI="https://catalog.company.com"
export ICEBERG_WAREHOUSE_BUCKET="company-data-warehouse"
export ICEBERG_TOKEN="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."

export ICEBERG_STAGING_URI="https://staging-catalog.company.com"
export ICEBERG_STAGING_TOKEN="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 4. Application Configuration

```yaml
# Application-level settings
duckdb:
  database: "${env:CATALOG_DATABASE_NAME:catalog}.duckdb"
  pragmas:
    - "SET memory_limit='${env:MEMORY_LIMIT:1GB}'"
    - "SET threads='${env:THREAD_COUNT:2}'"
    - "SET timezone='${env:TIMEZONE:UTC}'"

# File paths
attachments:
  duckdb:
    - alias: reference
      path: "${env:REFERENCE_DATA_PATH:./reference_data.duckdb}"

# S3 configuration
views:
  - name: data_source
    source: "${env:DATA_SOURCE_TYPE:parquet}"
    uri: "${env:DATA_URI:s3://default-bucket/data/*.parquet}"
```

**Application environment variables:**
```bash
export CATALOG_DATABASE_NAME="my_analytics"
export MEMORY_LIMIT="4GB"
export THREAD_COUNT="8"
export TIMEZONE="America/New_York"

export REFERENCE_DATA_PATH="/data/reference.duckdb"

export DATA_SOURCE_TYPE="parquet"
export DATA_URI="s3://my-bucket/production-data/*.parquet"
```

## Environment-Specific Configurations

### Development vs Production Strategy

Create a base configuration with environment overlays:

**`base-config.yaml`:**
```yaml
version: 1

duckdb:
  database: "${env:CATALOG_NAME:analytics}.duckdb"
  
views:
  - name: user_data
    source: parquet
    uri: "${env:DATA_BUCKET}/users/*.parquet"
    
  - name: event_data
    source: parquet
    uri: "${env:DATA_BUCKET}/events/*.parquet"
    
  - name: analytics_summary
    sql: |
      SELECT 
        DATE(e.timestamp) as event_date,
        COUNT(*) as total_events,
        COUNT(DISTINCT e.user_id) as unique_users
      FROM event_data e
      JOIN user_data u ON e.user_id = u.id
      GROUP BY DATE(e.timestamp)
```

**Development environment (`.env.dev`):**
```bash
export CATALOG_NAME="dev_analytics"
export DATA_BUCKET="s3://company-dev-data"
export AWS_ACCESS_KEY_ID="dev-key"
export AWS_SECRET_ACCESS_KEY="dev-secret"
```

**Production environment (`.env.prod`):**
```bash
export CATALOG_NAME="prod_analytics"
export DATA_BUCKET="s3://company-prod-data"
export AWS_ACCESS_KEY_ID="prod-key"
export AWS_SECRET_ACCESS_KEY="prod-secret"
```

### Docker and Container Deployment

**`Dockerfile`:**
```dockerfile
FROM python:3.9-slim

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY . /app
WORKDIR /app

# Use environment variables for configuration
ENV CONFIG_FILE="/app/config-production.yaml"
ENV LOG_LEVEL="INFO"

CMD ["duckalog", "build", "$CONFIG_FILE"]
```

**Docker Compose (development):**
```yaml
# docker-compose.yml
version: '3.8'
services:
  duckalog:
    build: .
    environment:
      - CONFIG_FILE=config-development.yaml
      - CATALOG_NAME=dev_catalog
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - DB_PASSWORD=${DB_PASSWORD}
    volumes:
      - ./data:/app/data
      - ./configs:/app/configs
```

**Kubernetes ConfigMap and Secret:**
```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: duckalog-config
data:
  config-production.yaml: |
    version: 1
    duckdb:
      database: "/data/catalog.duckdb"
      pragmas:
        - "SET memory_limit='8GB'"
        - "SET threads=8"
    views:
      - name: production_data
        source: parquet
        uri: "s3://${env:PRODUCTION_BUCKET}/data/*.parquet"

---
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: duckalog-secrets
type: Opaque
stringData:
  AWS_ACCESS_KEY_ID: "AKIA..."
  AWS_SECRET_ACCESS_KEY: "..."
  PRODUCTION_BUCKET: "company-prod-data"
```

## Step-by-Step Usage

### 1. Set Up Environment Variables

**Option A: Direct environment variables**
```bash
# Set variables for current session
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="..."
export DATABASE_PASSWORD="secret"
export ENVIRONMENT="development"

# Verify they're set
echo $AWS_ACCESS_KEY_ID
```

**Option B: Using .env file**
```bash
# Create .env file
cat > .env << EOF
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
DATABASE_PASSWORD=secret
ENVIRONMENT=development
EOF

# Load the file
source .env

# Add to .gitignore
echo ".env" >> .gitignore
```

**Option C: Using direnv (recommended)**
```bash
# Install direnv
# Then in your project directory:
echo "source .env" > .envrc
direnv allow
# direnv automatically loads .env when you cd into the directory
```

### 2. Create Configuration with Environment Variables

```yaml
# config.yaml
version: 1

duckdb:
  database: "${env:CATALOG_NAME:analytics}.duckdb"
  pragmas:
    - "SET memory_limit='${env:MEMORY_LIMIT:1GB}'"
    - "SET s3_access_key_id='${env:AWS_ACCESS_KEY_ID}'"
    - "SET s3_secret_access_key='${env:AWS_SECRET_ACCESS_KEY}'"

attachments:
  postgres:
    - alias: main_db
      host: "${env:DB_HOST}"
      database: "${env:DB_NAME}"
      user: "${env:DB_USER}"
      password: "${env:DB_PASSWORD}"

views:
  - name: sample_data
    source: parquet
    uri: "s3://${env:DATA_BUCKET}/sample/*.parquet"
```

### 3. Validate Configuration

```bash
# Check for missing environment variables
duckalog validate config.yaml

# If variables are missing, you'll see errors like:
# ConfigError: Environment variable 'AWS_ACCESS_KEY_ID' not found
```

### 4. Generate SQL with Environment Variables

```bash
# The SQL will be generated with environment variables resolved
duckalog generate-sql config.yaml --output generated.sql

# Check the output to see resolved values (be careful with secrets!)
cat generated.sql
```

### 5. Build Catalog

```bash
# Build with environment variables
duckalog build config.yaml

# This will create catalog.duckdb (or whatever name you specified)
```

### 6. Use in Scripts

```python
# build_catalog.py
import os
from duckalog import build_catalog, validate_config

# Set environment based on command line argument
env = os.environ.get('ENVIRONMENT', 'development')
config_file = f'config-{env}.yaml'

# Validate first
try:
    validate_config(config_file)
    print(f"✅ Configuration validated for {env} environment")
except Exception as e:
    print(f"❌ Configuration error: {e}")
    exit(1)

# Build catalog
build_catalog(config_file)
print(f"✅ Catalog built for {env} environment")
```

```bash
# Run for different environments
ENVIRONMENT=development python build_catalog.py
ENVIRONMENT=production python build_catalog.py
```

## Troubleshooting

### Common Issues

**1. Missing Environment Variables**
```bash
# Check what's set
env | grep -E "(AWS|DB|DATA)"

# Check specific variable
echo "AWS_ACCESS_KEY_ID: $AWS_ACCESS_KEY_ID"

# List all variables (be careful with secrets!)
env
```

**2. .env File Not Being Loaded**

```bash
# Check if .env file exists
ls -la .env

# Verify file permissions
ls -la .env

# Check file content
cat .env

# Run with verbose logging to see .env loading
duckalog build config.yaml --verbose
```

Expected verbose output:
```
Loading config {'path': 'config.yaml'}
Loading .env files {'config_path': 'config.yaml', 'file_count': 1}
Loaded .env file {'file_path': '/path/to/.env', 'var_count': 3}
Completed .env file loading {'total_files': 1}
```

**3. .env File Discovery Issues**

```bash
# Check directory structure
find . -name ".env" -type f

# Verify .env file location relative to config
tree -a  # Show hidden files

# Test with explicit .env placement
cp .env ./subdir/  # Copy .env to same directory as config
```

**4. Variable Not Expanding**

```yaml
# Make sure you're using the correct syntax
good: "${env:VARIABLE_NAME}"
bad: "$VARIABLE_NAME"                    # Wrong
bad: "${VARIABLE_NAME}"                  # Missing env: prefix
bad: "${env:}"                           # Empty variable name
```

**5. Default Values Not Working**

```yaml
# Correct syntax for defaults
with_default: "${env:MISSING_VAR:default_value}"
without_default: "${env:ANOTHER_VAR}"    # Will error if not set

# Note: Default values must be strings
correct: "${env:PORT:5432}"              # String default
incorrect: "${env:PORT:5432}"            # Still string, but looks like number
```

**6. Special Characters in .env Values**

```bash
# For passwords with special characters, quotes might be needed
# .env file:
PASSWORD="my'password\"with\"quotes"
COMPLEX_SECRET="base64==encoded==secret"

# Configuration:
password: "${env:PASSWORD}"
secret: "${env:COMPLEX_SECRET}"
```

**7. .env File Format Errors**

```bash
# Common .env format issues:
# - Missing equals sign
INVALID_LINE_WITHOUT_EQUALS

# - Empty variable names
=VALUE

# - Invalid variable names
123INVALID=value
INVALID-CHAR=value

# Good format:
VALID_VAR=value
ANOTHER_VAR="quoted value"
```

### Debug Commands

**Check .env file loading:**

```bash
# Run with maximum verbosity to see .env loading process
duckalog build config.yaml --verbose 2>&1 | grep -i env

# Look for these log messages:
# "Loading .env files" - .env discovery started
# "Loaded .env file" - .env file was loaded successfully  
# "No .env files found" - no .env files in search path
# "Failed to load .env file" - error loading .env file
```

**Check environment variable resolution:**

```bash
# Create a simple config to test variables
cat > test_vars.yaml << EOF
version: 1
test_field: "${env:TEST_VAR:default_value}"
EOF

# Validate and see what happens
duckalog validate test_vars.yaml

# Set the variable and test again
export TEST_VAR="resolved_value"
duckalog validate test_vars.yaml

# Check .env file specifically
export TEST_VAR=""
echo "TEST_VAR=test_value" > .env
duckalog validate test_vars.yaml
```

**List all environment variables used in config:**

```bash
# Use grep to find env variable usage
grep -o '\${env:[^}]*}' config.yaml | sort | uniq

# Check what's in your .env file
cat .env | grep -v '^#' | grep '=' | cut -d'=' -f1

# Compare used vs available variables
echo "Variables used in config:"
grep -o '\${env:[^}:]*' config.yaml | sed 's/\${env://' | sort | uniq

echo "Variables available in .env:"
cat .env | grep -v '^#' | grep '=' | cut -d'=' -f1 | sort | uniq
```

**Debug .env file discovery:**

```bash
# Check current working directory
pwd

# Check relative paths
ls -la .env* 2>/dev/null || echo "No .env files found in current directory"

# Check if .env is readable
test -r .env && echo ".env is readable" || echo ".env is not readable"

# Check directory permissions
ls -ld .
```

### .env File Security Testing

**Check for accidentally committed .env files:**

```bash
# Check if .env is tracked by git
git ls-files | grep "^\.env"

# Check git history for .env files
git log --full-history -- "*/.env"

# Search for .env files in repository
find . -name ".env" -type f

# Use git-secrets to scan for credentials
git-secrets --scan
```

**Validate .env file content:**

```bash
# Check for common secrets patterns
grep -iE "(password|secret|key|token)" .env

# Validate .env file syntax
python3 -c "
import os
with open('.env') as f:
    for line_num, line in enumerate(f, 1):
        line = line.strip()
        if line and not line.startswith('#') and '=' not in line:
            print(f'Line {line_num}: Invalid format - {line}')
        elif '=' in line:
            key, value = line.split('=', 1)
            if not key.strip():
                print(f'Line {line_num}: Empty key name')
"

# Check file permissions
ls -la .env
# Should show: -rw------- (600) for security
```

### Security Testing

**Check for accidentally committed secrets:**
```bash
# Search for potential secrets in config files
grep -r "password\|secret\|key\|token" *.yaml | grep -v env:

# Check git history for secrets
git log -p --grep="password\|secret\|key" --all

# Use git-secrets or similar tools
git-secrets --scan
```

## Advanced Patterns

### 1. Environment Variable Validation

```python
# validate_env.py
import os
import sys

required_vars = [
    'AWS_ACCESS_KEY_ID',
    'AWS_SECRET_ACCESS_KEY',
    'DATABASE_PASSWORD'
]

missing_vars = []
for var in required_vars:
    if not os.environ.get(var):
        missing_vars.append(var)

if missing_vars:
    print(f"❌ Missing required environment variables:")
    for var in missing_vars:
        print(f"   - {var}")
    print("\nSet them with:")
    print(f"export {' '.join(f'{var}=...' for var in missing_vars)}")
    sys.exit(1)

print("✅ All required environment variables are set")
```

### 2. Dynamic Configuration Selection

```python
# dynamic_config.py
import os
from pathlib import Path

def get_config_for_environment():
    env = os.environ.get('ENVIRONMENT', 'development')
    
    # Map environment to config file
    config_map = {
        'development': 'configs/config-dev.yaml',
        'staging': 'configs/config-staging.yaml',
        'production': 'configs/config-prod.yaml'
    }
    
    config_file = config_map.get(env)
    if not config_file or not Path(config_file).exists():
        raise FileNotFoundError(f"No config found for environment: {env}")
    
    return config_file

# Usage
config = get_config_for_environment()
print(f"Using configuration: {config}")
```

### 3. Secret Rotation Support

```yaml
# config-with-rotation.yaml
version: 1

duckdb:
  pragmas:
    # Support both old and new AWS credentials during rotation
    - "SET s3_access_key_id='${env:AWS_ACCESS_KEY_ID_NEW:${env:AWS_ACCESS_KEY_ID}}'"
    - "SET s3_secret_access_key='${env:AWS_SECRET_ACCESS_KEY_NEW:${env:AWS_SECRET_ACCESS_KEY}}'"
    
attachments:
  postgres:
    - alias: main
      password: "${env:DB_PASSWORD_NEW:${env:DB_PASSWORD}}"
```

This environment variable pattern enables secure, portable, and maintainable Duckalog configurations across all your deployment environments.