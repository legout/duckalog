from abc import ABC, abstractmethod
from typing import Union, Optional
from pathlib import Path


class PathValidator(ABC):
    """Abstract base class for path security validation."""

    @abstractmethod
    def validate(self, path: Union[str, Path]) -> None:
        """Validate that a path is secure and accessible."""
        pass


class PathResolver(ABC):
    """Abstract base class for path resolution."""

    @abstractmethod
    def resolve(self, path: str, base_path: Optional[Union[str, Path]] = None) -> str:
        """Resolve a path to an absolute path with security checks."""
        pass
