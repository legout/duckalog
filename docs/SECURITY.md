# Security Documentation

This document outlines the security features and best practices for Duckalog's web UI.

## Overview

Duckalog's web UI includes comprehensive security hardening to ensure safe operation in production environments. The security model focuses on read-only data access, secure configuration management, and controlled web access.

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