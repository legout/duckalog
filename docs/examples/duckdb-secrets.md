# DuckDB Secrets Example

This example demonstrates how to use DuckDB secrets in Duckalog to manage credentials for external services like S3, Azure, GCS, and databases. Secrets provide a secure way to handle authentication without hardcoding credentials in SQL.

## When to Use Secrets

Choose secrets when you need to:
- Access cloud storage services (S3, Azure, GCS) with credentials
- Connect to databases (PostgreSQL, MySQL) using authentication
- Manage credentials across different environments securely
- Support automatic credential fetching (credential chains)
- Create persistent secrets that survive database restarts

## Basic Secret Configuration

### S3 Secret with Static Credentials

Create a file called `secrets-example.yaml`:

```yaml
version: 1

duckdb:
  database: secrets_catalog.duckdb
  
  # Extensions required for S3 access
  install_extensions:
    - httpfs
  
  # Secrets for external services
  secrets:
    - type: s3
      name: production_s3
      key_id: AKIAIOSFODNN7EXAMPLE
      secret: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
      region: us-west-2
      endpoint: s3.amazonaws.com  # Optional: custom endpoint

views:
  - name: sales_data
    source: parquet
    uri: "s3://my-production-bucket/sales/*.parquet"
    description: "Sales data from S3 with secret authentication"
```

### Azure Storage Secret

```yaml
version: 1

duckdb:
  database: azure_catalog.duckdb
  install_extensions:
    - httpfs
  
  secrets:
    - type: azure
      name: azure_prod
      provider: config
      persistent: true
      scope: 'prod/'
      connection_string: DefaultEndpointsProtocol=https;AccountName=myaccount;AccountKey=mykey;EndpointSuffix=core.windows.net
      # Alternative: Use tenant_id + account_name + secret
      # tenant_id: my-tenant-id
      # account_name: mystorageaccount
      # secret: my-azure-secret

views:
  - name: azure_logs
    source: parquet
    uri: "azure://mycontainer/logs/*.parquet"
    description: "Application logs from Azure storage"
```

### GCS Secret

```yaml
version: 1

duckdb:
  database: gcs_catalog.duckdb
  install_extensions:
    - httpfs
  
  secrets:
    - type: gcs
      name: gcs_service_account
      key_id: my-service-account@project.iam.gserviceaccount.com
      secret: '-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKw...\n-----END PRIVATE KEY-----'
      endpoint: storage.googleapis.com

views:
  - name: gcs_data
    source: parquet
    uri: "gs://my-bucket/data/*.parquet"
    description: "Data from Google Cloud Storage"
```

## Advanced Secret Configurations

### Credential Chain Provider

For automatic credential detection (useful in AWS environments):

```yaml
version: 1

duckdb:
  database: auto_cred_catalog.duckdb
  install_extensions:
    - httpfs
  
  secrets:
    - type: s3
      name: s3_auto
      provider: credential_chain
      region: us-east-1
      # No key_id/secret needed - DuckDB will auto-detect

views:
  - name: auto_s3_data
    source: parquet
    uri: "s3://auto-bucket/data/*.parquet"
    description: "S3 data with automatic credentials"
```

### Database Secrets

#### PostgreSQL Secret

```yaml
version: 1

duckdb:
  database: pg_catalog.duckdb
  
  secrets:
    - type: postgres
      name: analytics_db
      provider: config
      persistent: true
      connection_string: postgresql://user:password@localhost:5432/analytics
      # Alternative: Individual parameters
      # host: localhost
      # port: 5432
      # database: analytics
      # key_id: user
      # secret: password

views:
  - name: postgres_users
    source: postgres
    database: analytics_db
    table: users
    description: "Users from PostgreSQL with secret authentication"
```

#### MySQL Secret

```yaml
version: 1

duckdb:
  database: mysql_catalog.duckdb
  
  secrets:
    - type: mysql
      name: webapp_db
      connection_string: mysql://user:password@db.example.com:3306/webapp

views:
  - name: mysql_products
    source: mysql
    database: webapp_db
    table: products
    description: "Products from MySQL with secret authentication"
```

### HTTP Basic Auth Secret

```yaml
version: 1

duckdb:
  database: api_catalog.duckdb
  
  secrets:
    - type: http
      name: api_auth
      key_id: my-api-username
      secret: my-api-password
      # Optional: Add custom headers
      options:
        custom_header: "Bearer-Token"
        timeout: 30

views:
  - name: api_data
    sql: |
      SELECT * FROM read_csv_auto('https://api.example.com/data.csv')
    description: "Data from HTTP API with basic authentication"
```

## Environment Variable Integration

### Using Environment Variables for Security

```yaml
version: 1

duckdb:
  database: env_secrets_catalog.duckdb
  install_extensions:
    - httpfs
  
  secrets:
    - type: s3
      name: secure_s3
      key_id: ${env:AWS_ACCESS_KEY_ID}
      secret: ${env:AWS_SECRET_ACCESS_KEY}
      region: ${env:AWS_DEFAULT_REGION}
      
    - type: postgres
      name: db_auth
      connection_string: ${env:DATABASE_URL}

views:
  - name: secure_data
    source: parquet
    uri: "s3://secure-bucket/data/*.parquet"
    description: "Secure data using environment variables"
```

