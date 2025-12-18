"""Litestar application factory for the dashboard."""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

from litestar import Litestar, get
from litestar.response import Response
from litestar.static_files import create_static_files_router
from litestar.di import Provide
from litestar.status_codes import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR

from .state import DashboardContext
from .routes import HomeController, ViewsController, QueryController, BuildController

if TYPE_CHECKING:
    from duckalog.config import Config


async def startup_handler() -> None:
    """Startup handler to initialize database connection."""
    # The context will be created via dependency injection
    # This handler just ensures the connection is established


async def shutdown_handler() -> None:
    """Shutdown handler to close database connection."""
    # Context cleanup happens automatically via dependency disposal


@get("/health")
async def health_check(ctx: DashboardContext) -> Response[dict]:
    """Health check endpoint.

    Returns:
        JSON response with status and timestamp
    """
    try:
        # Check if connection is alive by executing a simple query
        ctx.connection.execute("SELECT 1")
        return Response(
            {"status": "healthy", "timestamp": ctx._get_timestamp()},
            status_code=HTTP_200_OK,
            media_type="application/json",
        )
    except Exception as e:
        return Response(
            {"status": "unhealthy", "error": str(e), "timestamp": ctx._get_timestamp()},
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            media_type="application/json",
        )


def create_app(
    config: "Config",
    config_path: str,
    *,
    db_path: str | None = None,
    row_limit: int = 1000,
    static_dir: str | None = None,
) -> Litestar:
    """Create the Litestar dashboard application.

    Args:
        config: Duckalog configuration object
        config_path: Path to the configuration file
        db_path: Optional path to DuckDB database file
        row_limit: Maximum rows to return from queries
        static_dir: Optional custom static files directory

    Returns:
        Configured Litestar application
    """
    # Create the dashboard context
    ctx = DashboardContext(
        config=config,
        config_path=config_path,
        db_path=db_path,
        row_limit=row_limit,
    )

    # Determine static files directory
    if static_dir is None:
        # Default to package's static directory
        static_dir = str(Path(__file__).parent.parent / "static")

    # Dependency provider for context
    async def provide_ctx() -> DashboardContext:
        return ctx

    # Create static files router
    static_router = create_static_files_router(
        path="/static",
        directories=[static_dir],
        name="static",
    )

    # Create the application
    # Check for debug override via environment variable
    debug_mode = os.getenv("DASHBOARD_DEBUG", "false").lower() == "true"

    app = Litestar(
        route_handlers=[
            HomeController,
            ViewsController,
            QueryController,
            BuildController,
            health_check,
            static_router,
        ],
        dependencies={"ctx": Provide(provide_ctx)},
        debug=debug_mode,
        on_startup=[startup_handler],
        on_shutdown=[shutdown_handler],
    )

    return app
