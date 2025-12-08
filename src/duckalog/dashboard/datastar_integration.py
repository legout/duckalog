"""Datastar integration for real-time reactivity in the dashboard."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime
from typing import Any

from datastar_py import ServerSentEventGenerator as SSE
from datastar_py.starlette import DatastarResponse


async def build_status_stream() -> Any:
    """Stream real-time build status updates."""
    # Simulate build status updates for demo purposes
    statuses = ["idle", "building", "success", "idle"]

    for status in statuses:
        yield SSE.patch_signals({
            "buildStatus": status,
            "buildTime": datetime.now().isoformat(),
            "buildProgress": statuses.index(status) / (len(statuses) - 1)
        })
        await asyncio.sleep(2)  # Simulate time between status changes


async def query_status_stream(query_id: str) -> Any:
    """Stream real-time query execution updates."""
    # Simulate query execution phases
    phases = ["preparing", "executing", "fetching", "completed"]

    for phase in phases:
        yield SSE.patch_signals({
            "queryStatus": phase,
            "queryId": query_id,
            "queryTime": datetime.now().isoformat(),
            "queryProgress": phases.index(phase) / (len(phases) - 1)
        })
        await asyncio.sleep(1.5)  # Simulate processing time


async def notification_stream() -> Any:
    """Stream real-time notifications."""
    notifications = [
        {"type": "info", "message": "Dashboard loaded successfully", "timestamp": datetime.now().isoformat()},
        {"type": "success", "message": "View 'sales_data' refreshed", "timestamp": datetime.now().isoformat()},
        {"type": "warning", "message": "Build cache cleared", "timestamp": datetime.now().isoformat()}
    ]

    for notification in notifications:
        yield SSE.patch_signals({
            "notifications": [notification]
        })
        await asyncio.sleep(3)  # Show notifications periodically


class DatastarAttributes:
    """Helper class for generating Datastar attributes."""

    @staticmethod
    def signals(initial_data: dict[str, Any]) -> str:
        """Generate data-signals attribute."""
        return f'data-signals="{json.dumps(initial_data)}"'

    @staticmethod
    def bind(property_name: str) -> str:
        """Generate data-bind attribute for two-way binding."""
        return f'data-bind="{property_name}"'

    @staticmethod
    def text(expression: str) -> str:
        """Generate data-text attribute for text content."""
        return f'data-text="{expression}"'

    @staticmethod
    def html(expression: str) -> str:
        """Generate data-html attribute for HTML content."""
        return f'data-html="{expression}"'

    @staticmethod
    def show(condition: str) -> str:
        """Generate data-show attribute for conditional visibility."""
        return f'data-show="{condition}"'

    @staticmethod
    def hide(condition: str) -> str:
        """Generate data-hide attribute for conditional hiding."""
        return f'data-hide="{condition}"'

    @staticmethod
    def class_(class_map: dict[str, str]) -> str:
        """Generate data-class attribute for conditional classes."""
        return f'data-class="{json.dumps(class_map)}"'

    @staticmethod
    def on(event: str, action: str) -> str:
        """Generate data-on attribute for event handling."""
        return f'data-on-{event}="{action}"'

    @staticmethod
    def execute(expression: str) -> str:
        """Generate data-execute attribute for script execution."""
        return f'data-execute="{expression}"'


# Global attribute generator instance
ds = DatastarAttributes()