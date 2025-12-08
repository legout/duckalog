"""Build route handlers."""

from __future__ import annotations

import json
from typing import Any

from litestar.response import Response, Redirect

from ..state import DashboardContext


async def build_catalog_trigger(ctx: DashboardContext) -> Redirect:
    """Trigger a catalog build and redirect to home."""
    ctx.trigger_build()
    return Redirect(path="/", status_code=303)


async def build_catalog_stream(ctx: DashboardContext) -> Response:
    """Trigger a catalog build and stream status via Server-Sent Events."""

    async def event_stream():
        """Generate SSE events for build process."""
        events = []

        try:
            # Send start event
            events.append(f"event: datastar-patch-signals\n")
            events.append(f"data: {json.dumps({'signals': {'build_running': True, 'build_error': None, 'build_success': None}})}\n\n")

            # Execute build
            status = ctx.trigger_build()

            if status.success:
                # Send success result
                events.append(f"event: datastar-patch-signals\n")
                events.append(f"data: {json.dumps({'signals': {'build_running': False, 'build_error': None, 'build_success': True, 'build_summary': status.summary}})}\n\n")
            else:
                # Send error result
                events.append(f"event: datastar-patch-signals\n")
                events.append(f"data: {json.dumps({'signals': {'build_running': False, 'build_error': status.message, 'build_success': False}})}\n\n")

            # Send completion event
            events.append(f"event: datastar-patch-signals\n")
            events.append(f"data: {json.dumps({'signals': {'build_complete': True}})}\n\n")

        except Exception as exc:
            # Send error event
            events.append(f"event: datastar-patch-signals\n")
            events.append(f"data: {json.dumps({'signals': {'build_running': False, 'build_error': str(exc), 'build_success': False}})}\n\n")

        return "".join(events)

    content = await event_stream()

    return Response(
        content=content,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control",
        }
    )
