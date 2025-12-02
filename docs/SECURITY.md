# Security Documentation

This document outlines the security features and best practices for Duckalog, including both web UI security and path resolution security features.

## Overview

Duckalog includes comprehensive security hardening across multiple components:

- **Web UI Security**: Read-only SQL enforcement, authentication, and CORS protection
- **Path Resolution Security**: Validation against directory traversal and system access
- **Configuration Security**: Secure handling of credentials and file operations

## 🛡️ SQL Injection Protection

Duckalog implements comprehensive SQL injection protection through canonical quoting helpers and strict input validation.

### SQL Quoting Strategy

Duckalog uses two canonical functions for safe SQL construction:

#### **quote_ident()** - For Database Identifiers
- **Purpose**: Quote database, table, column, and view names
- **Protection**: Prevents identifier injection through proper escaping
- **Usage**: `view.database`, `view.table`, attachment aliases, catalog names

```python
from duckalog import quote_ident

# Safe identifier quoting
quote_ident("my_table")         # Returns: "my_table"
quote_ident("table; DROP...")   # Returns: "table; DROP..." (escaped, not executed)
quote_ident('user "events"')    # Returns: "user ""events""" (quotes escaped)
```

#### **quote_literal()** - For String Values
- **Purpose**: Quote string literals in SQL (paths, secrets, connection strings)
- **Protection**: Prevents SQL injection through proper string escaping
- **Usage**: File paths, secret values, connection strings, scope values

```python
from duckalog import quote_literal

# Safe literal quoting
quote_literal("user's data")      # Returns: "'user''s data'"
quote_literal("path/to/file")     # Returns: "'path/to/file'"
quote_literal("SELECT * FROM...") # Returns: "'SELECT * FROM...'" (not executed)
```

### Injection Attack Prevention

#### **View SQL Injection Protection**
```yaml
# ❌ MALICIOUS INPUT - BLOCKED
views:
  - name: evil
    source: duckdb
    database: '"; DROP TABLE users; --'
    table: 'bad_table'
    # Generated SQL: SELECT * FROM ""; DROP TABLE users; --"."bad_table"
    # The malicious SQL is safely quoted as identifiers, not executed

# ✅ LEGITIMATE INPUT - ALLOWED  
views:
  - name: sales_data
    source: duckdb
    database: my_database
    table: orders_2024
    # Generated SQL: SELECT * FROM "my_database"."orders_2024"
```

#### **Secret SQL Injection Protection**
```yaml
# ❌ MALICIOUS SECRET VALUE - BLOCKED
secrets:
  - type: s3
    name: evil_secret
    key_id: 'user'' OR 1=1 --'
    secret: 'malicious_value'
    # Generated SQL safely escapes quotes:
    # KEY_ID 'user'' OR 1=1 --' (not executed as SQL)
    # SECRET 'malicious_value' (safe)

# ✅ LEGITIMATE SECRET - ALLOWED
secrets:
  - type: s3
    name: prod_s3
    key_id: AKIA123456789
    secret: secret_key_abc123
    # Generated SQL: KEY_ID 'AKIA123456789', SECRET 'secret_key_abc123'
```

#### **Path SQL Injection Protection**
```python
# ❌ MALICIOUS PATH - BLOCKED
path = "../../../etc/passwd"
sql_path = normalize_path_for_sql(path)
# Returns: "'../../../etc/passwd'" (safe string literal)

# ✅ LEGITIMATE PATH - ALLOWED
path = "data/file.parquet"  
sql_path = normalize_path_for_sql(path)
# Returns: "'data/file.parquet'" (safe)
```

### Strict Type Enforcement

Duckalog enforces strict type checking for secret options to prevent unsafe object serialization:

```python
from duckalog import SecretConfig, generate_secret_sql

# ✅ ALLOWED TYPES
secret = SecretConfig(
    type="s3",
    options={
        "use_ssl": True,        # bool
        "timeout": 30,          # int  
        "rate_limit": 0.5,      # float
        "region": "us-west-2"   # str
    }
)
# This works fine

# ❌ BLOCKED TYPES
secret = SecretConfig(
    type="s3", 
    options={
        "bad_option": [1, 2, 3],      # list - BLOCKED
        "worse_option": {"key": "val"} # dict - BLOCKED
    }
)
generate_secret_sql(secret)  # Raises TypeError
```

### Security Guarantees

1. **Canonical API**: All SQL construction uses safe quoting helpers
2. **No Ad-hoc Quoting**: Prevents inconsistent or unsafe quoting patterns
3. **Type Safety**: Strict validation prevents unsafe object serialization
4. **Consistent Behavior**: Same quoting rules across all SQL generation
5. **Clear Error Messages**: Detailed TypeError messages for violations

