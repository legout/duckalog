"""SQL file processing utilities extracted from the legacy loader."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse

from ..validators import log_debug, log_info
from duckalog.sql_file_loader import SQLFileLoader
from duckalog.errors import ConfigError


def process_sql_file_references(
    views,
    sql_file_loader,
    config_file_path,
    log_info_func,
    log_debug_func,
    filesystem=None,
):
    """Process SQL file references in views and replace with inline SQL content.

    This is a shared utility function that handles the common logic for processing
    both sql_file and sql_template references across local and remote configs.

    Args:
        views: List of view objects to process
        sql_file_loader: SQLFileLoader instance for loading SQL files
        config_file_path: Path to the configuration file (for relative path resolution)
        log_info_func: Function for info-level logging
        log_debug_func: Function for debug-level logging
        filesystem: Optional filesystem object for remote file operations

    Returns:
        Tuple of (updated_views, file_based_views_count)

    Raises:
        ConfigError: If SQL file loading fails
    """
    from duckalog.sql_file_loader import SQLFileError

    def _is_remote_uri(uri: str) -> bool:
        """Check if a URI is a remote URI."""
        if not uri:
            return False
        parsed = urlparse(uri)
        remote_schemes = [
            "http://",
            "https://",
            "s3://",
            "gcs://",
            "az://",
            "abfs://",
            "sftp://",
        ]
        return any(uri.startswith(scheme) for scheme in remote_schemes)

    def _fetch_remote_content(uri: str) -> str:
        """Fetch content from a remote URI."""
        try:
            from duckalog.remote_config import fetch_remote_content

            return fetch_remote_content(uri, filesystem=filesystem)
        except ImportError:
            # Fallback to basic HTTP if remote_config not available
            import requests

            response = requests.get(uri)
            response.raise_for_status()
            return response.text

    updated_views = []
    file_based_views = 0

    for view in views:
        if view.sql_file is not None:
            # Handle direct SQL file reference
            file_path = view.sql_file.path

            # Check if the SQL file path is a remote URI
            if _is_remote_uri(file_path):
                # Load from remote URI
                try:
                    sql_content = _fetch_remote_content(file_path)

                    # Process as template if needed
                    if view.sql_file.as_template:
                        sql_content = sql_file_loader._process_template(
                            sql_content, view.sql_file.variables or {}, file_path
                        )

                    # Create new view with inline SQL
                    updated_view = view.model_copy(
                        update={"sql": sql_content, "sql_file": None}
                    )
                    updated_views.append(updated_view)
                    file_based_views += 1
                    log_debug_func(
                        "Loaded remote SQL file for view", view_name=view.name
                    )

                except Exception as exc:
                    raise ConfigError(
                        f"Failed to load remote SQL file for view '{view.name}': {exc}"
                    ) from exc
            else:
                # Load as local file using SQLFileLoader
                try:
                    sql_content = sql_file_loader.load_sql_file(
                        file_path=file_path,
                        config_file_path=config_file_path,
                        variables=view.sql_file.variables,
                        as_template=view.sql_file.as_template,
                        filesystem=filesystem,
                    )

                    # Create new view with inline SQL
                    updated_view = view.model_copy(
                        update={"sql": sql_content, "sql_file": None}
                    )
                    updated_views.append(updated_view)
                    file_based_views += 1
                    log_debug_func("Loaded SQL file for view", view_name=view.name)

                except SQLFileError as exc:
                    raise ConfigError(
                        f"Failed to load SQL file for view '{view.name}': {exc}"
                    ) from exc

        elif view.sql_template is not None:
            # Handle SQL template reference
            file_path = view.sql_template.path

            # Check if the SQL template path is a remote URI
            if _is_remote_uri(file_path):
                try:
                    sql_content = _fetch_remote_content(file_path)
                    # Process template variables
                    sql_content = sql_file_loader._process_template(
                        sql_content, view.sql_template.variables or {}, file_path
                    )

                    # Create new view with inline SQL
                    updated_view = view.model_copy(
                        update={"sql": sql_content, "sql_template": None}
                    )
                    updated_views.append(updated_view)
                    file_based_views += 1
                    log_debug_func(
                        "Loaded remote SQL template for view", view_name=view.name
                    )

                except Exception as exc:
                    raise ConfigError(
                        f"Failed to load remote SQL template for view '{view.name}': {exc}"
                    ) from exc
            else:
                # Load as local template
                try:
                    sql_content = sql_file_loader.load_sql_file(
                        file_path=file_path,
                        config_file_path=config_file_path,
                        variables=view.sql_template.variables,
                        as_template=True,  # Templates are always processed as templates
                        filesystem=filesystem,
                    )

                    # Create new view with inline SQL
                    updated_view = view.model_copy(
                        update={"sql": sql_content, "sql_template": None}
                    )
                    updated_views.append(updated_view)
                    file_based_views += 1
                    log_debug_func("Loaded SQL template for view", view_name=view.name)

                except SQLFileError as exc:
                    raise ConfigError(
                        f"Failed to load SQL template for view '{view.name}': {exc}"
                    ) from exc

        else:
            # No SQL file reference, keep original view
            updated_views.append(view)

    return updated_views, file_based_views


def load_sql_files_from_config(
    config: Any,
    config_path: Path,
    sql_file_loader: Optional[Any] = None,
    *,
    filesystem: Optional[Any] = None,
) -> Any:
    """Inline SQL content from external files referenced in the config."""
    if sql_file_loader is None:
        sql_file_loader = SQLFileLoader()

    has_sql_files = any(
        getattr(view, "sql_file", None) is not None
        or getattr(view, "sql_template", None) is not None
        for view in config.views
    )

    if not has_sql_files:
        return config

    log_info("Loading SQL files", total_views=len(config.views))

    updated_views, file_based_views = process_sql_file_references(
        views=config.views,
        sql_file_loader=sql_file_loader,
        config_file_path=str(config_path),
        log_info_func=log_info,
        log_debug_func=log_debug,
        filesystem=filesystem,
    )

    updated_config = config.model_copy(update={"views": updated_views})

    log_info(
        "SQL files loaded",
        total_views=len(config.views),
        file_based_views=file_based_views,
    )

    return updated_config


__all__ = ["load_sql_files_from_config", "process_sql_file_references"]
