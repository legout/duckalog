# Environment Variables Security Example

This example demonstrates security best practices for using environment variables in Duckalog configurations. You'll learn how to keep credentials out of configuration files, manage environment-specific settings, and implement secure credential management patterns.

## 🎯 Learning Objectives

After completing this example, you'll understand:

- **Security**: How to keep secrets and credentials out of version control
- **Portability**: Creating configurations that work across development, staging, and production
- **Environment Management**: Different setups for different environments
- **Best Practices**: Security patterns that prevent credential leaks
- **Deployment**: Using environment variables in Docker and Kubernetes

## 📋 Prerequisites

- Duckalog installed (`pip install duckalog`)
- Basic understanding of environment variables
- AWS account (for S3 examples - optional)

## 🏗️ Example Structure

```
environment-variables-security/
├── README.md                 # This file
├── catalog-dev.yaml         # Development configuration
├── catalog-prod.yaml        # Production configuration
├── .env.example            # Template for environment variables
├── .gitignore              # Files to exclude from version control
├── generate-test-data.py   # Create test data for demonstration
├── validate-configs.py     # Validate configurations with different envs
└── scripts/
    ├── setup-dev.sh        # Set up development environment
    └── deploy-prod.sh      # Production deployment script
```

## 🚀 Quick Start

### 1. Set Up Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit with your values (use fake/placeholder values for learning)
nano .env
```

### 2. Development Setup

```bash
# Source development environment variables
source scripts/setup-dev.sh

# Build development catalog
duckalog build catalog-dev.yaml

# Validate the configuration
python validate-configs.py dev
```

### 3. Production Setup

```bash
# Set production environment variables
export ENVIRONMENT=production
# Set your production credentials...

# Build production catalog
duckalog build catalog-prod.yaml

# Validate production configuration
python validate-configs.py prod
```

## 🔒 Security Scenarios Covered

### Scenario 1: AWS S3 Integration

Securely connect to S3 buckets without hardcoding credentials:

```yaml
duckdb:
  pragmas:
    - "SET s3_region='${env:AWS_REGION:us-east-1}'"
    - "SET s3_access_key_id='${env:AWS_ACCESS_KEY_ID}'"
    - "SET s3_secret_access_key='${env:AWS_SECRET_ACCESS_KEY}'"

views:
  - name: secure_s3_data
    source: parquet
    uri: "s3://${env:DATA_BUCKET_PREFIX}-${env:ENVIRONMENT}/data/*.parquet"
```

### Scenario 2: Database Connections

Secure database credentials with environment-specific values:

```yaml
attachments:
  postgres:
    - alias: analytics_db
      host: "${env:DB_HOST}"
      port: "${env:DB_PORT:5432}"
      database: "${env:DB_NAME}"
      user: "${env:DB_USER}"
      password: "${env:DB_PASSWORD}"
      sslmode: "${env:DB_SSL_MODE:require}"
```

### Scenario 3: Iceberg Catalog Integration

Secure data lake connections:

```yaml
iceberg_catalogs:
  - name: production_catalog
    catalog_type: rest
    uri: "${env:ICEBERG_URI}"
    warehouse: "s3://${env:WAREHOUSE_BUCKET}/${env:ENVIRONMENT}/"
    options:
      token: "${env:ICEBERG_TOKEN}"
      region: "${env:AWS_REGION}"
```

## 🛡️ Security Best Practices Demonstrated

### 1. Never Commit Secrets
- All sensitive values use `${env:...}` syntax
- Configuration files are safe to commit
- Example files show structure without real secrets

### 2. Environment Isolation
- Different configurations for dev/staging/prod
- Environment-specific variable naming
- Default values for development convenience

### 3. Secure Defaults
- Production configurations require explicit values
- Development has sensible defaults
- SSL connections enforced in production

### 4. Validation & Testing
- Configuration validation scripts
- Environment variable presence checks
- Integration testing with different environments

## 📁 Environment Files

### Development Environment (`.env`)
```bash
# Development settings (safe to commit with placeholder values)
ENVIRONMENT=development
CATALOG_NAME=dev_catalog
MEMORY_LIMIT=1GB
THREAD_COUNT=2

# AWS Development (use dev credentials)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
DATA_BUCKET_PREFIX=mycompany-dev-data

# Database Development
DB_HOST=localhost
DB_PORT=5432
DB_NAME=analytics_dev
DB_USER=dev_user
DB_PASSWORD=dev_password
DB_SSL_MODE=prefer

