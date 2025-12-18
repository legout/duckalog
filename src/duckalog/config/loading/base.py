from abc import ABC, abstractmethod
from typing import Any, Optional, Union
from pathlib import Path


class ConfigLoader(ABC):
    """Abstract base class for configuration loaders."""

    @abstractmethod
    def load(
        self, path: Union[str, Path], filesystem: Optional[Any] = None
    ) -> dict[str, Any]:
        """Load configuration from a source."""
        pass


class SQLFileLoader(ABC):
    """Abstract base class for SQL file loaders."""

    @abstractmethod
    def load_sql(self, path: Union[str, Path], filesystem: Optional[Any] = None) -> str:
        """Load SQL content from a file."""
        pass
