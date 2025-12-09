"""Query interface route handlers with SSE support."""

from __future__ import annotations

import asyncio
from typing import AsyncGenerator
from datetime import datetime

from litestar import Controller, get, post, Request
from litestar.response import Response
from litestar.exceptions import HTTPException

from datastar_py import ServerSentEventGenerator as SSE
from datastar_py.litestar import DatastarResponse, datastar_response, read_signals

from ..components import base_layout, page_header, card, table_component, table_header_component, table_rows_component
from ..state import DashboardContext
from ...engine import build_catalog, EngineError
from htpy import button, div, form, label, p, span, textarea


# Global build status tracking
_build_status = {
    "status": "idle",  # idle, building, complete, error
    "progress": 0,
    "message": "",
    "timestamp": None,
    "error": None,
}
_build_lock = asyncio.Lock()


class QueryController(Controller):
    """Query interface controller with SSE support."""

    path = "/query"

    @get()
    async def query_form(self, ctx: DashboardContext) -> Response[str]:
        """Render the query interface."""
        content = div(class_="space-y-6")[
            page_header(
                "Query",
                subtitle="Execute SQL queries against the catalog",
            ),
            card(
                "SQL Query",
                div(**{"data-signals": '{"sql": "", "loading": false, "error": ""}'})[
                    form(class_="space-y-4")[
                        div[
                            label(
                                for_="sql-input",
                                class_="block text-sm font-medium text-gray-700 dark:text-gray-300",
                            )["SQL Query"],
                            textarea(
                                id="sql-input",
                                name="sql",
                                rows="6",
                                class_="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white font-mono",
                                placeholder="SELECT * FROM information_schema.tables LIMIT 10",
                                **{"data-bind": "sql"},
                            ),
                        ],
                        div(class_="flex items-center gap-4")[
                            button(
                                type="button",
                                class_="btn inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500",
                                **{
                                    "data-on-click": "$$post('/query/execute')",
                                    "data-indicator": "loading",
                                },
                            )["Execute Query"],
                            span(
                                class_="text-sm text-gray-500",
                                **{"data-show": "$loading"},
                            )["Running..."],
                        ],
                    ],
                    # Error display
                    div(
                        class_="mt-4 p-4 bg-red-50 dark:bg-red-900 rounded-md",
                        **{"data-show": "$error"},
                    )[
                        p(
                            class_="text-sm text-red-700 dark:text-red-200",
                            **{"data-text": "$error"},
                        )
                    ],
                ],
            ),
            # Results area
            card(
                "Results",
                div(id="query-results", class_="min-h-[200px]")[
                    p(class_="text-gray-500 text-center py-8")[
                        "Execute a query to see results"
                    ]
                ],
            ),
        ]

        html = str(base_layout("Query", content))
        return Response(content=html, media_type="text/html")

    @post("/execute")
    @datastar_response
    async def execute_query(
        self, request: Request, ctx: DashboardContext
    ) -> AsyncGenerator:
        """Execute a query and stream results via SSE."""
        signals = await read_signals(request)

        if not signals:
            yield SSE.patch_signals({"error": "No query provided", "loading": False})
            return

        sql = signals.get("sql", "").strip()
        if not sql:
            yield SSE.patch_signals({"error": "Please enter a SQL query", "loading": False})
            return

        # Clear any previous error
        yield SSE.patch_signals({"error": "", "loading": True})

        try:
            # Execute the query and stream results
            row_count = 0
            first_batch = True
            columns = None

            async for batch_columns, batch_rows in ctx.execute_query(sql):
                if first_batch:
                    # First batch: contains column headers
                    columns = batch_columns
                    first_batch = False

                    if not columns:
                        yield SSE.patch_elements(
                            '<div id="query-results"><p class="text-gray-500 text-center py-8">Query returned no results</p></div>',
                            selector="#query-results",
                            mode="morph",
                        )
                        break

                    # Send initial table structure with header
                    header_html = str(table_header_component(columns))
                    result_html = f'''<div id="query-results">
                        <p class="text-sm text-gray-500 mb-2" id="row-count">Streaming results...</p>
                        {header_html}
                    </div>'''
                    yield SSE.patch_elements(
                        result_html,
                        selector="#query-results",
                        mode="morph",
                    )
                else:
                    # Subsequent batches: append rows to tbody
                    if batch_rows:
                        row_count += len(batch_rows)
                        rows_html = table_rows_component(batch_rows)
                        yield SSE.patch_elements(
                            rows_html,
                            selector="#results-tbody",
                            mode="append",
                        )

            # Send final row count
            if not first_batch:
                truncated = row_count >= ctx.row_limit
                count_text = f"{row_count} row(s) returned"
                if truncated:
                    count_text += f" (limited to {ctx.row_limit})"

                yield SSE.patch_signals({"loading": False, "row_count": count_text})
                yield SSE.patch_elements(
                    count_text,
                    selector="#row-count",
                    mode="text",
                )

        except ValueError as e:
            yield SSE.patch_signals({"error": str(e), "loading": False})
        except Exception as e:
            yield SSE.patch_signals({"error": f"Query error: {e}", "loading": False})
        finally:
            yield SSE.patch_signals({"loading": False})


class BuildController(Controller):
    """Build status streaming controller."""

    path = "/build"

    @post()
    async def trigger_build(
        self, request: Request, ctx: DashboardContext
    ) -> dict[str, str]:
        """Trigger a catalog build."""
        global _build_status, _build_lock

        async with _build_lock:
            if _build_status["status"] == "building":
                raise HTTPException(
                    status_code=409, detail="Build already in progress"
                )

            # Reset status
            _build_status = {
                "status": "building",
                "progress": 0,
                "message": "Starting build...",
                "timestamp": datetime.now().isoformat(),
                "error": None,
            }

            # Trigger async build
            asyncio.create_task(_run_build(ctx.config_path, ctx.db_path))

            return {"status": "started"}

    @get("/status")
    @datastar_response
    async def build_status(self, request: Request) -> AsyncGenerator:
        """Stream build status updates via SSE."""
        global _build_status

        # Send initial status
        yield SSE.patch_signals(_build_status)

        # Send heartbeat every 30 seconds using patch_signals
        heartbeat_interval = 30
        heartbeat_count = 0

        try:
            while True:
                await asyncio.sleep(heartbeat_interval)
                heartbeat_count += 1
                # Send heartbeat as a signal update
                yield SSE.patch_signals({"heartbeat": heartbeat_count})

        except asyncio.CancelledError:
            # Client disconnected
            pass


async def _run_build(config_path: str, db_path: str | None) -> None:
    """Run the build process and update status."""
    global _build_status

    try:
        _build_status["progress"] = 10
        _build_status["message"] = "Loading configuration..."
        await asyncio.sleep(0.1)

        _build_status["progress"] = 30
        _build_status["message"] = "Building catalog..."
        await asyncio.sleep(0.1)

        # Run the actual build
        build_catalog(config_path, db_path=db_path, verbose=False)

        _build_status["progress"] = 100
        _build_status["message"] = "Build completed successfully"
        _build_status["status"] = "complete"
        _build_status["timestamp"] = datetime.now().isoformat()

    except EngineError as e:
        _build_status["status"] = "error"
        _build_status["error"] = str(e)
        _build_status["message"] = f"Build failed: {e}"
        _build_status["timestamp"] = datetime.now().isoformat()
    except Exception as e:
        _build_status["status"] = "error"
        _build_status["error"] = str(e)
        _build_status["message"] = f"Unexpected error: {e}"
        _build_status["timestamp"] = datetime.now().isoformat()

