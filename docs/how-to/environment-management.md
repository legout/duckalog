# How to Manage Different Environments

Set up and manage different environments (development, staging, production) with proper separation of concerns and secure credential management.

## Problem

You need to deploy Duckalog configurations across multiple environments while maintaining:
- Separate database connections and credentials
- Environment-specific settings and paths
- Consistent configuration structure
- Secure deployment practices

## Prerequisites

- Basic Duckalog configuration knowledge
- Understanding of environment variables
- Familiarity with deployment concepts
- Access to different environment credentials

## Solution

### 1. Base Configuration Structure

Create a base configuration with common settings:

```yaml
# config/base.yaml
version: 1

duckdb:
  # Common pragmas for all environments
  pragmas:
    - "SET memory_limit='2GB'"
    - "SET threads=4"
    - "SET enable_progress_bar=false"

# Common views that exist in all environments
views: []
```

### 2. Environment-Specific Configurations

Create separate configurations for each environment:

#### Development Environment

```yaml
# config/dev.yaml
version: 1
imports:
  - ./base.yaml

duckdb:
  database: dev_analytics.duckdb
  # Development-specific settings
  pragmas:
    - "SET memory_limit='1GB'"     # Lower memory for dev
    - "SET threads=2"              # Fewer threads for dev

views:
  - name: users_dev
    source: parquet
    uri: "./data/dev/users.parquet"
    sql: |
      SELECT * FROM users 
      WHERE created_at >= '2023-01-01'  # Recent data only
```

#### Staging Environment

```yaml
# config/staging.yaml
version: 1
imports:
  - ./base.yaml

duckdb:
  database: staging_analytics.duckdb
  pragmas:
    - "SET memory_limit='4GB'"     # More memory for staging
    - "SET threads=6"              # More threads for staging

views:
  - name: users_staging
    source: parquet
    uri: "./data/staging/users.parquet"
    sql: |
      SELECT * FROM users 
      WHERE created_at >= '2022-01-01'  # Full historical data
```

#### Production Environment

```yaml
# config/prod.yaml
version: 1
imports:
  - ./base.yaml

duckdb:
  database: prod_analytics.duckdb
  pragmas:
    - "SET memory_limit='8GB'"     # Maximum memory for production
    - "SET threads=8"              # Maximum threads for production
    - "SET enable_progress_bar=false"  # No progress bars in production

views:
  - name: users_prod
    source: parquet
    uri: "s3://prod-data-bucket/analytics/users.parquet"
    sql: |
      SELECT * FROM users 
      -- No WHERE clause - full production data
```

### 3. Environment Variables for Credentials

Use environment variables for sensitive information:

```yaml
# config/prod.yaml
version: 1
imports:
  - ./base.yaml

duckdb:
  database: prod_analytics.duckdb

attachments:
  postgres:
    - alias: warehouse
      host: "${env:PG_HOST}"           # Production database host
      port: 5432
      database: "${env:PG_DATABASE}"     # Production database name
      user: "${env:PG_USER}"           # Production database user
      password: "${env:PG_PASSWORD}"     # Production database password

views:
  - name: users_prod
    source: parquet
    uri: "s3://prod-data-bucket/analytics/"
    # S3 credentials from environment
    sql: |
      SELECT * FROM users 
      WHERE created_at >= '${env:DATA_START_DATE}'
```

### 4. Environment Selection Script

Create a script to select the right configuration:

```bash
#!/bin/bash
# scripts/deploy.sh

set -e

# Environment selection
ENVIRONMENT=${1:-dev}
echo "Deploying to environment: $ENVIRONMENT"

# Validate environment
case $ENVIRONMENT in
  dev|staging|prod)
    ;;
  *)
    echo "Error: Environment must be dev, staging, or prod"
    exit 1
    ;;
esac

# Set environment-specific variables
export DUCKALOG_ENV=$ENVIRONMENT

# Load environment variables
case $ENVIRONMENT in
  dev)
    export PG_HOST=localhost
    export PG_DATABASE=analytics_dev
    export PG_USER=dev_user
    export PG_PASSWORD=dev_password
    export DATA_START_DATE="2023-01-01"
    ;;
  staging)
    export PG_HOST=staging-db.company.com
    export PG_DATABASE=analytics_staging
    export PG_USER=staging_user
    export PG_PASSWORD=${STAGING_PG_PASSWORD}
    export DATA_START_DATE="2022-01-01"
    ;;
  prod)
    export PG_HOST=prod-db.company.com
    export PG_DATABASE=analytics_prod
    export PG_USER=prod_user
    export PG_PASSWORD=${PROD_PG_PASSWORD}
    export DATA_START_DATE="2020-01-01"
    ;;
esac

# Build catalog
CONFIG_FILE="config/${ENVIRONMENT}.yaml"
echo "Building catalog from: $CONFIG_FILE"

duckalog build "$CONFIG_FILE"

echo "Deployment to $ENVIRONMENT completed successfully"
```