### Security Testing

Test SQL injection protection:

```python
# Test malicious inputs are safely quoted
from duckalog import quote_ident, quote_literal, generate_view_sql, ViewConfig

# Test identifier injection
malicious_db = '"; DROP TABLE users; --'
sql = generate_view_sql(ViewConfig(
    name="test", source="duckdb", database=malicious_db, table="test_table"
))
assert "DROP TABLE" not in sql  # Injection blocked

# Test literal injection  
malicious_secret = "user' OR 1=1 --"
quoted = quote_literal(malicious_secret)
assert "OR 1=1" not in quoted  # Injection blocked
```

## 🔒 Path Resolution Security

Duckalog's path resolution feature includes robust security validation to prevent malicious file access while allowing legitimate use cases.

### Directory Traversal Protection

#### Security Threats Mitigated

**Excessive Parent Directory Traversal:**
```yaml
# ❌ BLOCKED - Attempts to access system files
views:
  - name: malicious
    source: parquet
    uri: ../../../../etc/passwd
```

**System Directory Access:**
```yaml
# ❌ BLOCKED - Attempts to access system directories
views:
  - name: system_config
    source: parquet
    uri: ../etc/config.parquet
    # Resolves to /etc/config.parquet - BLOCKED
```

**Security Violations Blocked:**
- `/etc/`, `/usr/`, `/bin/`, `/sbin/`, `/var/log/`, `/sys/`, `/proc/`
- Excessive parent directory traversal (more than 3 levels)
- Paths that resolve to system locations
- Invalid or malformed path sequences

#### Reasonable Traversal Allowed

The security model allows legitimate parent directory access within reasonable bounds:

```yaml
# ✅ ALLOWED - Reasonable parent directory access
views:
  - name: shared_data
    source: parquet
    uri: ../shared/data.parquet  # 1 level up - allowed
    
  - name: project_common
    source: parquet
    uri: ../../project/common.parquet  # 2 levels up - allowed
    
  - name: enterprise_data
    source: parquet
    uri: ../../../enterprise/data.parquet  # 3 levels up - allowed
```

### Path Type Detection

Duckalog automatically detects and handles different path types:

| Path Type | Security Considerations |
|-----------|------------------------|
| **Relative Paths** | Validated against traversal limits and system directories |
| **Absolute Paths** | Validated to ensure they don't point to dangerous locations |
| **Remote URIs** | Considered safe (S3, HTTP, etc.) - not subject to local file validation |
| **Windows Paths** | Cross-platform validation for Windows-specific patterns |

### Security Validation Process

1. **Path Detection**: Classify path as relative, absolute, or remote
2. **Resolution**: Convert relative paths to absolute paths
3. **Traversal Analysis**: Count and validate parent directory traversals
4. **Pattern Matching**: Check against dangerous location patterns
5. **File Access**: Validate file exists and is accessible
6. **Error Reporting**: Provide detailed security violation messages

### Security Error Handling

**Directory Traversal Violation:**
```json
{
  "error": "Path resolution violates security rules: '../../../etc/passwd' resolves to '/etc/passwd' which is outside reasonable bounds"
}
```

**System Directory Access Violation:**
```json
{
  "error": "Path resolution violates security rules: '../etc/config.parquet' resolves to dangerous location"
}
```

**File Access Issues:**
```json
{
  "error": "File does not exist: /path/to/missing.parquet"
}
```

### Security Configuration

Path resolution security is always enabled when path resolution is active:

```python
from duckalog import load_config

# Path resolution with security validation (default)
config = load_config("catalog.yaml", resolve_paths=True)

# Disable path resolution (no security validation needed)
config = load_config("catalog.yaml", resolve_paths=False)
```

### Security Best Practices for Paths

#### Project Structure Recommendations

```
project/
├── config/
│   └── catalog.yaml
├── data/
│   ├── raw/
│   ├── processed/
│   └── external/
├── databases/
│   └── reference.duckdb
└── shared/
    └── enterprise/
        └── common_data/
```

#### Secure Configuration Patterns

```yaml
# ✅ GOOD - Clear project structure
views:
  - name: local_data
    source: parquet
    uri: ./data/processed/events.parquet
    
  - name: shared_reference
    source: parquet
    uri: ../shared/enterprise/common_data/customers.parquet

# ❌ AVOID - Deep or unclear traversal
views:
  - name: unclear_data
    source: parquet
    uri: ../../../../some/deep/structure/data.parquet
```

#### Environment-Specific Security

**Development Environment:**
- Allow broader file access for development convenience
- Use relative paths for portable development setups

