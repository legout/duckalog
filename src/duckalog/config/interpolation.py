"""Environment variable interpolation utilities (Legacy Proxy).

.. deprecated:: 0.4.0
    Use :mod:`duckalog.config.resolution.env` and :mod:`duckalog.config.loading.sql` instead.
"""

import warnings
from typing import Any

# Add module-level deprecation warning
warnings.warn(
    "The 'duckalog.config.interpolation' module is deprecated (introduced in 0.4.0) and will be removed in version 1.0.0. "
    "Please use 'duckalog.config.resolution.env' and 'duckalog.config.loading.sql' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from .resolution.env import _interpolate_env as _new_interpolate_env
from .loading.sql import process_sql_file_references as _new_process_sql_file_references


def _interpolate_env(value: Any) -> Any:
    """Proxy for legacy _interpolate_env."""
    warnings.warn(
        "duckalog.config.interpolation._interpolate_env is deprecated. "
        "Please use duckalog.config.resolution.env._interpolate_env instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return _new_interpolate_env(value)


def process_sql_file_references(*args: Any, **kwargs: Any) -> Any:
    """Proxy for legacy process_sql_file_references."""
    warnings.warn(
        "duckalog.config.interpolation.process_sql_file_references is deprecated. "
        "Please use duckalog.config.loading.sql.process_sql_file_references instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return _new_process_sql_file_references(*args, **kwargs)