### 5. Docker Environment Configuration

For containerized deployments:

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install Duckalog
RUN pip install duckalog[remote]

# Copy configuration files
COPY config/ ./config/
COPY scripts/ ./scripts/
COPY data/ ./data/

# Set default environment
ENV DUCKALOG_ENV=dev

# Run deployment script
CMD ["./scripts/deploy.sh"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  duckalog-dev:
    build: .
    environment:
      - DUCKALOG_ENV=dev
      - PG_HOST=postgres-dev
      - PG_DATABASE=analytics_dev
      - PG_USER=dev_user
      - PG_PASSWORD=dev_password
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs

  duckalog-staging:
    build: .
    environment:
      - DUCKALOG_ENV=staging
      - PG_HOST=postgres-staging
      - PG_DATABASE=analytics_staging
      - PG_USER=staging_user
      - PG_PASSWORD=${STAGING_PG_PASSWORD}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs

  duckalog-prod:
    build: .
    environment:
      - DUCKALOG_ENV=prod
      - PG_HOST=postgres-prod
      - PG_DATABASE=analytics_prod
      - PG_USER=prod_user
      - PG_PASSWORD=${PROD_PG_PASSWORD}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
```

### 6. Kubernetes Environment Configuration

For Kubernetes deployments:

```yaml
# k8s/duckalog-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: duckalog
spec:
  replicas: 1
  selector:
    matchLabels:
      app: duckalog
  template:
    metadata:
      labels:
        app: duckalog
    spec:
      containers:
      - name: duckalog
        image: duckalog:latest
        env:
        - name: DUCKALOG_ENV
          value: "prod"
        - name: PG_HOST
          valueFrom:
            secretKeyRef:
              name: database-credentials
              key: host
        - name: PG_DATABASE
          valueFrom:
            secretKeyRef:
              name: database-credentials
              key: database
        - name: PG_USER
          valueFrom:
            secretKeyRef:
              name: database-credentials
              key: username
        - name: PG_PASSWORD
          valueFrom:
            secretKeyRef:
              name: database-credentials
              key: password
        volumeMounts:
        - name: config-volume
          mountPath: /app/config
        - name: data-volume
          mountPath: /app/data
      volumes:
      - name: config-volume
        configMap:
          name: duckalog-config
      - name: data-volume
        persistentVolumeClaim:
          claimName: duckalog-data
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: duckalog-config
data:
  prod.yaml: |
    version: 1
    imports:
      - ./base.yaml
    duckdb:
      database: /app/data/prod_analytics.duckdb
      pragmas:
        - "SET memory_limit='8GB'"
        - "SET threads=8"
    views:
      - name: users_prod
        source: parquet
        uri: "/app/data/production/users.parquet"
```

## Verification

### 1. Test Environment Loading

```bash
# Test each environment
for env in dev staging prod; do
  echo "Testing $env environment..."
  duckalog validate "config/${env}.yaml"
  if [ $? -eq 0 ]; then
    echo "✅ $env configuration is valid"
  else
    echo "❌ $env configuration has errors"
  fi
done
```

### 2. Verify Environment Isolation

```bash
# Ensure environments don't interfere
echo "Checking environment isolation..."

# Check that dev doesn't access prod data
if duckalog build config/dev.yaml --dry-run | grep -q "prod-data-bucket"; then
  echo "❌ Dev configuration accessing production data"
  exit 1
fi

# Check that prod doesn't use dev settings
if duckalog build config/prod.yaml --dry-run | grep -q "memory_limit='1GB'"; then
  echo "❌ Production configuration using development memory"
  exit 1
fi

echo "✅ Environment isolation verified"
```

### 3. Test Deployment Script

```bash
# Test deployment script
./scripts/deploy.sh dev
echo "Dev deployment exit code: $?"

./scripts/deploy.sh staging
echo "Staging deployment exit code: $?"

./scripts/deploy.sh prod
echo "Production deployment exit code: $?"
```

## Common Variations

### 1. Configuration Imports for Environments

Use config imports to share common settings:

```yaml
# config/prod.yaml
version: 1
imports:
  - ./base.yaml          # Common settings
  - ./shared-views.yaml   # Shared view definitions
  - ./prod-secrets.yaml   # Production-only secrets

duckdb:
  database: prod_analytics.duckdb
  # Production-specific overrides
  pragmas:
    - "SET memory_limit='16GB'"  # Override base.yaml
```

### 2. Environment Detection

Automatically detect environment:

```yaml
# config/auto.yaml
version: 1
imports:
  - ./base.yaml
  - "./${env:ENVIRONMENT}.yaml"  # Dynamic import based on environment

duckdb:
  database: "${env:ENVIRONMENT}_analytics.duckdb"
```

```bash
# Use environment detection
export ENVIRONMENT=prod
duckalog build config/auto.yaml
```

### 3. Configuration Templates

Use template files with environment substitution:

```yaml
# config/template.yaml
version: 1
imports:
  - ./base.yaml

duckdb:
  database: "{{ENVIRONMENT}}_analytics.duckdb"
  threads: "{{THREADS}}"
  memory_limit: "{{MEMORY_LIMIT}}"

views:
  - name: "{{ENVIRONMENT}}_users"
    uri: "{{DATA_PATH}}/users.parquet"
```

```bash
# Generate configuration from template
envsubst < config/template.yaml > config/generated.yaml
```

## Troubleshooting

### Environment Variable Not Found

**Error**: `ConfigError: Environment variable not found: PG_HOST`

**Solution**:
```bash
# Check if variable is set
echo $PG_HOST

# Set variable
export PG_HOST=your_host

# Use .env file
echo "PG_HOST=your_host" >> .env
source .env
```

### Configuration File Not Found

**Error**: `ConfigError: Config file not found: config/prod.yaml`

**Solution**:
```bash
# Check file exists
ls -la config/prod.yaml

# Check working directory
pwd

# Use absolute path
duckalog build /full/path/to/config/prod.yaml
```

### Permission Issues

**Error**: `PermissionError: Cannot read configuration file`

**Solution**:
```bash
# Check file permissions
ls -la config/prod.yaml

# Fix permissions
chmod 600 config/prod.yaml  # Read/write for owner only
chmod 644 config/prod.yaml  # Read for everyone, write for owner
```

### Database Connection Failures

**Error**: `EngineError: Failed to connect to database`

**Solution**:
```bash
# Test database connection manually
duckdb config/prod_analytics.duckdb
# Then test: .tables

# Check database file permissions
ls -la prod_analytics.duckdb

# Verify database path in config
grep "database:" config/prod.yaml
```

## Best Practices

### 1. Security
- Never commit credentials to version control
- Use environment variables for all sensitive data
- Rotate credentials regularly
- Use read-only database connections where possible

### 2. Consistency
- Maintain consistent structure across environments
- Use config imports to share common settings
- Document environment-specific differences
- Use naming conventions for environments

### 3. Deployment
- Test configurations in staging before production
- Use deployment scripts for consistency
- Implement rollback procedures
- Monitor deployments for issues

### 4. Maintenance
- Regularly update base configurations
- Review environment-specific settings
- Document configuration changes
- Use version control for configuration files

## Next Steps

After setting up environment management:

- **Automate deployments** with CI/CD pipelines
- **Implement monitoring** for different environments
- **Create backup procedures** for configuration and data
- **Document team workflows** for environment changes
- **Explore advanced patterns** in [Performance Tuning](performance-tuning.md)

You now have a robust environment management system that supports secure, scalable deployments across development, staging, and production environments.