Set environment variables:

```bash
# AWS Credentials
export AWS_ACCESS_KEY_ID="AKIAIOSFODNN7EXAMPLE"
export AWS_SECRET_ACCESS_KEY="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
export AWS_DEFAULT_REGION="us-west-2"

# Database URL
export DATABASE_URL="postgresql://user:password@localhost:5432/analytics"
```

## Multiple Secrets and Scoping

### Multiple S3 Secrets for Different Environments

```yaml
version: 1

duckdb:
  database: multi_env_catalog.duckdb
  install_extensions:
    - httpfs
  
  secrets:
    # Production S3 with persistent secret
    - type: s3
      name: prod_s3
      provider: config
      persistent: true
      scope: 's3://prod-bucket/'
      key_id: ${env:PROD_AWS_KEY}
      secret: ${env:PROD_AWS_SECRET}
      region: us-east-1
      
    # Development S3 with temporary secret
    - type: s3
      name: dev_s3
      provider: config
      scope: 's3://dev-bucket/'
      key_id: ${env:DEV_AWS_KEY}
      secret: ${env:DEV_AWS_SECRET}
      region: us-west-2
      
    # Staging S3 with credential chain
    - type: s3
      name: staging_s3
      provider: credential_chain
      scope: 's3://staging-bucket/'
      region: us-central-1

views:
  - name: production_data
    source: parquet
    uri: "s3://prod-bucket/sales/*.parquet"
    description: "Production sales data"
    
  - name: development_data
    source: parquet
    uri: "s3://dev-bucket/experiments/*.parquet"
    description: "Development experiment data"
    
  - name: staging_logs
    source: parquet
    uri: "s3://staging-bucket/logs/*.parquet"
    description: "Staging log data"
```

## Step-by-Step Usage

### 1. Create Configuration

Save one of the examples above as `secrets-example.yaml`.

### 2. Set Environment Variables (if using interpolation)

```bash
# For S3 secrets
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-west-2"

# For database secrets
export DATABASE_URL="postgresql://user:password@localhost:5432/analytics"
```

### 3. Validate Configuration

```bash
duckalog validate secrets-example.yaml
```

Expected output:
```
✅ Configuration is valid
✅ All secrets defined correctly
✅ Environment variables resolved
```

### 4. Build Catalog

```bash
duckalog build secrets-example.yaml
```

### 5. Verify Secrets

```bash
# Connect to the created database
duckdb secrets_catalog.duckdb

# List created secrets
SELECT name, type, provider FROM duckdb_secrets();

# Check specific secret details
SELECT * FROM duckdb_secrets() WHERE name = 'production_s3';
```

## Secret Types Reference

### S3 Secret Fields

| Field | Required | Description |
|--------|-----------|-------------|
| `type` | Yes | Must be `"s3"` |
| `key_id` | For `config` provider | AWS access key ID |
| `secret` | For `config` provider | AWS secret access key |
| `region` | Optional | AWS region (e.g., `us-west-2`) |
| `endpoint` | Optional | Custom S3 endpoint |
| `scope` | Optional | URL prefix for secret scope |
| `provider` | Optional | `"config"` (default) or `"credential_chain"` |
| `persistent` | Optional | Whether secret persists across sessions |

### Azure Secret Fields

| Field | Required | Description |
|--------|-----------|-------------|
| `type` | Yes | Must be `"azure"` |
| `connection_string` | Either/or | Full connection string |
| `tenant_id` | Either/or | Azure AD tenant ID |
| `account_name` | Either/or | Storage account name |
| `secret` | For explicit auth | Account key or password |
| `scope` | Optional | URL prefix for secret scope |

### GCS Secret Fields

| Field | Required | Description |
|--------|-----------|-------------|
| `type` | Yes | Must be `"gcs"` |
| `key_id` | For `config` provider | Service account email |
| `secret` | For `config` provider | Private key content |
| `endpoint` | Optional | Custom GCS endpoint |
| `scope` | Optional | URL prefix for secret scope |

### Database Secret Fields

| Field | Required | Description |
|--------|-----------|-------------|
| `type` | Yes | `"postgres"` or `"mysql"` |
| `connection_string` | Either/or | Full database connection string |
| `host` | Either/or | Database host |
| `port` | Either/or | Database port |
| `database` | Either/or | Database name |
| `key_id` | Either/or | Database username |
| `secret` | Either/or | Database password |

### HTTP Secret Fields

| Field | Required | Description |
|--------|-----------|-------------|
| `type` | Yes | Must be `"http"` |
| `key_id` | Yes | Username for basic auth |
| `secret` | Yes | Password for basic auth |
| `options` | Optional | Additional HTTP headers/options |

## Best Practices

### Security

