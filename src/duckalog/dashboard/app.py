"""Litestar app factory for the duckalog dashboard."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from litestar import Litestar, get, post
from litestar.connection import Request
from litestar.response import Response, Template
from litestar.static_files import StaticFilesConfig

from .routes.home import home_page
from .routes.views import views_page, view_detail_page
from .routes.query import query_page, execute_query, execute_query_stream
from .routes.build import build_catalog_trigger, build_catalog_stream
from .state import DashboardContext


def create_app(context: DashboardContext) -> Litestar:
    """Create and configure the Litestar application."""

    @get("/", cache=False)
    async def home() -> Response:
        """Dashboard home page."""
        return await home_page(context)

    @get("/views", cache=False)
    async def views(request: Request) -> Response:
        """List all views."""
        q = request.query_params.get("q")
        return await views_page(context, q)

    @get("/views/{name:str}", cache=False)
    async def view_detail(request: Request) -> Response:
        """View detail page."""
        name = request.path_params["name"]
        return await view_detail_page(context, name)

    @get("/query", cache=False)
    async def query_get() -> Response:
        """Query interface page."""
        return await query_page()

    @post("/query", cache=False)
    async def query_post(request: Request) -> Response:
        """Execute query and stream results."""
        form_data = await request.form()
        sql = form_data.get("sql") or ""
        return await execute_query(context, str(sql))

    @post("/query/stream", cache=False)
    async def query_stream(request: Request) -> Response:
        """Execute query and stream results via Server-Sent Events."""
        form_data = await request.form()
        sql = form_data.get("sql") or ""
        return await execute_query_stream(context, str(sql))

    @post("/build", cache=False)
    async def build() -> Response:
        """Trigger catalog build."""
        return await build_catalog_trigger(context)

    @post("/build/stream", cache=False)
    async def build_stream() -> Response:
        """Trigger catalog build and stream status."""
        return await build_catalog_stream(context)

    static_dir = Path(__file__).parent.parent / "static"

    app = Litestar(
        route_handlers=[
            home,
            views,
            view_detail,
            query_get,
            query_post,
            query_stream,
            build,
            build_stream,
        ],
        static_files_config=[
            StaticFilesConfig(
                path="/static",
                directories=[str(static_dir)] if static_dir.exists() else [],
            )
        ] if static_dir.exists() else [],
        type_encoders={},
    )

    app.state.dashboard_ctx = context  # type: ignore[attr-defined]

    return app
