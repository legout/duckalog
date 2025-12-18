# Managing Secrets Persistence

This guide explains how to configure secrets persistence in Duckalog, covering the security implications of temporary versus persistent secrets, configuration examples, and best practices for secure secret management.

## Overview: Temporary vs Persistent Secrets

Duckalog supports two modes for secrets persistence, each with distinct security implications:

### Temporary Secrets (Default)

**Behavior:**
- Secrets exist only for the current session
- Automatically removed when the database connection closes
- Secrets are not persisted to disk
- Must be recreated on each application restart

**Security Implications:**
- ✅ **Higher Security**: Secrets never persist beyond session lifetime
- ✅ **Reduced Exposure**: Limited window for credential compromise
- ✅ **No Storage**: No secrets stored in database files
- ❌ **Performance Overhead**: Secrets recreated on every startup
- ❌ **Inconvenience**: Must manage secret availability on each run

**When to Use:**
- Development and testing environments
- Short-lived processes (CI/CD pipelines, data processing jobs)
- High-security environments where credential exposure must be minimized
- Applications with frequent restarts

### Persistent Secrets (Opt-in)

**Behavior:**
- Secrets are persisted to the DuckDB database
- Survive database connection closures and application restarts
- Available automatically when database is opened
- Must be explicitly enabled via `persistent: true`

**Security Implications:**
- ✅ **Convenience**: Automatic availability on restart
- ✅ **Performance**: No recreation overhead
- ✅ **Stability**: Consistent secret availability
- ⚠️ **Security Risk**: Secrets stored in database file
- ⚠️ **File Exposure**: Database file contains encrypted secrets
- ⚠️ **Access Control**: Database file becomes high-value target

**When to Use:**
- Production services with long-running operations
- Automated batch processes that restart frequently
- Environments where secret management overhead is problematic
- Services where database file security can be guaranteed

## Configuration Examples

### Default: Temporary Secrets

```yaml
version: 1

duckdb:
  database: analytics_catalog.duckdb
  install_extensions:
    - httpfs
  
  # Temporary secrets (default)
  secrets:
    - type: s3
      name: production_s3
      key_id: ${env:AWS_ACCESS_KEY_ID}
      secret: ${env:AWS_SECRET_ACCESS_KEY}
      region: us-west-2
      
    - type: postgres
      name: analytics_db
      connection_string: ${env:DATABASE_URL}

views:
  - name: sales_data
    source: parquet
    uri: "s3://prod-bucket/sales/*.parquet"
    
  - name: customers
    source: postgres
    database: analytics_db
    table: customers
```

**Behavior:** Secrets `production_s3` and `analytics_db` exist only during the current session.

### Explicit Temporary Secrets

```yaml
duckdb:
  database: analytics_catalog.duckdb
  secrets:
    - type: s3
      name: production_s3
      key_id: ${env:AWS_ACCESS_KEY_ID}
      secret: ${env:AWS_SECRET_ACCESS_KEY}
      persistent: false  # Explicitly temporary
      region: us-west-2
```

### Persistent Secrets (Opt-in)

```yaml
version: 1

duckdb:
  database: production_catalog.duckdb
  install_extensions:
    - httpfs
  
  # Persistent secrets
  secrets:
    - type: s3
      name: production_s3
      key_id: ${env:AWS_ACCESS_KEY_ID}
      secret: ${env:AWS_SECRET_ACCESS_KEY}
      persistent: true  # Enable persistence
      region: us-west-2
      
    - type: azure
      name: azure_storage
      connection_string: ${env:AZURE_STORAGE_CONNECTION_STRING}
      account_name: ${env:AZURE_STORAGE_ACCOUNT}
      persistent: true  # Enable persistence

views:
  - name: production_data
    source: parquet
    uri: "s3://prod-bucket/data/*.parquet"
    
  - name: azure_logs
    source: parquet
    uri: "abfs://logs@storageaccount.dfs.core.windows.net/*.parquet"
```

**Behavior:** Secrets `production_s3` and `azure_storage` persist in the database file and are automatically available on restart.

