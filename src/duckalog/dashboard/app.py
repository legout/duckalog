"""ASGI app factory for the duckalog dashboard."""

from __future__ import annotations

import os
from pathlib import Path

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette.routing import Route
from starlette.staticfiles import StaticFiles

from .datastar_integration import (
    build_status_stream,
    notification_stream,
    query_status_stream,
)
from .state import DashboardContext
from .views import home_page, query_page, view_detail_page, views_page


async def _home(request: Request) -> Response:
    ctx: DashboardContext = request.app.state.dashboard_ctx  # type: ignore[attr-defined]
    return home_page(ctx)


async def _views(request: Request) -> Response:
    ctx: DashboardContext = request.app.state.dashboard_ctx  # type: ignore[attr-defined]
    q = request.query_params.get("q")
    return views_page(ctx, q)


async def _view_detail(request: Request) -> Response:
    ctx: DashboardContext = request.app.state.dashboard_ctx  # type: ignore[attr-defined]
    name = request.path_params["name"]
    return view_detail_page(ctx, name)


async def _query_get(request: Request) -> Response:
    return query_page()


async def _query_post(request: Request) -> Response:
    ctx: DashboardContext = request.app.state.dashboard_ctx  # type: ignore[attr-defined]
    form = await request.form()
    sql = form.get("sql") or ""
    result = ctx.run_query(str(sql))
    return query_page(result=result, sql_text=str(sql))


async def _build(request: Request) -> Response:
    ctx: DashboardContext = request.app.state.dashboard_ctx  # type: ignore[attr-defined]
    ctx.trigger_build()
    return RedirectResponse(url="/", status_code=303)


async def _events_build_status(request: Request) -> Response:
    """SSE endpoint for real-time build status updates."""
    from datastar_py.starlette import DatastarResponse
    return DatastarResponse(build_status_stream())


async def _events_query_status(request: Request) -> Response:
    """SSE endpoint for real-time query execution updates."""
    from datastar_py.starlette import DatastarResponse
    query_id = request.query_params.get("queryId", "unknown")
    return DatastarResponse(query_status_stream(query_id))


async def _events_notifications(request: Request) -> Response:
    """SSE endpoint for real-time notifications."""
    from datastar_py.starlette import DatastarResponse
    return DatastarResponse(notification_stream())


def create_app(context: DashboardContext) -> Starlette:
    routes = [
        Route("/", _home, methods=["GET"]),
        Route("/views", _views, methods=["GET"]),
        Route("/views/{name:str}", _view_detail, methods=["GET"]),
        Route("/query", _query_get, methods=["GET"]),
        Route("/query", _query_post, methods=["POST"]),
        Route("/build", _build, methods=["POST"]),
        # Datastar SSE endpoints
        Route("/events/build-status", _events_build_status, methods=["GET"]),
        Route("/events/query-status", _events_query_status, methods=["GET"]),
        Route("/events/notifications", _events_notifications, methods=["GET"]),
    ]

    app = Starlette(debug=False, routes=routes)
    app.state.dashboard_ctx = context  # type: ignore[attr-defined]

    # Mount static files for CSS and JavaScript
    static_dir = Path(__file__).parent.parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    return app