**Production Environment:**
- Restrict to well-defined data directories
- Use absolute paths or controlled relative paths
- Implement additional monitoring and logging

### Security Testing

#### Manual Security Testing

```python
from duckalog.path_resolution import validate_path_security
from pathlib import Path

# Test dangerous patterns
config_dir = Path("/project/config")

# Test cases that should fail
assert not validate_path_security("../../../etc/passwd", config_dir)
assert not validate_path_security("../usr/local/data.parquet", config_dir)

# Test cases that should succeed
assert validate_path_security("../shared/data.parquet", config_dir)
assert validate_path_security("./local/data.parquet", config_dir)
```

#### Automated Security Tests

The test suite includes comprehensive security validation:

```bash
# Run path resolution security tests
pytest tests/test_path_resolution.py -k "security"

# Test specific security scenarios
pytest tests/test_path_resolution.py::TestPathValidation
```

### Security Auditing

#### Logging

Path resolution security violations are logged with detailed information:

```python
# Security logging includes:
# - Original path that violated security
# - Resolved path that was blocked
# - Security rule that was violated
# - Configuration file location
```

#### Monitoring

Monitor for security violations in production:

1. **Log Analysis**: Look for path resolution security errors
2. **Access Patterns**: Monitor for unusual file access attempts
3. **Configuration Changes**: Track path configuration modifications
4. **Error Rates**: Alert on increased security violation rates

## 🛡️ Read-Only SQL Enforcement

### SQL Query Validation

The UI enforces strict read-only SQL execution to prevent data modification and database attacks:

#### **Allowed Operations**
- `SELECT` statements (single statement only)
- `WITH` clauses (Common Table Expressions)
- `JOIN`, `UNION`, `INTERSECT`, `EXCEPT` operations
- `WHERE`, `GROUP BY`, `HAVING`, `ORDER BY` clauses
- `LIMIT` and `OFFSET` clauses
- Subqueries and nested queries
- Window functions and aggregate functions

#### **Blocked Operations**

**DDL (Data Definition Language)**
- `CREATE` (TABLE, VIEW, INDEX, etc.)
- `DROP` (TABLE, VIEW, INDEX, etc.)
- `ALTER` (TABLE, etc.)
- `TRUNCATE`
- `RENAME`

**DML (Data Manipulation Language)**
- `INSERT`
- `UPDATE`
- `DELETE`
- `MERGE` / `UPSERT` / `REPLACE`
- `CALL` (stored procedures)

**Administrative Commands**
- `GRANT` / `REVOKE`
- `COMMENT`
- `EXPLAIN` / `DESCRIBE`
- `EXECUTE`

**Multi-Statement Queries**
- Any query containing multiple statements separated by semicolons
- Attempted SQL injection using statement chaining

### Security Error Messages

When queries are blocked, the system returns descriptive error messages:

```json
{
  "error": "Invalid query: DDL statements are not allowed for security reasons"
}
```

```json
{
  "error": "Invalid query: Only single SELECT statements are allowed"
}
```

### Examples

✅ **Allowed Queries:**
```sql
SELECT * FROM my_view WHERE id > 100
SELECT * FROM users JOIN orders ON users.id = orders.user_id
WITH ranked_data AS (SELECT *, ROW_NUMBER() OVER (ORDER BY created_at) as rn FROM my_table) SELECT * FROM ranked_data
```

❌ **Blocked Queries:**
```sql
DROP TABLE users
SELECT * FROM users; DELETE FROM users;
INSERT INTO logs VALUES ('hack attempt')
CALL malicious_procedure()
```

## 🔐 Authentication and Authorization

### Admin Token Protection

Mutating operations (POST, PUT, DELETE) require authentication in production mode:

```bash
# Set admin token for production
export DUCKALOG_ADMIN_TOKEN="your-secure-random-token"
```

#### **Protected Endpoints**
- `/api/config` (POST)
- `/api/views` (POST, PUT, DELETE)
- `/api/rebuild` (POST)

#### **Local Mode (Development)**
When running locally without an admin token, the UI operates in a permissive mode suitable for development.

#### **Production Mode**
When `DUCKALOG_ADMIN_TOKEN` is set, all mutating endpoints require:
```http
Authorization: Bearer your-secure-random-token
```

### Token Security Best Practices

1. **Use strong, random tokens** (minimum 32 characters)
2. **Rotate tokens regularly**
3. **Never commit tokens to version control**
4. **Use environment variables or secure secret management**
5. **Monitor for unauthorized access attempts**

## 🌐 CORS Policy

### Default Configuration

The UI implements restrictive CORS policies by default:

#### **Allowed Origins**
- `http://localhost`
- `http://127.0.0.1`
- Specific localhost ports (3000, 8000, 8080, 9000, 5173)

