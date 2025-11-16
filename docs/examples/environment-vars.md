# Environment Variables Example

This example demonstrates how to use environment variables effectively in Duckalog configurations. You'll learn security best practices, environment-specific configurations, and credential management patterns that keep your configs portable and secure.

## When to Use This Example

Choose this example if:
- You need to keep credentials out of configuration files
- You want different configs for development, staging, and production
- You're deploying Duckalog across multiple environments
- You need to comply with security policies (no hardcoded secrets)
- You want to make configs reusable across different setups

## Prerequisites

1. **Duckalog installed:**
   ```bash
   pip install duckalog
   ```

2. **Basic understanding of environment variables in your shell:**
   ```bash
   # Check if a variable exists
   echo $AWS_ACCESS_KEY_ID
   
   # Set a variable
   export DATABASE_PASSWORD="my-secret-password"
   
   # Unset a variable
   unset DATABASE_PASSWORD
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

**✅ Correct - Use environment variables:**
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

# Generated catalogs
*.duckdb
*.db

# Logs
*.log

# Temporary files
tmp/
temp/
```

### 3. Environment-Specific Files

Use `.env` files for local development (add to `.gitignore`):

```bash
# .env.local (for local development)
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
DATABASE_PASSWORD=dev-password

# .env.production (for production deployment)
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
DATABASE_PASSWORD=production-password
```

Load with:
```bash
# Load environment file
source .env.local

# Or use a tool like direnv
# (add to .gitignore)
echo "source .env.local" > .envrc
direnv allow
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

**2. Variable Not Expanding**
```yaml
# Make sure you're using the correct syntax
good: "${env:VARIABLE_NAME}"
bad: "$VARIABLE_NAME"                    # Wrong
bad: "${VARIABLE_NAME}"                  # Missing env: prefix
bad: "${env:}"                           # Empty variable name
```

**3. Default Values Not Working**
```yaml
# Correct syntax for defaults
with_default: "${env:MISSING_VAR:default_value}"
without_default: "${env:ANOTHER_VAR}"    # Will error if not set

# Note: Default values must be strings
correct: "${env:PORT:5432}"              # String default
incorrect: "${env:PORT:5432}"            # Still string, but looks like number
```

**4. Special Characters in Values**
```yaml
# For passwords with special characters, quotes might be needed
password: "${env:DB_PASSWORD}"           # Usually works
password: "'${env:DB_PASSWORD}'"         # Force quotes if needed

# If your password contains quotes, escape them
password: "${env:COMPLEX_PASSWORD:my\"special'pass}"
```

### Debug Commands

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
```

**List all environment variables used in config:**
```bash
# Use grep to find env variable usage
grep -o '\${env:[^}]*}' config.yaml | sort | uniq
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