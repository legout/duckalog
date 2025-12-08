"""ASGI app factory for the duckalog dashboard."""

from __future__ import annotations


from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response, JSONResponse
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles

from .datastar import DatastarSignals, sse_event_stream
from .middleware import CORSMiddleware, SecurityHeadersMiddleware
from .query_validator import validate_dashboard_query
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

    # Validate SQL for security
    is_valid, error_message = validate_dashboard_query(str(sql))
    if not is_valid:
        # Create an error result
        from .state import QueryResult
        error_result = QueryResult(columns=[], rows=[], truncated=False, error=f"Security validation failed: {error_message}")
        return query_page(result=error_result, sql_text=str(sql))

    result = ctx.run_query(str(sql))
    return query_page(result=result, sql_text=str(sql))


async def _build(request: Request) -> Response:
    ctx: DashboardContext = request.app.state.dashboard_ctx  # type: ignore[attr-defined]
    ctx.trigger_build()
    return RedirectResponse(url="/", status_code=303)


# Datastar API endpoints
async def _api_summary(request: Request) -> Response:
    """API endpoint for dashboard summary data."""
    ctx: DashboardContext = request.app.state.dashboard_ctx  # type: ignore[attr-defined]
    signals = DatastarSignals(ctx)
    return JSONResponse(signals.get_summary_signals())


async def _api_views(request: Request) -> Response:
    """API endpoint for views data."""
    ctx: DashboardContext = request.app.state.dashboard_ctx  # type: ignore[attr-defined]
    search_query = request.query_params.get("q", "")
    signals = DatastarSignals(ctx)
    return JSONResponse(signals.get_views_signals(search_query))


async def _api_query(request: Request) -> Response:
    """API endpoint for query execution."""
    ctx: DashboardContext = request.app.state.dashboard_ctx  # type: ignore[attr-defined]

    try:
        # Get SQL from request body
        body = await request.json()
        sql = body.get("sql", "")

        if not sql.strip():
            return JSONResponse({
                "columns": [],
                "rows": [],
                "truncated": False,
                "error": "Empty SQL query",
            })

        # Validate SQL for security
        is_valid, error_message = validate_dashboard_query(sql)
        if not is_valid:
            return JSONResponse({
                "columns": [],
                "rows": [],
                "truncated": False,
                "error": f"Security validation failed: {error_message}",
            })

        # Execute query
        result = ctx.run_query(sql)

        return JSONResponse({
            "columns": result.columns,
            "rows": result.rows,
            "truncated": result.truncated,
            "error": result.error,
        })

    except Exception as e:
        return JSONResponse({
            "columns": [],
            "rows": [],
            "truncated": False,
            "error": str(e),
        })


async def _sse_events(request: Request) -> Response:
    """Server-Sent Events endpoint for real-time updates."""
    ctx: DashboardContext = request.app.state.dashboard_ctx  # type: ignore[attr-defined]
    return await sse_event_stream(request, ctx)


def create_app(context: DashboardContext, host: str = "127.0.0.1") -> Starlette:
    # Determine the path to static files relative to this file
    import os
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")

    routes = [
        Route("/", _home, methods=["GET"]),
        Route("/views", _views, methods=["GET"]),
        Route("/views/{name:str}", _view_detail, methods=["GET"]),
        Route("/query", _query_get, methods=["GET"]),
        Route("/query", _query_post, methods=["POST"]),
        Route("/build", _build, methods=["POST"]),
        # Datastar API endpoints
        Route("/api/summary", _api_summary, methods=["GET"]),
        Route("/api/views", _api_views, methods=["GET"]),
        Route("/api/query", _api_query, methods=["POST"]),
        Route("/sse/events", _sse_events, methods=["GET"]),
        Mount("/static", StaticFiles(directory=static_dir), name="static"),
    ]

    app = Starlette(debug=False, routes=routes)
    app.state.dashboard_ctx = context  # type: ignore[attr-defined]

    # Add security middleware
    # For localhost-only access, restrict CORS to local addresses
    allowed_hosts = [host, "127.0.0.1", "localhost", "::1"]
    if host not in allowed_hosts:
        allowed_hosts.append(host)

    app.add_middleware(CORSMiddleware, allow_hosts=allowed_hosts)
    app.add_middleware(SecurityHeadersMiddleware)

    return app