### Mixed Configuration

```yaml
version: 1

duckdb:
  database: hybrid_catalog.duckdb
  install_extensions:
    - httpfs
  
  secrets:
    # Production secret - persistent for stability
    - type: s3
      name: prod_data_lake
      key_id: ${env:PROD_AWS_KEY}
      secret: ${env:PROD_AWS_SECRET}
      persistent: true
      region: us-east-1
      
    # Development secret - temporary for security
    - type: s3
      name: dev_test_bucket
      key_id: ${env:DEV_AWS_KEY}
      secret: ${env:DEV_AWS_SECRET}
      persistent: false  # Temporary
      region: us-west-2
      
    # Database connection - temporary for rotation flexibility
    - type: postgres
      name: analytics_db
      connection_string: ${env:DATABASE_URL}
      persistent: false  # Temporary (default)

views:
  - name: production_metrics
    source: parquet
    uri: "s3://prod-data-lake/metrics/*.parquet"
    
  - name: dev_experiments
    source: parquet
    uri: "s3://dev-test-bucket/experiments/*.parquet"
    
  - name: analytics_data
    source: postgres
    database: analytics_db
    table: events
```

## Security Best Practices

### Why Temporary Secrets are Default

Duckalog defaults to temporary secrets for security reasons:

1. **Principle of Least Persistence**: Secrets should persist only as long as necessary
2. **Reduced Attack Surface**: Temporary secrets limit the window for credential theft
3. **No Database File Exposure**: Database files don't contain sensitive credentials
4. **Forced Secret Management**: Requires explicit secret management processes
5. **Environment Alignment**: Aligns with modern secret management practices

### When to Use Persistent Secrets

Consider persistent secrets only when:

1. **Controlled Environment**: Database files are properly secured
2. **Operational Need**: Frequent restarts create operational overhead
3. **Access Control**: Database file access is restricted to authorized personnel
4. **Encryption at Rest**: Database file encryption is implemented
5. **Compliance Requirements**: Persistent storage doesn't violate security policies

### Security Considerations

#### For Temporary Secrets:

```yaml
# Good: Temporary secrets with environment variables
secrets:
  - type: s3
    name: sensitive_data
    key_id: ${env:TEMP_ACCESS_KEY}
    secret: ${env:TEMP_SECRET_KEY}
    # persistent: false (default)
```

**Security Benefits:**
- Secrets exist only in memory during session
- No credential storage in database files
- Automatic cleanup on connection close
- Reduced risk from database file compromise

**Operational Requirements:**
- Environment variables must be available on each run
- Secret management system must provide credentials at startup
- Process restart requires secret availability

#### For Persistent Secrets:

```yaml
# Careful: Persistent secrets require additional security
secrets:
  - type: s3
    name: production_data
    key_id: ${env:PROD_ACCESS_KEY}
    secret: ${env:PROD_SECRET_KEY}
    persistent: true  # Use with caution
    scope: "s3://production-bucket/"  # Limit scope when possible
```

**Security Requirements:**
- **Database File Protection**: Strict access controls on `.duckdb` files
- **Encryption at Rest**: Database files stored on encrypted filesystems
- **Backup Security**: Encrypted backups with limited access
- **Audit Logging**: Track database file access and modifications
- **Access Control**: Only authorized services can access database files

### Migration Strategies

#### From Temporary to Persistent

```bash
# 1. Backup existing configuration
cp catalog.yaml catalog.yaml.backup

# 2. Update configuration to enable persistence
# Edit catalog.yaml to add persistent: true to specific secrets

# 3. Rebuild catalog with persistent secrets
duckalog build catalog.yaml

# 4. Verify persistence by restarting and testing
duckalog serve catalog.yaml
# Test access after restart
```

#### From Persistent to Temporary

```bash
# 1. Clear existing persistent secrets
duckalog execute catalog.yaml "DROP SECRET IF EXISTS secret_name;"

# 2. Update configuration to remove persistence
# Edit catalog.yaml to remove persistent: true or set to false

# 3. Rebuild with temporary secrets
duckalog build catalog.yaml
```

