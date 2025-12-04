"""Shared data generators for duckalog examples."""

from .events import generate_events
from .sales import generate_sales
from .timeseries import generate_timeseries
from .users import generate_users

__all__ = [
    "generate_users",
    "generate_events",
    "generate_sales",
    "generate_timeseries",
]