#### **Security Settings**
- **Credentials**: Disabled by default (`Access-Control-Allow-Credentials: false`)
- **Methods**: GET, POST, PUT, DELETE, OPTIONS
- **Headers**: Content-Type, Authorization

### Cross-Origin Protection

External domains are automatically blocked:
- ❌ `https://evil-site.com`
- ❌ `https://malicious-domain.net`
- ❌ Any non-localhost origin

### Customization

For production deployments, customize CORS settings in your deployment configuration:

```python
# Example: Custom allowed origins
cors_origins = ["https://your-trusted-domain.com"]
```

## 📁 Configuration Security

### Format Preservation

The UI preserves the original configuration file format (YAML/JSON) when making updates:

- **YAML files**: Maintain comments, formatting, and structure
- **JSON files**: Preserve pretty-printing and organization
- **Atomic writes**: Prevent configuration corruption

### Atomic Operations

All configuration updates use atomic file operations:
1. Write to temporary file
2. Validate the temporary file
3. Atomically move to target location
4. Clean up on failure

### In-Memory Reload

Configuration changes are immediately reflected in memory without requiring server restart.

## ⚡ Background Task Security

### Task Isolation

Database operations run in isolated background threads:
- Prevents UI blocking during long-running queries
- Isolates failures between concurrent operations
- Prevents resource exhaustion

### Task Result Management

- **Unique task IDs**: Prevent result collisions
- **Automatic cleanup**: Prevents memory leaks
- **Error isolation**: Failed tasks don't affect others
- **Timeout handling**: Prevents hanging operations

### Concurrent Operation Safety

Multiple users can safely:
- Run queries simultaneously
- Export data concurrently
- Rebuild catalogs without interference
- View and modify configurations independently

## 🔍 Security Monitoring

### Request Logging

All security-relevant actions are logged:
- Failed authentication attempts
- Blocked SQL queries
- CORS policy violations
- Configuration changes

### Error Handling

Security-sensitive errors don't expose internal details:
- Generic error messages for security violations
- No stack traces in production responses
- Proper HTTP status codes (401, 403, 400)

## 🚀 Production Deployment Security

### Environment Variables

```bash
# Required for production security
export DUCKALOG_ADMIN_TOKEN="your-secure-random-token"

# Optional: Custom CORS origins
export DUCKALOG_CORS_ORIGINS="https://yourdomain.com,https://app.yourdomain.com"
```

### Network Security

1. **Firewall**: Restrict access to UI port (default: 8000)
2. **HTTPS**: Use reverse proxy with SSL/TLS termination
3. **VPN**: Consider VPN access for internal deployments
4. **Network segmentation**: Isolate from sensitive systems

### Reverse Proxy Configuration

Example using nginx:

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    # SSL configuration
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🔧 Security Testing

The comprehensive test suite validates security features:

- **Read-only SQL enforcement** (`TestReadOnlySQLEnforcement`)
- **CORS policy validation** (`TestCORSPolicy`)
- **Authentication verification** (integrated tests)
- **Configuration security** (`TestConfigFormatPreservation`)
- **Background task isolation** (`TestBackgroundTaskConcurrency`)

Run security tests:

```bash
# Run all security-related tests
pytest tests/test_ui.py::TestReadOnlySQLEnforcement
pytest tests/test_ui.py::TestCORSPolicy
pytest tests/test_ui.py::TestConfigFormatPreservation

# Run all UI security tests
pytest tests/test_ui.py -k "security or auth or cors or read_only"
```

## 🚨 Security Considerations

### Database Security

- **Read-only database user**: Consider using read-only database credentials
- **Connection security**: Use SSL/TLS for database connections
- **Access control**: Limit database access to the UI server only

### Data Privacy

- **Sensitive data**: Avoid exposing PII in view definitions
- **Query logs**: Be aware that queries may be logged
- **Export limits**: Consider implementing export size limits

### Operational Security

- **Regular updates**: Keep dependencies updated
- **Monitoring**: Monitor for unusual activity patterns
- **Backup security**: Secure configuration backups
- **Access audit**: Regularly review access logs

## 🆘 Incident Response

### Security Incident Response

1. **Containment**: Immediately rotate admin tokens
2. **Analysis**: Review logs for unauthorized access
3. **Recovery**: Restart services with clean configuration
4. **Prevention**: Update security configurations
5. **Reporting**: Document and learn from incidents

### Contact Information

Report security vulnerabilities:
- Create an issue with "SECURITY" label
- Email security contacts (if provided)
- Follow responsible disclosure practices

---

*Last updated: Duckalog v0.1.0*