# Iceberg Development
ICEBERG_URI=https://dev-catalog.example.com
ICEBERG_TOKEN=dev-token-placeholder
WAREHOUSE_BUCKET=mycompany-dev-warehouse
```

### Production Environment (production values)
```bash
# Production settings (real values)
ENVIRONMENT=production
CATALOG_NAME=prod_catalog
MEMORY_LIMIT=8GB
THREAD_COUNT=8

# AWS Production (real credentials)
AWS_REGION=us-west-2
AWS_ACCESS_KEY_ID=AKIAI44QH8DHBEXAMPLE
AWS_SECRET_ACCESS_KEY=je7MtGbClwBF/2Zp9Utk/h3yCo8nvbEXAMPLEKEY
DATA_BUCKET_PREFIX=mycompany-prod-data

# Database Production
DB_HOST=prod-db.example.com
DB_PORT=5432
DB_NAME=analytics_prod
DB_USER=prod_user
DB_PASSWORD=real-production-password
DB_SSL_MODE=require

# Iceberg Production
ICEBERG_URI=https://catalog.example.com
ICEBERG_TOKEN=real-production-token
WAREHOUSE_BUCKET=mycompany-prod-warehouse
```

## 🧪 Validation and Testing

Run comprehensive validation:

```bash
# Validate development configuration
python validate-configs.py dev

# Validate production configuration
python validate-configs.py prod

# Test with missing variables (should fail gracefully)
unset AWS_ACCESS_KEY_ID
python validate-configs.py dev
```

The validation script checks:
- ✅ Required environment variables are present
- ✅ Configuration files are syntactically correct
- ✅ Environment variables resolve properly
- ✅ Security best practices are followed

## 🐳 Docker Integration

```dockerfile
FROM python:3.9-slim

# Install Duckalog
RUN pip install duckalog

# Copy configuration
COPY . /app
WORKDIR /app

# Use environment variables for configuration
ENV CONFIG_FILE=catalog-prod.yaml

CMD ["duckalog", "build", "$CONFIG_FILE"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  duckalog:
    build: .
    environment:
      - CONFIG_FILE=catalog-dev.yaml
      - ENVIRONMENT=development
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - DB_PASSWORD=${DB_PASSWORD}
    volumes:
      - ./catalogs:/app/catalogs
```

## ☸️ Kubernetes Deployment

```yaml
# k8s-configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: duckalog-config
data:
  catalog-prod.yaml: |
    version: 1
    duckdb:
      database: "/data/catalog.duckdb"
      pragmas:
        - "SET memory_limit='${env:MEMORY_LIMIT:8GB}'"
        - "SET s3_access_key_id='${env:AWS_ACCESS_KEY_ID}'"
        - "SET s3_secret_access_key='${env:AWS_SECRET_ACCESS_KEY}'"
    views:
      - name: production_data
        source: parquet
        uri: "s3://${env:DATA_BUCKET}/data/*.parquet"

---
# k8s-secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: duckalog-secrets
type: Opaque
stringData:
  AWS_ACCESS_KEY_ID: "AKIA..."
  AWS_SECRET_ACCESS_KEY: "..."
  DATA_BUCKET: "company-prod-data"
  MEMORY_LIMIT: "8GB"
```

## 🔍 Troubleshooting

### Common Issues and Solutions

**Missing Environment Variables**
```bash
# Check what's set
env | grep -E "(AWS|DB|DATA)"

# Set missing variables
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
```

**Variable Not Expanding**
- Check syntax: must be `${env:VAR_NAME}`, not `$VAR_NAME`
- Ensure no typos in variable names
- Verify variables are exported, not just set

**Permission Issues**
- Check file permissions on configuration files
- Ensure database directory is writable
- Verify S3 bucket permissions

### Security Validation

```bash
# Check for accidentally committed secrets
grep -r "password\|secret\|key\|token" *.yaml | grep -v env:

# Validate git history for secrets
git log -p --grep="password\|secret\|key" --all

# Use duckalog validation
duckalog validate catalog-prod.yaml
```

## 📚 Key Takeaways

1. **Security First**: Never commit credentials - use environment variables
2. **Environment Isolation**: Separate configs for dev/staging/prod
3. **Validation**: Always validate configurations before deployment
4. **Default Values**: Use sensible defaults for development
5. **Documentation**: Document all required environment variables
6. **Testing**: Test configurations in all target environments

## 🎯 Next Steps

- Try the **DuckDB Performance Settings** example for optimization techniques
- Explore the **Multi-Source Analytics** example for complex data integration
- Review the contributing guidelines for creating your own examples

---

**💡 Tip**: Use `direnv` for automatic environment loading when switching between projects.