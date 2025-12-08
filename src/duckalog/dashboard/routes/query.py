"""Query route handlers."""

from __future__ import annotations

import json
from typing import Any

from litestar import MediaType
from litestar.response import Response

from ..components import layout, forms, tables
from ..state import DashboardContext, QueryResult


async def query_page(result: QueryResult | None = None, sql_text: str = "") -> Response:
    """Generate the query interface page."""
    table_content = ""

    if result:
        if result.error:
            table_content = f"""
            <div class="bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded-lg p-4 text-red-800 dark:text-red-200">
                <div class="flex">
                    <svg class="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                    <p class="font-medium">Error executing query</p>
                </div>
                <pre class="mt-2 text-sm overflow-x-auto">{result.error}</pre>
            </div>
            """
        else:
            table_content = tables.query_results_table(result.columns, result.rows, result.truncated)

    # Enhanced query form with Datastar attributes for real-time submission
    query_form = forms.query_form(
        initial_sql=sql_text,
        datastar_signal="query_sql",
        action="/query/stream",
        method="POST"
    )

    content = (
        layout.page_header("Ad-hoc Query", "Execute SQL queries against your DuckDB database") +
        layout.page_container(
            '<div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">' +
            query_form +
            '</div>' +
            '<div id="query-results-container">' +
            table_content +
            '</div>' +
            '<div class="mt-6"><a href="/" class="text-blue-600 dark:text-blue-400 hover:underline">&larr; Back to home</a></div>'
        )
    )

    html = layout.html_document("Query - Duckalog Dashboard", content)

    return Response(html, media_type="text/html")


async def execute_query(ctx: DashboardContext, sql: str) -> Response:
    """Execute a SQL query and return results."""
    result = ctx.run_query(sql)
    return await query_page(result=result, sql_text=sql)


async def execute_query_stream(ctx: DashboardContext, sql: str) -> Response:
    """Execute a SQL query and stream results via Server-Sent Events."""

    async def event_stream():
        """Generate SSE events for query execution."""
        events = []

        try:
            # Send start event
            events.append(f"event: datastar-patch-signals\n")
            events.append(f"data: {json.dumps({'signals': {'query_running': True, 'query_error': None, 'query_results': None}})}\n\n")

            # Execute query
            result = ctx.run_query(sql)

            if result.error:
                # Send error result
                events.append(f"event: datastar-patch-signals\n")
                events.append(f"data: {json.dumps({'signals': {'query_running': False, 'query_error': result.error, 'query_results': None}})}\n\n")
            else:
                # Convert results to dictionary format
                results_data = {
                    'columns': result.columns,
                    'rows': [[str(cell) for cell in row] for row in result.rows],
                    'truncated': result.truncated,
                    'row_count': len(result.rows)
                }

                # Send successful results
                events.append(f"event: datastar-patch-signals\n")
                events.append(f"data: {json.dumps({'signals': {'query_running': False, 'query_error': None, 'query_results': results_data}})}\n\n")

            # Send completion event
            events.append(f"event: datastar-patch-signals\n")
            events.append(f"data: {json.dumps({'signals': {'query_complete': True}})}\n\n")

        except Exception as exc:
            # Send error event
            events.append(f"event: datastar-patch-signals\n")
            events.append(f"data: {json.dumps({'signals': {'query_running': False, 'query_error': str(exc), 'query_results': None}})}\n\n")

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


async def render_query_results(signals: dict[str, Any]) -> str:
    """Render query results from Datastar signals for HTML response."""
    query_results = signals.get('query_results')

    if not query_results:
        if signals.get('query_error'):
            return f"""
            <div class="bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded-lg p-4 text-red-800 dark:text-red-200">
                <div class="flex">
                    <svg class="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                    <p class="font-medium">Error executing query</p>
                </div>
                <pre class="mt-2 text-sm overflow-x-auto">{signals['query_error']}</pre>
            </div>
            """
        return ""

    # Format results as table
    columns = query_results.get('columns', [])
    rows = query_results.get('rows', [])
    truncated = query_results.get('truncated', False)
    row_count = query_results.get('row_count', len(rows))

    if not rows:
        return '<div class="text-gray-500 dark:text-gray-400">No results returned</div>'

    # Generate table HTML
    table_html = tables.query_results_table(columns, rows, truncated)

    return table_html
