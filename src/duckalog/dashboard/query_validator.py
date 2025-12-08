"""SQL validation for dashboard query security."""

from __future__ import annotations

import re
from typing import List


class SQLValidator:
    """Validates SQL queries for read-only access and security."""

    # Keywords that are allowed (read-only operations)
    ALLOWED_KEYWORDS = {
        "SELECT",
        "WITH",  # CTEs
        "FROM",
        "JOIN",
        "INNER",
        "LEFT",
        "RIGHT",
        "FULL",
        "OUTER",
        "ON",
        "WHERE",
        "GROUP",
        "BY",
        "HAVING",
        "ORDER",
        "LIMIT",
        "OFFSET",
        "UNION",
        "INTERSECT",
        "EXCEPT",
        "DISTINCT",
        "AS",
        "AND",
        "OR",
        "NOT",
        "IN",
        "EXISTS",
        "BETWEEN",
        "LIKE",
        "ILIKE",
        "IS",
        "NULL",
        "TRUE",
        "FALSE",
        "CASE",
        "WHEN",
        "THEN",
        "ELSE",
        "END",
        "CAST",
        "EXTRACT",
        "SUBSTRING",
        "UPPER",
        "LOWER",
        "TRIM",
        "COALESCE",
        "NULLIF",
        # Aggregate functions
        "COUNT",
        "SUM",
        "AVG",
        "MIN",
        "MAX",
        # Window functions
        "OVER",
        "PARTITION",
        "ROW_NUMBER",
        "RANK",
        "DENSE_RANK",
        "LAG",
        "LEAD",
    }

    # Keywords that are NOT allowed (DML/DDL operations)
    FORBIDDEN_KEYWORDS = {
        "INSERT",
        "UPDATE",
        "DELETE",
        "CREATE",
        "ALTER",
        "DROP",
        "TRUNCATE",
        "GRANT",
        "REVOKE",
        "COMMIT",
        "ROLLBACK",
        "BEGIN",
        "TRANSACTION",
        "SAVEPOINT",
        "RELEASE",
        "SET",
        "SHOW",
        "DESCRIBE",
        "EXPLAIN",  # Can reveal schema information
        "PRAGMA",
        "ATTACH",
        "DETACH",
        "VACUUM",
        "REINDEX",
        "ANALYZE",
        "COPY",
        "IMPORT",
        "EXPORT",
        # DuckDB-specific potentially dangerous operations
        "INSTALL",
        "LOAD",
        "UNINSTALL",
        # File operations
        "EXPORT",
        "COPY",
    }

    @classmethod
    def validate_query(cls, sql: str) -> tuple[bool, str | None]:
        """
        Validate if a SQL query is read-only and safe to execute.

        Args:
            sql: SQL query to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not sql or not sql.strip():
            return False, "Empty SQL query"

        # Normalize SQL - remove extra whitespace and convert to uppercase for analysis
        normalized_sql = re.sub(r'\s+', ' ', sql.strip()).upper()

        # Check for forbidden keywords
        for forbidden in cls.FORBIDDEN_KEYWORDS:
            # Use word boundaries to avoid false positives (e.g., "column_name" containing "DROP")
            pattern = r'\b' + re.escape(forbidden) + r'\b'
            if re.search(pattern, normalized_sql, re.IGNORECASE):
                return False, f"Query contains forbidden keyword: {forbidden}. Only SELECT statements are allowed."

        # Check if query starts with SELECT or WITH (CTE)
        if not (normalized_sql.startswith('SELECT') or normalized_sql.startswith('WITH')):
            return False, "Query must start with SELECT or WITH (Common Table Expression)"

        # Additional safety checks
        dangerous_patterns = [
            r'--',           # SQL comments
            r'/\*',          # Multi-line comment start
            r'\*/',          # Multi-line comment end
            r';.*SELECT',    # Multiple statements
            r'SELECT.*;',    # Statement terminator after SELECT
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, normalized_sql, re.IGNORECASE | re.DOTALL):
                return False, "Query contains potentially dangerous syntax (comments or multiple statements)"

        # Check for function calls that might be dangerous
        dangerous_functions = [
            'LOAD_EXTENSION',
            'READ_FILE',
            'WRITE_FILE',
            'SCAN_PARQUET',
            'SCAN_CSV',
            # DuckDB-specific functions that might access files
        ]

        for func in dangerous_functions:
            if func.upper() in normalized_sql:
                return False, f"Query contains potentially dangerous function: {func}"

        return True, None

    @classmethod
    def sanitize_query(cls, sql: str) -> str:
        """
        Basic sanitization of SQL query.

        Args:
            sql: SQL query to sanitize

        Returns:
            Sanitized SQL query
        """
        # Remove comments
        sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
        sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)

        # Remove extra whitespace
        sql = re.sub(r'\s+', ' ', sql).strip()

        return sql


def validate_dashboard_query(sql: str) -> tuple[bool, str | None]:
    """
    Validate a dashboard query for security.

    This is the main entry point for query validation in the dashboard.

    Args:
        sql: SQL query to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    validator = SQLValidator()
    return validator.validate_query(sql)


__all__ = ["SQLValidator", "validate_dashboard_query"]