## DuckDB Compatibility

### Current Limitations

#### SCOPE Not Supported

```yaml
# ❌ NOT SUPPORTED - SCOPE configuration
secrets:
  - type: s3
    name: scoped_s3
    key_id: ${env:AWS_ACCESS_KEY_ID}
    secret: ${env:AWS_SECRET_ACCESS_KEY}
    scope: "s3://specific-bucket/prefix/"  # Not supported in current DuckDB
```

**Workaround:** Use more granular secrets with limited permissions:

```yaml
# ✅ WORKAROUND - Multiple secrets for different buckets
secrets:
  - type: s3
    name: bucket_read_only
    key_id: ${env:READ_ONLY_KEY}
    secret: ${env:READ_ONLY_SECRET}
    # Limited IAM permissions for specific buckets
    
  - type: s3
    name: bucket_write_access
    key_id: ${env:WRITE_ACCESS_KEY}
    secret: ${env:WRITE_ACCESS_SECRET}
    # Limited IAM permissions for write operations
```

#### HTTP Secrets BEARER_TOKEN Only

```yaml
# ✅ SUPPORTED - HTTP secrets with bearer tokens
secrets:
  - type: http
    name: api_access
    bearer_token: ${env:API_BEARER_TOKEN}
    # Only BEARER_TOKEN is supported for HTTP secrets

# ❌ NOT SUPPORTED - Other HTTP authentication
secrets:
  - type: http
    name: api_basic_auth
    key_id: ${env:API_USERNAME}
    secret: ${env:API_PASSWORD}
    # Basic auth not supported for HTTP secrets
```

### Future Compatibility Notes

Duckalog is designed to accommodate future DuckDB enhancements:

#### Future SCOPE Support
When DuckDB adds SCOPE support, existing configurations will automatically work:

```yaml
# This will work when DuckDB supports SCOPE
secrets:
  - type: s3
    name: future_scoped_secret
    key_id: ${env:AWS_ACCESS_KEY_ID}
    secret: ${env:AWS_SECRET_ACCESS_KEY}
    scope: "s3://allowed-bucket/"  # Future support planned
```

#### Enhanced HTTP Authentication
Future DuckDB versions may support additional HTTP authentication methods.

#### Migration Path
Existing configurations will remain compatible when new features are added.

## Implementation Details

### How the Persistent Flag Works

The `persistent` flag controls DuckDB's `CREATE SECRET` behavior:

#### Temporary Secrets (Default)
```sql
-- Generated SQL for temporary secrets
CREATE TEMPORARY SECRET s3_prod (
    TYPE S3,
    KEY_ID 'AKIAIOSFODNN7EXAMPLE',
    SECRET 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
    REGION 'us-west-2'
);
```

#### Persistent Secrets
```sql
-- Generated SQL for persistent secrets
CREATE SECRET s3_prod (
    TYPE S3,
    KEY_ID 'AKIAIOSFODNN7EXAMPLE',
    SECRET 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
    REGION 'us-west-2'
);
```

**Key Differences:**
- `TEMPORARY` keyword indicates session-only existence
- No `TEMPORARY` keyword means persistence to database

### Secret Recreation Behavior

#### Temporary Secrets
1. **Created**: When Duckalog processes configuration
2. **Available**: During current database session
3. **Destroyed**: When database connection closes
4. **Recreated**: On next catalog build/session

#### Persistent Secrets
1. **Created**: When Duckalog processes configuration
2. **Persisted**: Stored in DuckDB database file
3. **Available**: Automatically when database opens
4. **Updated**: Replaced if configuration changes

### Connection Management Integration

Secrets integrate with Duckalog's connection management:

#### Session Management
```python
from duckalog import build_catalog

# Temporary secrets - session-bound
catalog = build_catalog("catalog.yaml")  # Secrets created
catalog.close()  # Secrets destroyed with connection

# Persistent secrets - database-bound
catalog = build_catalog("persistent_catalog.yaml")  # Secrets created and persisted
catalog.close()  # Secrets remain in database
```

#### Error Handling
Secret creation failures are handled gracefully:

