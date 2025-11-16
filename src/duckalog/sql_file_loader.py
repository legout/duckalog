"""SQL file loader utility for Duckalog.

This module provides functionality to load SQL content from external files,
including support for templates with variable substitution.
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, Optional, Set
from urllib.parse import quote

from pydantic import BaseModel, Field, ValidationError

from .config import ConfigError


class SQLFileError(ConfigError):
    """Base exception for SQL file-related errors."""

    pass


class SQLFileNotFoundError(SQLFileError):
    """Raised when a referenced SQL file does not exist."""

    pass


class SQLFilePermissionError(SQLFileError):
    """Raised when a SQL file cannot be read due to permissions."""

    pass


class SQLFileEncodingError(SQLFileError):
    """Raised when a SQL file has invalid encoding."""

    pass


class SQLFileSizeError(SQLFileError):
    """Raised when a SQL file exceeds size limits."""

    pass


class SQLTemplateError(SQLFileError):
    """Raised when template processing fails."""

    pass


class TemplateProcessor:
    """Handles variable substitution in SQL templates.

    Supports three types of variable substitution:
    - {{ variable_name }} - Direct variable replacement
    - ${env:ENV_VAR} - Environment variable substitution
    - ${config:config_path} - Configuration value substitution
    """

    def __init__(self, variables: Optional[Dict[str, Any]] = None):
        self.variables = variables or {}

    def process(
        self, template: str, config_vars: Optional[Dict[str, Any]] = None
    ) -> str:
        """Process a SQL template with variable substitution.

        Args:
            template: SQL template string with {{ variable }} placeholders
            config_vars: Configuration variables for substitution

        Returns:
            Processed SQL string with variables substituted

        Raises:
            SQLTemplateError: If template processing fails
        """
        result = template

        # Process {{ variable }} substitutions
        result = self._substitute_variables(result, config_vars)

        # Process ${env:ENV_VAR} substitutions
        result = self._substitute_env_vars(result)

        # Process ${config:config_path} substitutions
        result = self._substitute_config_vars(result, config_vars)

        return result

    def _substitute_variables(
        self, template: str, config_vars: Optional[Dict[str, Any]]
    ) -> str:
        """Substitute {{ variable }} placeholders."""

        # Match {{ variable_name }} pattern
        pattern = r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}"

        # Extract all template variables
        template_vars = re.findall(pattern, template)

        # If template contains variables but no config provided, error
        if template_vars and config_vars is None:
            raise SQLTemplateError(
                f"Template contains variables but no config variables provided: {template_vars}"
            )

        # If template contains variables but config is empty dict, error
        if template_vars and config_vars is not None and not config_vars:
            raise SQLTemplateError(
                f"Template contains variables but config variables is empty: {template_vars}"
            )

        def replace_var(match):
            var_name = match.group(1).strip()
            # Check if config_vars is None (already handled above) or if variable is missing
            if config_vars is None or var_name not in config_vars:
                raise SQLTemplateError(f"Undefined template variable: {var_name}")
            return str(config_vars[var_name])

        result = re.sub(pattern, replace_var, template)
        return result

    def _substitute_env_vars(self, template: str) -> str:
        """Substitute ${env:ENV_VAR} placeholders."""

        def replace_env(match):
            var_name = match.group(1).strip()
            value = os.environ.get(var_name)
            if value is None:
                raise SQLTemplateError(f"Environment variable '{var_name}' not found")
            return value

        # Match ${env:ENV_VAR} pattern
        pattern = r"\$\{env:([a-zA-Z_][a-zA-Z0-9_]*)\}"
        return re.sub(pattern, replace_env, template)

    def _substitute_config_vars(
        self, template: str, config_vars: Optional[Dict[str, Any]]
    ) -> str:
        """Substitute ${config:config_path} placeholders."""
        if not config_vars:
            return template

        def replace_config(match):
            path = match.group(1).strip()
            # Simple dot-path resolution
            parts = path.split(".")
            value = config_vars
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    raise SQLTemplateError(f"Config path '{path}' not found")
            return str(value)

        # Match ${config:config_path} pattern
        pattern = r"\$\{config:([a-zA-Z_.][a-zA-Z0-9_.]*)\}"
        return re.sub(pattern, replace_config, template)


class PathResolver:
    """Resolves relative and absolute file paths with security validation."""

    # Set of allowed file extensions
    ALLOWED_EXTENSIONS = {".sql"}

    def __init__(self, allowed_base_paths: Optional[Set[str]] = None):
        """Initialize path resolver.

        Args:
            allowed_base_paths: Set of allowed base paths for SQL files.
                              If None, allows paths relative to config file location.
        """
        self.allowed_base_paths = allowed_base_paths or set()

    def resolve_path(
        self, sql_file_path: str, config_file_path: Optional[str] = None
    ) -> Path:
        """Resolve a SQL file path with security checks.

        Args:
            sql_file_path: Path to the SQL file (relative or absolute)
            config_file_path: Path to the configuration file (for relative resolution)

        Returns:
            Resolved Path object

        Raises:
            SQLFileError: If path resolution fails or security check fails
        """
        try:
            if os.path.isabs(sql_file_path):
                # Absolute path - validate against allowed base paths
                path = Path(sql_file_path).resolve()
                if self.allowed_base_paths:
                    self._validate_absolute_path(path)
                else:
                    self._validate_absolute_path_security(path)
            else:
                # Relative path - resolve relative to config file location
                if not config_file_path:
                    raise SQLFileError(
                        f"Relative SQL file path '{sql_file_path}' requires config file path for resolution"
                    )

                config_dir = Path(config_file_path).parent
                path = (config_dir / sql_file_path).resolve()

            # Validate the resolved path
            self._validate_path(path)
            return path

        except (ValueError, OSError) as e:
            raise SQLFileError(
                f"Failed to resolve SQL file path '{sql_file_path}': {e}"
            )

    def _validate_absolute_path(self, path: Path) -> None:
        """Validate absolute path against allowed base paths."""
        if not any(
            str(path).startswith(base_path) for base_path in self.allowed_base_paths
        ):
            raise SQLFileError(
                f"SQL file path '{path}' is outside allowed base paths: {list(self.allowed_base_paths)}"
            )

    def _validate_absolute_path_security(self, path: Path) -> None:
        """Validate absolute path for security issues."""
        # Basic security checks for absolute paths
        if ".." in str(path).split("/"):
            raise SQLFileError(f"SQL file path '{path}' contains directory traversal")

    def _validate_path(self, path: Path) -> None:
        """Validate a resolved path."""
        if not path.exists():
            raise SQLFileNotFoundError(f"SQL file not found: {path}")

        if not path.is_file():
            raise SQLFileError(f"Path is not a file: {path}")

        # Check file extension
        if path.suffix.lower() not in self.ALLOWED_EXTENSIONS:
            raise SQLFileError(f"SQL file must have .sql extension, got: {path.suffix}")

        # Check if file is readable
        if not os.access(path, os.R_OK):
            raise SQLFilePermissionError(f"SQL file is not readable: {path}")


class SQLFileLoader:
    """Loads and validates SQL files for use in Duckalog configurations.

    This class handles:
    - Loading SQL content from external files
    - Template processing with variable substitution
    - Security validation and path resolution
    - File encoding and size validation
    """

    # Default maximum file size (10MB)
    DEFAULT_MAX_SIZE_BYTES = 10 * 1024 * 1024

    def __init__(
        self,
        max_size_bytes: int = DEFAULT_MAX_SIZE_BYTES,
        allowed_base_paths: Optional[Set[str]] = None,
        cache_enabled: bool = True,
    ):
        """Initialize SQL file loader.

        Args:
            max_size_bytes: Maximum allowed file size in bytes
            allowed_base_paths: Set of allowed base paths for SQL files
            cache_enabled: Whether to enable file content caching
        """
        self.max_size_bytes = max_size_bytes
        self.allowed_base_paths = allowed_base_paths or set()
        self.cache_enabled = cache_enabled
        self._path_resolver = PathResolver(allowed_base_paths)
        self._cache: Dict[str, str] = {}

    def load_sql_file(
        self,
        file_path: str,
        config_file_path: Optional[str] = None,
        variables: Optional[Dict[str, Any]] = None,
        as_template: bool = False,
    ) -> str:
        """Load SQL content from a file.

        Args:
            file_path: Path to the SQL file (relative or absolute)
            config_file_path: Path to the configuration file (for relative resolution)
            variables: Variables for template substitution
            as_template: Whether to process the content as a template

        Returns:
            SQL content (with template variables substituted if applicable)

        Raises:
            SQLFileError: If file loading or processing fails
        """
        # Resolve the file path
        resolved_path = self._path_resolver.resolve_path(file_path, config_file_path)

        # Check cache first
        cache_key = f"{resolved_path}:{hash(str(variables))}:{as_template}"
        if self.cache_enabled and cache_key in self._cache:
            return self._cache[cache_key]

        # Load the file content
        content = self._load_file_content(resolved_path)

        # Process as template if requested
        if as_template and content:
            processor = TemplateProcessor()
            content = processor.process(content, variables)

        # Cache the result
        if self.cache_enabled:
            self._cache[cache_key] = content

        return content

    def _load_file_content(self, path: Path) -> str:
        """Load and validate file content.

        Args:
            path: Path to the SQL file

        Returns:
            File content as string

        Raises:
            SQLFileError: If file content validation fails
        """
        try:
            # Check file size
            file_size = path.stat().st_size
            if file_size > self.max_size_bytes:
                raise SQLFileSizeError(
                    f"SQL file '{path}' exceeds maximum size of {self.max_size_bytes} bytes "
                    f"(actual size: {file_size} bytes)"
                )

            # Read file with explicit UTF-8 encoding
            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError as e:
                raise SQLFileEncodingError(f"SQL file '{path}' is not valid UTF-8: {e}")

            # Basic content validation
            if not content.strip():
                raise SQLFileError(f"SQL file '{path}' is empty")

            # Check for potential security issues
            self._validate_content_security(content, path)

            return content

        except (OSError, IOError) as e:
            raise SQLFileError(f"Failed to read SQL file '{path}': {e}")

    def _validate_content_security(self, content: str, path: Path) -> None:
        """Validate file content for security issues.

        Args:
            content: File content to validate
            path: Path to the file (for error reporting)

        Raises:
            SQLFileError: If content validation fails
        """
        # Check for potentially dangerous SQL constructs
        dangerous_patterns = [
            r"DROP\s+DATABASE",
            r"DROP\s+SCHEMA",
            r"DROP\s+USER",
            r"DROP\s+ROLE",
            r"GRANT\s+.*\s+TO",
            r"REVOKE\s+.*\s+FROM",
        ]

        content_upper = content.upper()
        for pattern in dangerous_patterns:
            if re.search(pattern, content_upper):
                raise SQLFileError(
                    f"SQL file '{path}' contains potentially dangerous SQL: {pattern}"
                )

        # Check for excessive length (basic SQL injection attempt detection)
        if len(content) > 100000:  # 100KB
            # This is just a warning, not an error
            pass

    def clear_cache(self) -> None:
        """Clear the file content cache."""
        self._cache.clear()

    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about the current cache state.

        Returns:
            Dictionary with cache statistics
        """
        return {
            "enabled": self.cache_enabled,
            "entries": len(self._cache),
            "total_size": sum(len(content) for content in self._cache.values()),
        }


# Convenience function for backward compatibility
def load_sql_from_file(
    file_path: str,
    config_file_path: Optional[str] = None,
    variables: Optional[Dict[str, Any]] = None,
    max_size_bytes: int = SQLFileLoader.DEFAULT_MAX_SIZE_BYTES,
) -> str:
    """Convenience function to load SQL from a file.

    This function provides a simple interface for loading SQL files
    without requiring instantiation of the SQLFileLoader class.

    Args:
        file_path: Path to the SQL file
        config_file_path: Path to the configuration file (for relative resolution)
        variables: Variables for template substitution
        max_size_bytes: Maximum allowed file size

    Returns:
        SQL content with template variables substituted

    Raises:
        SQLFileError: If file loading or processing fails
    """
    loader = SQLFileLoader(max_size_bytes=max_size_bytes)
    as_template = variables is not None
    return loader.load_sql_file(file_path, config_file_path, variables, as_template)
