"""Datastar integration for reactive dashboard functionality."""

from __future__ import annotations

import json
from typing import Any, AsyncGenerator

from starlette.requests import Request
from starlette.responses import Response

from .state import DashboardContext


class DatastarSignals:
    """Manages Datastar signals for the dashboard."""

    def __init__(self, context: DashboardContext):
        self.context = context

    def get_summary_signals(self) -> dict[str, Any]:
        """Get dashboard summary as Datastar signals."""
        from .state import summarize_config

        summary = summarize_config(self.context)

        # Add build status if available
        if self.context.last_build:
            build_status = {
                "success": self.context.last_build.success,
                "message": self.context.last_build.message,
                "summary": self.context.last_build.summary,
                "duration_seconds": self.context.last_build.duration_seconds,
            }
        else:
            build_status = {
                "success": None,
                "message": None,
                "summary": "No build performed yet",
                "duration_seconds": None,
            }

        return {
            "config_path": summary.get("config_path", ""),
            "database": summary.get("database", ""),
            "views_count": int(summary.get("views", "0")),
            "attachments_count": int(summary.get("attachments", "0")),
            "semantic_models_count": int(summary.get("semantic_models", "0")),
            "last_build_success": build_status["success"],
            "last_build_message": build_status["message"],
            "last_build_summary": build_status["summary"],
            "last_build_duration_seconds": build_status["duration_seconds"],
        }

    def get_views_signals(self, search_query: str = "") -> dict[str, Any]:
        """Get views list as Datastar signals."""
        views = self.context.view_list()

        if search_query:
            views = [
                view for view in views
                if search_query.lower() in view["name"].lower()
                or search_query.lower() in view.get("uri", "").lower()
            ]

        return {
            "views": views,
            "search_query": search_query,
            "views_count": len(views),
        }

    def get_query_signals(self) -> dict[str, Any]:
        """Get query state as Datastar signals."""
        return {
            "query_sql": "",
            "query_columns": [],
            "query_rows": [],
            "query_truncated": False,
            "query_error": None,
            "query_executing": False,
        }


def create_sse_response(data: dict[str, Any]) -> str:
    """Create Server-Sent Events response data."""
    lines = []
    for key, value in data.items():
        # Convert value to JSON for proper Datastar formatting
        json_value = json.dumps(value)
        lines.append(f"data: {key} {json_value}")
    lines.append("")  # Empty line to end the message
    return "\n".join(lines)


async def sse_event_stream(request: Request, context: DashboardContext) -> Response:
    """Create SSE event stream for real-time updates."""
    signals = DatastarSignals(context)

    async def event_stream() -> AsyncGenerator[str, None]:
        # Send initial signals
        initial_data = {
            "summary": signals.get_summary_signals(),
            "views": signals.get_views_signals(),
            "query": signals.get_query_signals(),
        }

        for signal_type, data in initial_data.items():
            yield create_sse_response({signal_type: data})

    return Response(
        content=event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        },
    )


def get_datastar_attributes(signal_name: str, expression: str = None) -> dict[str, str]:
    """Get Datastar attributes for reactive HTML elements."""
    attrs = {
        "data-signals": signal_name,
    }

    if expression:
        attrs["data-bind"] = expression

    return attrs


def get_datastar_action(action: str, target: str = None) -> dict[str, str]:
    """Get Datastar action attributes for interactive elements."""
    attrs = {
        "data-on-click": action,
    }

    if target:
        attrs["data-target"] = target

    return attrs


__all__ = [
    "DatastarSignals",
    "sse_event_stream",
    "get_datastar_attributes",
    "get_datastar_action",
]