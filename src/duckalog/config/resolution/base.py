from abc import ABC, abstractmethod
from typing import Any, Optional, Union, Protocol, runtime_checkable, TYPE_CHECKING
from pathlib import Path
from dataclasses import dataclass, field
import threading

if TYPE_CHECKING:
    from ...performance import PerformanceMetrics


@dataclass
class ImportContext:
    """Tracks import state during loading."""

    visited_files: set[str] = field(default_factory=set)
    import_stack: list[str] = field(default_factory=list)
    config_cache: dict[str, Any] = field(default_factory=dict)
    import_chain: list[str] = field(default_factory=list)
    max_cache_size: int = 1000  # Maximum number of configs to cache
    metrics: Optional["PerformanceMetrics"] = None
    _lock: threading.RLock = field(default_factory=threading.RLock)

    def _enforce_cache_limit(self, log_debug_func=None) -> None:
        """Enforce cache size limit to prevent memory issues with large config trees."""
        with self._lock:
            if len(self.config_cache) > self.max_cache_size:
                # Remove oldest entries (simple FIFO strategy)
                oldest_keys = list(self.config_cache.keys())[
                    : len(self.config_cache) - self.max_cache_size
                ]
                for key in oldest_keys:
                    del self.config_cache[key]
                if log_debug_func:
                    log_debug_func(
                        "Cache size limit enforced",
                        removed_count=len(oldest_keys),
                        current_size=len(self.config_cache),
                        max_size=self.max_cache_size,
                    )


@runtime_checkable
class EnvProcessor(Protocol):
    """Interface for environment variable processors."""

    def process(
        self, config_data: dict[str, Any], load_dotenv: bool = True
    ) -> dict[str, Any]:
        """Process environment variables and .env files."""
        ...


@runtime_checkable
class ImportResolver(Protocol):
    """Interface for configuration import resolvers."""

    def resolve(
        self, config_data: dict[str, Any], context: ImportContext
    ) -> dict[str, Any]:
        """Resolve imports within a configuration dictionary."""
        ...