1. **Use Environment Variables**: Never hardcode secrets in configuration files
   ```yaml
   # Good: Use environment variables
   key_id: ${env:AWS_ACCESS_KEY_ID}
   secret: ${env:AWS_SECRET_ACCESS_KEY}
   
   # Bad: Hardcode secrets
   key_id: AKIAIOSFODNN7EXAMPLE
   secret: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
   ```

2. **Separate Environments**: Use different secrets for dev/staging/prod
3. **Use Persistent Secrets**: For long-running applications
4. **Limit Secret Scope**: Use scope to restrict secret to specific paths
5. **Rotate Credentials**: Update secrets regularly without changing configuration

### Performance

1. **Use Credential Chains**: In cloud environments for automatic credential rotation
2. **Scope Secrets**: Limit secrets to specific buckets/prefixes
3. **Persistent vs Temporary**: Use persistent secrets for frequently accessed resources
4. **Connection Pooling**: For database secrets, consider connection pooling

### Organization

1. **Name Secrets Clearly**: Use descriptive names like `prod_s3`, `dev_postgres`
2. **Group by Environment**: Keep production, development, staging secrets separate
3. **Document Dependencies**: Note which views depend on which secrets
4. **Version Control**: Keep secret configurations out of version control

## Troubleshooting

### Common Issues

**1. Secret Not Found Error:**
```
Catalog Error: Secret with name 'my_secret' does not exist
```
Solution: Check that the secret was created successfully and the name matches exactly.

**2. Permission Denied:**
```
Catalog Error: Permission denied
```
Solution: Verify credentials, region, and IAM permissions for cloud services.

**3. Invalid Secret Configuration:**
```
Config Error: S3 config provider requires key_id and secret
```
Solution: Ensure all required fields for the secret type are provided.

**4. Environment Variable Not Set:**
```
Config Error: Environment variable 'AWS_ACCESS_KEY_ID' is not set
```
Solution: Set the required environment variables before running duckalog.

### Debugging Secrets

```sql
-- List all secrets
SELECT name, type, provider, persistent FROM duckdb_secrets();

-- Check specific secret
SELECT * FROM duckdb_secrets() WHERE name = 'my_secret';

-- Test secret access
SELECT * FROM read_csv_auto('s3://my-bucket/test.csv') LIMIT 1;
```

## Integration with Other Duckalog Features

### Secrets with Attachments

```yaml
version: 1

duckdb:
  database: integrated_catalog.duckdb
  install_extensions:
    - httpfs
  
  secrets:
    - type: postgres
      name: analytics_db
      connection_string: ${env:ANALYTICS_DB_URL}
  
  attachments:
    postgres:
      - alias: analytics
        # Use the secret for authentication
        # DuckDB will automatically use the postgres secret
        
views:
  - name: analytics_data
    source: postgres
    database: analytics_db
    table: sales
    description: "Analytics data using secret authentication"
```

### Secrets with Iceberg Catalogs

```yaml
version: 1

duckdb:
  database: lakehouse_catalog.duckdb
  install_extensions:
    - httpfs
    - iceberg
  
  secrets:
    - type: s3
      name: lakehouse_s3
      key_id: ${env:LAKEHOUSE_AWS_KEY}
      secret: ${env:LAKEHOUSE_AWS_SECRET}
      region: us-east-1
  
  iceberg_catalogs:
    - name: production_iceberg
      catalog_type: rest
      uri: https://iceberg.example.com
      # DuckDB will use S3 secret for S3 paths in this catalog

views:
  - name: iceberg_sales
    source: iceberg
    catalog: production_iceberg
    table: sales
    description: "Iceberg sales data using S3 secret"
```

## Production Deployment

### Docker Example

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY catalog.yaml .
COPY .env .

# Set environment variables
ENV AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
ENV AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
ENV AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}

CMD ["duckalog", "build", "catalog.yaml"]
```

### Kubernetes Example

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: duckdb-secrets
type: Opaque
stringData:
  AWS_ACCESS_KEY_ID: "AKIAIOSFODNN7EXAMPLE"
  AWS_SECRET_ACCESS_KEY: "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: duckalog-config
data:
  catalog.yaml: |
    version: 1
    duckdb:
      database: /data/duckdb.duckdb
      install_extensions:
        - httpfs
      secrets:
        - type: s3
          name: k8s_s3
          key_id: ${AWS_ACCESS_KEY_ID}
          secret: ${AWS_SECRET_ACCESS_KEY}
          region: us-west-2
      views:
        - name: app_data
          source: parquet
          uri: "s3://app-bucket/data/*.parquet"
---
apiVersion: v1
kind: Pod
metadata:
  name: duckalog-builder
spec:
  containers:
  - name: duckalog
    image: my-registry/duckalog:latest
    envFrom:
      - secretRef:
          name: duckdb-secrets
    volumeMounts:
      - name: config
        mountPath: /app/config.yaml
        subPath: catalog.yaml
  volumes:
    - name: config
      configMap:
        name: duckalog-config
```

This example shows how DuckDB secrets in Duckalog provide comprehensive credential management for external services, enabling secure and scalable data access patterns.