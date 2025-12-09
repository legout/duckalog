"""Duckalog Dashboard - Modern UI for inspecting DuckDB catalogs."""

from .app import create_app
from .state import DashboardContext

__all__ = ["create_app", "DashboardContext"]
