"""Configuration loading orchestration for Duckalog catalogs.

This module provides the main entry points for loading and processing configuration files,
handling both local file loading and remote URI loading.
"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml

from duckalog.errors import (
    CircularImportError,
    ConfigError,
    DuplicateNameError,
    ImportError,
    ImportFileNotFoundError,
    ImportValidationError,
    PathResolutionError,
)
from .validators import log_info, log_debug


def _interpolate_env(value: Any) -> Any:
    """Simple stub for environment variable interpolation."""
    if isinstance(value, str):
        # Simple ${env:VAR} replacement (basic implementation)
        import re
        import os

        pattern = re.compile(r"\$\{env:([A-Za-z_][A-Za-z0-9_]*)\}")

        def replace_env_match(match: Any) -> str:
            var_name = match.group(1)
            try:
                return os.environ[var_name]
            except KeyError as exc:
                raise ConfigError(
                    f"Environment variable '{var_name}' is not set"
                ) from exc

        return pattern.sub(replace_env_match, value)
    if isinstance(value, list):
        return [_interpolate_env(item) for item in value]
    if isinstance(value, dict):
        return {key: _interpolate_env(val) for key, val in value.items()}
    return value


def _load_sql_files_from_config(
    config: Any, config_path: Path, sql_file_loader: Optional[Any] = None
) -> Any:
    """Load SQL content from external files referenced in the config.

    This function processes views that reference external SQL files or templates
    and inlines the SQL content into the configuration.

    Args:
        config: The configuration object to process
        config_path: Path to the configuration file (for relative path resolution)
        sql_file_loader: Optional SQLFileLoader instance for loading SQL files

    Returns:
        Updated configuration with SQL content inlined

    Raises:
        ConfigError: If the config contains SQL file references that cannot be loaded
    """
    # Import here to avoid circular import
    from ..sql_file_loader import SQLFileError, SQLFileLoader

    if sql_file_loader is None:
        sql_file_loader = SQLFileLoader()

    # Check if any views have SQL file references
    has_sql_files = any(
        getattr(view, "sql_file", None) is not None
        or getattr(view, "sql_template", None) is not None
        for view in config.views
    )

    if not has_sql_files:
        # No SQL files to process
        return config

    log_info("Loading SQL files", total_views=len(config.views))

    updated_views = []
    for view in config.views:
        if view.sql_file is not None:
            # Handle direct SQL file reference
            try:
                sql_content = sql_file_loader.load_sql_file(
                    file_path=view.sql_file.path,
                    config_file_path=str(config_path),
                    variables=view.sql_file.variables,
                    as_template=view.sql_file.as_template,
                )

                # Create new view with inline SQL
                updated_view = view.model_copy(
                    update={"sql": sql_content, "sql_file": None}
                )
                updated_views.append(updated_view)
                log_debug("Loaded SQL file for view", view_name=view.name)

            except SQLFileError as exc:
                raise ConfigError(
                    f"Failed to load SQL file for view '{view.name}': {exc}"
                ) from exc

        elif view.sql_template is not None:
            # Handle SQL template reference
            try:
                sql_content = sql_file_loader.load_sql_file(
                    file_path=view.sql_template.path,
                    config_file_path=str(config_path),
                    variables=view.sql_template.variables,
                    as_template=True,  # Templates are always processed as templates
                )

                # Create new view with inline SQL
                updated_view = view.model_copy(
                    update={"sql": sql_content, "sql_template": None}
                )
                updated_views.append(updated_view)
                log_debug("Loaded SQL template for view", view_name=view.name)

            except SQLFileError as exc:
                raise ConfigError(
                    f"Failed to load SQL template for view '{view.name}': {exc}"
                ) from exc

        else:
            # No SQL file reference, keep original view
            updated_views.append(view)

    # Create updated config with processed views
    updated_config = config.model_copy(update={"views": updated_views})

    file_based_views = len(
        [
            v
            for v in updated_views
            if v.sql
            and v != next((ov for ov in config.views if ov.name == v.name), None)
        ]
    )

    log_info(
        "SQL files loaded",
        total_views=len(config.views),
        file_based_views=file_based_views,
    )

    return updated_config


def load_config(
    path: str,
    load_sql_files: bool = True,
    sql_file_loader: Optional[Any] = None,
    resolve_paths: bool = True,
    filesystem: Optional[Any] = None,
) -> Any:
    """Load, interpolate, and validate a Duckalog configuration file.

    This helper is the main entry point for turning a YAML or JSON file into a
    validated :class:`Config` instance. It applies environment-variable
    interpolation and enforces the configuration schema.

    Args:
        path: Path to a YAML or JSON config file, or a remote URI.
        load_sql_files: Whether to load and process SQL from external files.
                      If False, SQL file references are left as-is for later processing.
        sql_file_loader: Optional SQLFileLoader instance for loading SQL files.
                        If None, a default loader will be created.
        resolve_paths: Whether to resolve relative paths to absolute paths.
                      If True, relative paths in view URIs and attachment paths
                      will be resolved relative to the config file's directory.
                      For remote configs, this defaults to False.
        filesystem: Optional fsspec filesystem object to use for remote operations.
                   If provided, this filesystem will be used instead of creating
                   a new one based on URI scheme. Useful for custom
                   authentication or advanced use cases.

    Returns:
        A validated :class:`Config` object.

    Raises:
        ConfigError: If the file cannot be read, is not valid YAML/JSON,
            fails schema validation, contains unresolved
            ``${env:VAR_NAME}`` placeholders, or if SQL file loading fails.

    Example:
        Load a catalog from ``catalog.yaml``::

            from duckalog import load_config

            config = load_config("catalog.yaml")
            print(len(config.views))

        Load a catalog from S3::

            config = load_config("s3://my-bucket/configs/catalog.yaml")
            print(len(config.views))

        Load a catalog with custom filesystem::

            import fsspec
            fs = fsspec.filesystem("s3", key="key", secret="secret", anon=False)
            config = load_config("s3://my-bucket/configs/catalog.yaml", filesystem=fs)
            print(len(config.views))
    """
    # Check if this is a remote URI
    try:
        from duckalog.remote_config import is_remote_uri, load_config_from_uri

        if is_remote_uri(path):
            # For remote URIs, use the remote loader
            # Default resolve_paths to False for remote configs
            return load_config_from_uri(
                uri=path,
                load_sql_files=load_sql_files,
                sql_file_loader=sql_file_loader,
                resolve_paths=False,  # Remote configs don't resolve relative paths by default
                filesystem=filesystem,  # Pass through filesystem parameter
            )
    except ImportError:
        # Remote functionality not available, continue with local loading
        pass

    # Local file loading - delegate to the dedicated helper with import support
    return _load_config_from_local_file(
        path=path,
        load_sql_files=load_sql_files,
        sql_file_loader=sql_file_loader,
        resolve_paths=resolve_paths,
        filesystem=filesystem,
    )


def _load_config_from_local_file(
    path: str,
    load_sql_files: bool = True,
    sql_file_loader: Optional[Any] = None,
    resolve_paths: bool = True,
    filesystem: Optional[Any] = None,
) -> Any:
    """Load a configuration from a local file with import support.

    This is an internal helper responsible for local file reading, environment
    interpolation, path resolution, validation, and import processing.

    Args:
        path: Path to a local YAML or JSON config file.
        load_sql_files: Whether to load and process SQL from external files.
        sql_file_loader: Optional SQLFileLoader instance for loading SQL files.
        resolve_paths: Whether to resolve relative paths to absolute paths.
        filesystem: Optional filesystem object for file I/O operations.
                   If None, uses default path-based file I/O.

    Returns:
        A validated :class:`Config` object.

    Raises:
        ConfigError: If the file cannot be read, is not valid YAML/JSON,
            fails schema validation, contains unresolved
            ``${env:VAR_NAME}`` placeholders, or if SQL file loading fails.
    """
    config_path = Path(path)
    if not config_path.exists():
        raise ConfigError(f"Config file not found: {path}")

    log_info("Loading config", path=str(config_path))

    # Use the new _load_config_with_imports function which handles everything
    return _load_config_with_imports(
        file_path=str(config_path),
        filesystem=filesystem,
        resolve_paths=resolve_paths,
        load_sql_files=load_sql_files,
        sql_file_loader=sql_file_loader,
    )


@dataclass
class ImportContext:
    """Tracks import state during loading."""
    visited_files: set[str] = field(default_factory=set)
    import_stack: list[str] = field(default_factory=list)
    config_cache: dict[str, Any] = field(default_factory=dict)
    import_chain: list[str] = field(default_factory=list)


def _is_remote_uri(path: str) -> bool:
    """Check if a path is a remote URI."""
    # Simple check for common remote URI schemes
    remote_schemes = ["http://", "https://", "s3://", "gcs://", "az://", "abfs://"]
    return any(path.startswith(scheme) for scheme in remote_schemes)


def _deep_merge_dict(base: dict, override: dict) -> dict:
    """Deep merge two dictionaries.

    Args:
        base: Base dictionary to merge into.
        override: Override dictionary with new/updated values.

    Returns:
        A new dictionary with merged content.
    """
    result = base.copy()

    for key, override_value in override.items():
        if key not in result:
            # New key, just add it
            result[key] = override_value
        else:
            # Key exists, need to merge
            base_value = result[key]

            if isinstance(base_value, dict) and isinstance(override_value, dict):
                # Both are dicts, recursively merge
                result[key] = _deep_merge_dict(base_value, override_value)
            elif isinstance(base_value, list) and isinstance(override_value, list):
                # Both are lists, concatenate
                result[key] = base_value + override_value
            else:
                # Override scalar values
                result[key] = override_value

    return result


def _deep_merge_config(base: Any, override: Any) -> Any:
    """Deep merge two Config objects.

    Args:
        base: Base Config object.
        override: Override Config object.

    Returns:
        A new Config object with merged content.
    """
    from .models import Config

    # Get the field values from both configs
    base_dict = base.model_dump(mode='json')
    override_dict = override.model_dump(mode='json')

    # Deep merge the dicts
    merged_dict = _deep_merge_dict(base_dict, override_dict)

    # Create a new Config from the merged dict
    # Use ** to unpack the dict and let Pydantic properly instantiate nested objects
    return Config(**merged_dict)


def _resolve_import_path(import_path: str, base_path: str) -> str:
    """Resolve an import path relative to the importing file.

    Args:
        import_path: The import path to resolve (can contain ${env:VAR}).
        base_path: Path to the importing file.

    Returns:
        The resolved absolute path.

    Raises:
        PathResolutionError: If path resolution fails.
    """
    # Apply environment variable interpolation
    if "${env:" in import_path:
        import_path = _interpolate_env(import_path)

    # Check if it's a remote URI
    if _is_remote_uri(import_path):
        return import_path

    # Resolve relative to base file
    if os.path.isabs(import_path):
        resolved_path = import_path
    else:
        base_dir = os.path.dirname(base_path)
        resolved_path = os.path.normpath(os.path.join(base_dir, import_path))

    # Security check - ensure path doesn't escape allowed directory
    # This is a basic check - the actual validation will happen during file loading
    if not os.path.isabs(resolved_path):
        raise PathResolutionError(
            f"Failed to resolve import path: {import_path}",
            original_path=import_path,
            resolved_path=resolved_path,
        )

    return resolved_path


def _validate_unique_names(config: Any, context: ImportContext) -> None:
    """Validate unique names across all config sections.

    Args:
        config: The merged Config object.
        context: Import context with import chain information.

    Raises:
        DuplicateNameError: If duplicate names are found.
    """
    # Validate unique view names
    view_names: dict[tuple[Optional[str], str], int] = {}
    duplicates = []
    for view in config.views:
        key = (view.db_schema, view.name)
        if key in view_names:
            schema_part = f"{view.db_schema}." if view.db_schema else ""
            duplicates.append(f"{schema_part}{view.name}")
        else:
            view_names[key] = 1

    if duplicates:
        raise DuplicateNameError(
            f"Duplicate view name(s) found: {', '.join(sorted(set(duplicates)))}",
            name_type="view",
            duplicate_names=sorted(set(duplicates)),
        )

    # Validate unique Iceberg catalog names
    catalog_names: dict[str, int] = {}
    duplicates = []
    for catalog in config.iceberg_catalogs:
        if catalog.name in catalog_names:
            duplicates.append(catalog.name)
        else:
            catalog_names[catalog.name] = 1

    if duplicates:
        raise DuplicateNameError(
            f"Duplicate Iceberg catalog name(s) found: {', '.join(sorted(set(duplicates)))}",
            name_type="iceberg_catalog",
            duplicate_names=sorted(set(duplicates)),
        )

    # Validate unique semantic model names
    semantic_model_names: dict[str, int] = {}
    duplicates = []
    for semantic_model in config.semantic_models:
        if semantic_model.name in semantic_model_names:
            duplicates.append(semantic_model.name)
        else:
            semantic_model_names[semantic_model.name] = 1

    if duplicates:
        raise DuplicateNameError(
            f"Duplicate semantic model name(s) found: {', '.join(sorted(set(duplicates)))}",
            name_type="semantic_model",
            duplicate_names=sorted(set(duplicates)),
        )

    # Validate unique attachment aliases
    attachment_aliases: dict[str, int] = {}
    duplicates = []

    # Check duckdb attachments
    for attachment in config.attachments.duckdb:
        if attachment.alias in attachment_aliases:
            duplicates.append(f"duckdb.{attachment.alias}")
        else:
            attachment_aliases[attachment.alias] = 1

    # Check sqlite attachments
    for attachment in config.attachments.sqlite:
        if attachment.alias in attachment_aliases:
            duplicates.append(f"sqlite.{attachment.alias}")
        else:
            attachment_aliases[attachment.alias] = 1

    # Check postgres attachments
    for attachment in config.attachments.postgres:
        if attachment.alias in attachment_aliases:
            duplicates.append(f"postgres.{attachment.alias}")
        else:
            attachment_aliases[attachment.alias] = 1

    # Check duckalog attachments
    for attachment in config.attachments.duckalog:
        if attachment.alias in attachment_aliases:
            duplicates.append(f"duckalog.{attachment.alias}")
        else:
            attachment_aliases[attachment.alias] = 1

    if duplicates:
        raise DuplicateNameError(
            f"Duplicate attachment alias(es) found: {', '.join(sorted(set(duplicates)))}",
            name_type="attachment",
            duplicate_names=sorted(set(duplicates)),
        )


def _resolve_and_load_import(
    import_path: str,
    base_path: str,
    filesystem: Optional[Any],
    resolve_paths: bool,
    load_sql_files: bool,
    sql_file_loader: Optional[Any],
    import_context: ImportContext,
) -> Any:
    """Resolve and load an imported config file.

    Args:
        import_path: Path to the import (can be relative or remote).
        base_path: Path to the importing file.
        filesystem: Optional filesystem object.
        resolve_paths: Whether to resolve relative paths.
        load_sql_files: Whether to load SQL files.
        sql_file_loader: Optional SQLFileLoader instance.
        import_context: Import context for tracking visited files.

    Returns:
        The loaded Config object.

    Raises:
        CircularImportError: If a circular import is detected.
        ImportFileNotFoundError: If the imported file doesn't exist.
        ImportValidationError: If the imported config fails validation.
    """
    # Resolve the import path
    try:
        resolved_path = _resolve_import_path(import_path, base_path)
    except Exception as exc:
        raise ImportFileNotFoundError(
            f"Failed to resolve import path '{import_path}' from '{base_path}': {exc}",
            import_path=import_path,
            cause=exc,
        ) from exc

    log_debug("Resolving import", import_path=import_path, resolved_path=resolved_path)

    # Check for circular imports
    # Use the resolved path as the key
    if resolved_path in import_context.visited_files:
        # Check if it's in the current import stack
        if resolved_path in import_context.import_stack:
            # Circular import detected!
            chain = " -> ".join(import_context.import_stack + [resolved_path])
            raise CircularImportError(
                f"Circular import detected in import chain: {chain}",
                import_chain=import_context.import_stack + [resolved_path],
            )
        else:
            # This file was already loaded in a different branch, use cached version
            log_debug("Using cached config for already-loaded import", path=resolved_path)
            return import_context.config_cache.get(resolved_path)

    # Add to import stack and visited files
    import_context.import_stack.append(resolved_path)
    import_context.visited_files.add(resolved_path)

    try:
        # Load the imported config
        # Check if it's a remote URI
        if _is_remote_uri(resolved_path):
            # For remote URIs, we need to use the remote loader
            try:
                from duckalog.remote_config import load_config_from_uri

                imported_config = load_config_from_uri(
                    uri=resolved_path,
                    load_sql_files=load_sql_files,
                    sql_file_loader=sql_file_loader,
                    resolve_paths=False,
                    filesystem=filesystem,
                )
            except Exception as exc:
                raise ImportValidationError(
                    f"Failed to load remote config '{resolved_path}': {exc}",
                    import_path=resolved_path,
                    cause=exc,
                ) from exc
        else:
            # Local file loading
            config_path = Path(resolved_path)
            if not config_path.exists():
                raise ImportFileNotFoundError(
                    f"Imported file not found: {resolved_path}",
                    import_path=resolved_path,
                )

            try:
                if filesystem is not None:
                    if not hasattr(filesystem, "open") or not hasattr(filesystem, "exists"):
                        raise ImportError(
                            "filesystem object must provide 'open' and 'exists' methods"
                        )
                    if not filesystem.exists(resolved_path):
                        raise ImportFileNotFoundError(
                            f"Imported file not found: {resolved_path}",
                            import_path=resolved_path,
                        )
                    with filesystem.open(resolved_path, "r") as f:
                        raw_text = f.read()
                else:
                    raw_text = config_path.read_text()
            except OSError as exc:
                raise ImportValidationError(
                    f"Failed to read imported file '{resolved_path}': {exc}",
                    import_path=resolved_path,
                    cause=exc,
                ) from exc

            suffix = config_path.suffix.lower()
            if suffix in {".yaml", ".yml"}:
                parsed = yaml.safe_load(raw_text)
            elif suffix == ".json":
                parsed = json.loads(raw_text)
            else:
                raise ImportValidationError(
                    f"Imported file must use .yaml, .yml, or .json extension: {resolved_path}",
                    import_path=resolved_path,
                )

            if parsed is None:
                raise ImportValidationError(
                    f"Imported file is empty: {resolved_path}",
                    import_path=resolved_path,
                )
            if not isinstance(parsed, dict):
                raise ImportValidationError(
                    f"Imported file must define a mapping at the top level: {resolved_path}",
                    import_path=resolved_path,
                )

            # Apply environment variable interpolation
            interpolated = _interpolate_env(parsed)

            # Validate the imported config
            from .models import Config

            try:
                imported_config = Config.model_validate(interpolated)
            except Exception as exc:
                raise ImportValidationError(
                    f"Imported config validation failed: {exc}",
                    import_path=resolved_path,
                    cause=exc,
                ) from exc

            # Load SQL files if requested
            if load_sql_files:
                imported_config = _load_sql_files_from_config(
                    imported_config, config_path, sql_file_loader
                )

        # Cache the imported config
        import_context.config_cache[resolved_path] = imported_config

        # Recursively process imports in the imported config
        if imported_config.imports:
            log_debug(
                "Processing nested imports",
                path=resolved_path,
                import_count=len(imported_config.imports),
            )
            for nested_import_path in imported_config.imports:
                nested_config = _resolve_and_load_import(
                    import_path=nested_import_path,
                    base_path=resolved_path,
                    filesystem=filesystem,
                    resolve_paths=resolve_paths,
                    load_sql_files=load_sql_files,
                    sql_file_loader=sql_file_loader,
                    import_context=import_context,
                )
                # Merge the nested import into the imported config
                # Main config should override imported config, so import goes first
                imported_config = _deep_merge_config(nested_config, imported_config)

        return imported_config

    finally:
        # Remove from import stack
        import_context.import_stack.pop()


def _load_config_with_imports(
    file_path: str,
    content: Optional[str] = None,
    format: str = "yaml",
    filesystem: Optional[Any] = None,
    resolve_paths: bool = True,
    load_sql_files: bool = True,
    sql_file_loader: Optional[Any] = None,
    import_context: Optional[ImportContext] = None,
) -> Any:
    """Load config with import support.

    Args:
        file_path: Path to the config file.
        content: Optional file content (if not provided, will read from file_path).
        format: File format (yaml or json).
        filesystem: Optional filesystem object.
        resolve_paths: Whether to resolve relative paths.
        load_sql_files: Whether to load SQL files.
        sql_file_loader: Optional SQLFileLoader instance.
        import_context: Optional existing import context.

    Returns:
        A validated and merged Config object.

    Raises:
        ConfigError: If the config cannot be loaded or validated.
    """
    if import_context is None:
        import_context = ImportContext()

    config_path = Path(file_path)
    resolved_path = str(config_path.resolve())

    log_debug("Loading config with imports", path=resolved_path)

    # Check if config is already in cache
    if resolved_path in import_context.config_cache:
        log_debug("Using cached config", path=resolved_path)
        return import_context.config_cache[resolved_path]

    # Add to visited files
    import_context.visited_files.add(resolved_path)
    import_context.import_stack.append(resolved_path)

    try:
        # Load the base config
        if content is not None:
            raw_text = content
        else:
            if filesystem is not None:
                if not hasattr(filesystem, "open") or not hasattr(filesystem, "exists"):
                    raise ConfigError(
                        "filesystem object must provide 'open' and 'exists' methods"
                    )
                if not filesystem.exists(resolved_path):
                    raise ConfigError(f"Config file not found: {file_path}")
                with filesystem.open(resolved_path, "r") as f:
                    raw_text = f.read()
            else:
                if not config_path.exists():
                    raise ConfigError(f"Config file not found: {file_path}")
                raw_text = config_path.read_text()

        # Parse the content
        if format == "yaml":
            parsed = yaml.safe_load(raw_text)
        elif format == "json":
            parsed = json.loads(raw_text)
        else:
            raise ConfigError("Config files must use .yaml, .yml, or .json extensions")

        if parsed is None:
            raise ConfigError("Config file is empty")
        if not isinstance(parsed, dict):
            raise ConfigError("Config file must define a mapping at the top level")

        # Apply environment variable interpolation
        interpolated = _interpolate_env(parsed)

        # Validate the base config
        from .models import Config

        try:
            config = Config.model_validate(interpolated)
        except Exception as exc:
            raise ConfigError(f"Configuration validation failed: {exc}") from exc

        # Cache the base config
        import_context.config_cache[resolved_path] = config

        # Process imports
        if config.imports:
            log_debug("Processing imports", import_count=len(config.imports))
            for import_path in config.imports:
                imported_config = _resolve_and_load_import(
                    import_path=import_path,
                    base_path=resolved_path,
                    filesystem=filesystem,
                    resolve_paths=resolve_paths,
                    load_sql_files=load_sql_files,
                    sql_file_loader=sql_file_loader,
                    import_context=import_context,
                )
                # Merge the imported config into the base config
                # Main config should override imported config, so import goes first
                config = _deep_merge_config(imported_config, config)

        # Validate merged config
        _validate_unique_names(config, import_context)

        # Load SQL files if requested (after all merges are complete)
        if load_sql_files:
            config = _load_sql_files_from_config(config, config_path, sql_file_loader)

        log_debug("Config loaded with imports", path=resolved_path, views=len(config.views))
        return config

    finally:
        # Remove from import stack
        import_context.import_stack.pop()
