"""Public API orchestration for Duckalog configuration loading."""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any, Optional, Union

from duckalog.errors import ConfigError

from .models import Config
from .resolution.imports import (
    DefaultImportResolver,
    request_cache_scope,
    _load_config_with_imports,
)
from .resolution.imports import _is_remote_uri  # re-use existing detection
from .validators import log_info


def load_config(
    path: Union[str, Path],
    load_sql_files: bool = True,
    sql_file_loader: Optional[Any] = None,
    resolve_paths: bool = True,
    filesystem: Optional[Any] = None,
    load_dotenv: bool = True,
) -> Config:
    """Load, interpolate, and validate a Duckalog configuration file."""
    try:
        from duckalog.remote_config import is_remote_uri, load_config_from_uri

        if is_remote_uri(str(path)):
            return load_config_from_uri(
                uri=str(path),
                load_sql_files=load_sql_files,
                sql_file_loader=sql_file_loader,
                resolve_paths=False,
                filesystem=filesystem,
                load_dotenv=load_dotenv,
            )
    except ImportError:
        pass

    return _load_config_from_local_file_impl(
        path=str(path),
        load_sql_files=load_sql_files,
        sql_file_loader=sql_file_loader,
        resolve_paths=resolve_paths,
        filesystem=filesystem,
        load_dotenv=load_dotenv,
    )


def _load_config_from_local_file(
    path: str,
    load_sql_files: bool = True,
    sql_file_loader: Optional[Any] = None,
    resolve_paths: bool = True,
    filesystem: Optional[Any] = None,
    load_dotenv: bool = True,
) -> Config:
    """Internal helper for loading local config files.

    .. deprecated:: 0.4.0
        Use :func:`load_config` instead.
    """
    warnings.warn(
        "_load_config_from_local_file is internal and deprecated (introduced in 0.4.0). "
        "Please use load_config instead. This function will be made private in a future version.",
        DeprecationWarning,
        stacklevel=2,
    )
    return _load_config_from_local_file_impl(
        path=path,
        load_sql_files=load_sql_files,
        sql_file_loader=sql_file_loader,
        resolve_paths=resolve_paths,
        filesystem=filesystem,
        load_dotenv=load_dotenv,
    )


def _load_config_from_local_file_impl(
    path: str,
    load_sql_files: bool = True,
    sql_file_loader: Optional[Any] = None,
    resolve_paths: bool = True,
    filesystem: Optional[Any] = None,
    load_dotenv: bool = True,
) -> Config:
    log_info("Loading config", path=path)

    with request_cache_scope() as request_context:
        resolver = DefaultImportResolver(context=request_context)
        return _load_config_with_imports(
            file_path=path,
            filesystem=filesystem,
            resolve_paths=resolve_paths,
            load_sql_files=load_sql_files,
            sql_file_loader=sql_file_loader,
            import_context=request_context.import_context,
            load_dotenv=load_dotenv,
            env_cache=request_context.env_cache,
        )


__all__ = ["load_config", "_load_config_from_local_file"]