```python
# Secret creation errors are reported clearly
try:
    catalog = build_catalog("catalog.yaml")
except DuckDBError as e:
    if "CREATE SECRET" in str(e):
        print("Secret creation failed - check credentials")
    raise
```

### Performance Considerations

#### Temporary Secrets Impact
- **Startup Cost**: Secrets recreated on each session
- **Memory Usage**: Secrets exist only in memory
- **Network Load**: Potential credential verification on each startup

#### Persistent Secrets Impact
- **Startup Cost**: Secrets loaded from database (faster)
- **Storage Usage**: Database file includes secret metadata
- **Memory Usage**: Secrets loaded into memory at startup

## Monitoring and Troubleshooting

### Monitoring Secret Usage

#### SQL Monitoring
```sql
-- List all current secrets
SELECT name, type, persistent FROM duckdb_secrets();

-- Check specific secret details
SELECT * FROM duckdb_secrets() WHERE name = 'production_s3';

-- Monitor secret creation
SELECT * FROM duckdb_secrets() WHERE created_at >= CURRENT_DATE;
```

#### Application Logging
```bash
# Enable verbose logging for secret operations
duckalog build catalog.yaml --log-level DEBUG

# Look for secret-related messages
grep -i "secret" /var/log/duckalog.log
```

### Common Issues

#### Secret Not Found After Restart
```bash
Error: Catalog Error: Secret with name 'production_s3' does not exist
```

**Cause:** Secret was temporary and not recreated
**Solution:** Check secret configuration and environment variables

#### Persistent Secret Not Working
```bash
Error: Permission denied accessing s3://bucket/data
```

**Cause:** Persistent secret may have outdated credentials
**Solution:** Update secret configuration and rebuild

#### Environment Variable Issues
```bash
Error: Environment variable 'AWS_ACCESS_KEY_ID' not set
```

**Solution:** Ensure environment variables are available:
```bash
export AWS_ACCESS_KEY_ID="your_key"
export AWS_SECRET_ACCESS_KEY="your_secret"
```

### Debugging Secret Configuration

#### Test Secret Creation
```python
from duckalog import load_config, generate_secret_sql

config = load_config("catalog.yaml")
for secret in config.duckdb.secrets:
    sql = generate_secret_sql(secret)
    print(f"Secret SQL for {secret.name}:")
    print(sql)
    print()
```

#### Validate Secret Access
```bash
# Test secret access without building full catalog
duckalog execute catalog.yaml "SELECT * FROM duckdb_secrets();"

# Test file access with secret
duckalog execute catalog.yaml "SELECT * FROM read_csv_auto('s3://bucket/test.csv') LIMIT 1;"
```

## Security Checklist

### Before Using Persistent Secrets

- [ ] Database file access is restricted to authorized users
- [ ] Database files are stored on encrypted filesystems
- [ ] Backup processes include proper encryption
- [ ] Database file integrity is monitored
- [ ] Secret rotation procedures are documented
- [ ] Access logging is enabled and monitored
- [ ] Security policies allow credential persistence
- [ ] Compliance requirements are satisfied

### For Temporary Secrets

- [ ] Environment variables are available at startup
- [ ] Secret management system provides credentials
- [ ] Process restart procedures include secret availability
- [ ] Development environment secret management is established
- [ ] CI/CD pipeline secret injection is configured

### Ongoing Security Practices

- [ ] Regular secret rotation is implemented
- [ ] Database file access is audited
- [ ] Secret usage patterns are monitored
- [ ] Backup security procedures are tested
- [ ] Security incident response includes secret handling
- [ ] Documentation is kept up-to-date
- [ ] Team security training includes secret management

---

## Related Documentation

- [DuckDB Secrets Example](../examples/duckdb-secrets.md)
- [Configuration Schema Reference](../reference/config-schema.md#secrets-configuration)
- [Security Documentation](../SECURITY.md)
- [User Guide - Secret Management](../guides/usage.md#secret-management)
- [Architecture - Secret Management](../explanation/architecture.md#secret-management-architecture)