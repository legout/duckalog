# DuckDB Secrets Example

This example demonstrates how to use DuckDB secrets in Duckalog to manage credentials for external services like S3, Azure, GCS, and databases. Secrets provide a secure way to handle authentication without hardcoding credentials in SQL.

## Architecture Integration

Duckalog's secret management is built on the canonical `SecretConfig` model that integrates with DuckDB's `CREATE SECRET` functionality. This provides:

- **Unified Secret Handling**: Single configuration format across all secret types
- **Environment Variable Integration**: Secure credential management through `${env:VARIABLE}` patterns
- **DuckDB Native Integration**: Direct mapping to DuckDB `CREATE SECRET` statements
- **Cross-Platform Security**: Consistent behavior across different deployment environments

**Related Documentation:**
- [Architecture - Secret Management](../explanation/architecture.md#secret-management-architecture)
- [User Guide - Secret Management](../guides/usage.md#secret-management)

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
  
  # Secrets are defined within duckdb configuration
  secrets:
    - name: production_s3
      type: s3
      key_id: ${env:AWS_ACCESS_KEY_ID}
      secret: ${env:AWS_SECRET_ACCESS_KEY}
      region: us-west-2
      endpoint: s3.amazonaws.com  # Optional: custom endpoint

views:
  - name: sales_data
    source: parquet
    uri: "s3://my-production-bucket/sales/*.parquet"
```

### Azure Storage Secret

```yaml
version: 1

duckdb:
  database: azure_catalog.duckdb
  install_extensions:
    - httpfs
  
secrets:
  - name: azure_prod
    type: azure
    connection_string: ${env:AZURE_STORAGE_CONNECTION_STRING}
    account_name: ${env:AZURE_STORAGE_ACCOUNT}

views:
  - name: azure_logs
    source: parquet
    uri: "abfs://mycontainer/logs/*.parquet"
    description: "Azure blob storage logs using defined S3 secret"
```

### GCS Secret

```yaml
version: 1

duckdb:
  database: gcs_catalog.duckdb
  install_extensions:
    - httpfs
  
secrets:
  - name: gcs_service_account
    type: gcs
    service_account_key: ${env:GCS_SERVICE_ACCOUNT_JSON}

views:
  - name: gcs_data
    source: parquet
    uri: "gs://my-bucket/data/*.parquet"
    description: "GCS data using defined service account secret"
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
  - name: analytics_db
    type: postgres
    connection_string: ${env:DATABASE_URL}
    # Alternative: Individual parameters
    # host: localhost
    # port: 5432
    # database: analytics
    # user: ${env:PG_USER}
    # password: ${env:PG_PASSWORD}

views:
  - name: postgres_users
    source: postgres
    database: analytics_db
    table: users
```

#### MySQL Secret

```yaml
version: 1

duckdb:
  database: mysql_catalog.duckdb
  
secrets:
  - name: webapp_db
    type: postgres  # MySQL uses postgres secret type in DuckDB
    connection_string: ${env:MYSQL_DATABASE_URL}

views:
  - name: mysql_products
    source: postgres
    database: webapp_db
    table: products
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

### S3 Secret with Options

For advanced S3 configurations, use the `options` field to specify DuckDB-specific parameters:

```yaml
version: 1

duckdb:
  database: s3_advanced_catalog.duckdb
  install_extensions:
    - httpfs
  
  secrets:
    - type: s3
      name: advanced_s3
      key_id: ${env:LODL_ACCESS_KEY_ID}
      secret: ${env:LODL_SECRET_ACCESS_KEY}
      endpoint: ${env:LODL_ENDPOINT_URL}
      options:
        use_ssl: true                # Enable/disable SSL (default: true)
        url_style: path              # URL style: 'path' or 'virtual'
        session_token: ${env:AWS_SESSION_TOKEN}  # For temporary credentials
        region: us-east-1           # Override region in options

views:
  - name: advanced_data
    source: parquet
    uri: "s3://my-advanced-bucket/data/*.parquet"
    description: "Data from S3 with advanced options configuration"
```

**Common S3 Options:**
- `use_ssl`: Enable/disable SSL encryption (use `false` for local testing)
- `url_style`: URL style for S3-compatible storage (`path` for MinIO/other, `virtual` for standard AWS S3)
- `session_token`: AWS temporary session token
- `region`: AWS region override

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

## Understanding the Options Field

The `options` field is available for **all secret types** (S3, Azure, GCS, Database, HTTP) and allows you to specify additional key-value parameters that are specific to each secret type. This field is particularly useful for:

- **DuckDB-specific parameters**: Settings like `use_ssl`, `url_style` for S3
- **Service-specific options**: Custom parameters for different providers  
- **Advanced configurations**: Session tokens, custom headers, connection settings

### How the Options Field Works

The `options` field accepts a dictionary of key-value pairs:

```yaml
secrets:
  - type: s3
    name: my_secret
    key_id: ${env:MY_KEY}
    secret: ${env:MY_SECRET}
    options:
      # S3-specific parameters
      use_ssl: true
      url_style: path
      session_token: ${env:AWS_SESSION_TOKEN}
```

**Key Points:**
- `options` works the same way for all secret types
- The exact parameters available depend on the secret type
- Environment variables can be used within options values
- This field helps prevent validation errors when you need additional parameters

### Best Practices for Using Options

1. **Use Environment Variables**: Keep secrets secure by using environment variables within options:
   ```yaml
   options:
     session_token: ${env:AWS_SESSION_TOKEN}
   ```

2. **Documentation First**: Check if a parameter is supported by the underlying service before adding it to options

3. **Consistent Configuration**: Use similar option patterns across different secret types when available

4. **Testing**: Test options configuration in non-production environments first

5. **Version Control**: Document which options are required for your specific setup

### S3 Options Usage Examples

Different configurations require different S3 options. Here are common scenarios:

#### MinIO/S3-Compatible Storage
```yaml
secrets:
  - type: s3
    name: minio_storage
    key_id: ${env:MINIO_ACCESS_KEY}
    secret: ${env:MINIO_SECRET_KEY}
    endpoint: http://minio-server:9000
    options:
      use_ssl: false          # Often disabled for local MinIO
      url_style: path          # Path style common for MinIO
```

#### AWS S3 with Session Token
```yaml
secrets:
  - type: s3
    name: aws_s3_temp
    key_id: ${env:AWS_ACCESS_KEY_ID}
    secret: ${env:AWS_SECRET_ACCESS_KEY}
    region: us-east-1
    options:
      session_token: ${env:AWS_SESSION_TOKEN}
      url_style: virtual        # Virtual style for standard AWS S3
```

#### Custom S3 Endpoint
```yaml
secrets:
  - type: s3
    name: custom_endpoint
    key_id: ${env:MY_ACCESS_KEY}
    secret: ${env:MY_SECRET_KEY}
    endpoint: https://s3.example.com
    options:
      use_ssl: true
      region: custom-region-1
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
| `options` | Optional | Additional S3-specific parameters (e.g., `use_ssl`, `url_style`) |

### Azure Secret Fields

| Field | Required | Description |
|--------|-----------|-------------|
| `type` | Yes | Must be `"azure"` |
| `connection_string` | Either/or | Full connection string |
| `tenant_id` | Either/or | Azure AD tenant ID |
| `account_name` | Either/or | Storage account name |
| `secret` | For explicit auth | Account key or password |
| `scope` | Optional | URL prefix for secret scope |
| `options` | Optional | Additional Azure-specific parameters |

### GCS Secret Fields

| Field | Required | Description |
|--------|-----------|-------------|
| `type` | Yes | Must be `"gcs"` |
| `key_id` | For `config` provider | Service account email |
| `secret` | For `config` provider | Private key content |
| `endpoint` | Optional | Custom GCS endpoint |
| `scope` | Optional | URL prefix for secret scope |
| `options` | Optional | Additional GCS-specific parameters |

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
| `options` | Optional | Additional database-specific parameters |

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