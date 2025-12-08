"""Views route handlers."""

from __future__ import annotations

from litestar.response import Response

from ..components import layout, tables
from ..state import DashboardContext


async def views_page(ctx: DashboardContext, q: str | None) -> Response:
    """Generate the views listing page."""
    rows = ctx.view_list()

    if q:
        q_lower = q.lower()
        rows = [r for r in rows if q_lower in r["name"].lower()]

    search_form = f"""
    <form method="GET" class="mb-6">
        <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
                </svg>
            </div>
            <input
                type="text"
                name="q"
                value="{q or ''}"
                placeholder="Search view name..."
                class="block w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
        </div>
    </form>
    """

    view_rows = []
    for view in rows:
        view_rows.append([
            f'<a href="/views/{view["name"]}" class="text-blue-600 dark:text-blue-400 hover:underline">{view["name"]}</a>',
            view.get("source", ""),
            view.get("uri", ""),
            view.get("database", ""),
            view.get("table", ""),
            "✅" if view.get("semantic") == "yes" else "—",
        ])

    table = tables.data_table(
        columns=["Name", "Source", "URI", "Database", "Table", "Semantic"],
        rows=view_rows,
    )

    back_link = '<a href="/" class="text-blue-600 dark:text-blue-400 hover:underline">&larr; Back to home</a>'

    content = (
        layout.page_header("Views", f"Found {len(rows)} view(s)") +
        layout.page_container(search_form + table + '<div class="mt-6">' + back_link + '</div>')
    )

    html = layout.html_document("Views - Duckalog Dashboard", content)

    return Response(html, media_type="text/html")


async def view_detail_page(ctx: DashboardContext, name: str) -> Response:
    """Generate a view detail page."""
    view = ctx.get_view(name)

    if view is None:
        content = (
            layout.page_header("View Not Found", None) +
            layout.page_container(
                '<div class="bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded-lg p-4 text-red-800 dark:text-red-200">'
                'The requested view was not found.'
                '</div>'
                '<div class="mt-6"><a href="/views" class="text-blue-600 dark:text-blue-400 hover:underline">&larr; Back to views</a></div>'
            )
        )
        html = layout.html_document("View Not Found - Duckalog Dashboard", content)
        return Response(html, media_type="text/html", status_code=404)

    semantic_models = ctx.semantic_for_view(name)

    definition_parts = []
    if view.sql:
        definition_parts.append(view.sql)
    else:
        definition_parts.append(f"source={view.source or 'sql'}")
        if view.uri:
            definition_parts.append(f"uri={view.uri}")
        if view.database:
            definition_parts.append(f"database={view.database}")
        if view.table:
            definition_parts.append(f"table={view.table}")

    definition_block = f"""
    <div class="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
        <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Definition</h3>
        <pre class="text-sm text-gray-900 dark:text-gray-100 overflow-x-auto">{chr(10).join(definition_parts)}</pre>
    </div>
    """

    semantics_block = ""
    if semantic_models:
        semantics_html = ""
        for sm in semantic_models:
            semantics_html += f"""
            <div class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 mb-4">
                <h4 class="font-medium text-gray-900 dark:text-white mb-2">Semantic Model: {sm.name}</h4>
                <div class="space-y-2">
                    <div>
                        <span class="text-sm font-medium text-gray-500 dark:text-gray-400">Dimensions:</span>
                        <span class="text-sm text-gray-900 dark:text-gray-100">{', '.join(d.name for d in sm.dimensions) or '—'}</span>
                    </div>
                    <div>
                        <span class="text-sm font-medium text-gray-500 dark:text-gray-400">Measures:</span>
                        <span class="text-sm text-gray-900 dark:text-gray-100">{', '.join(m.name for m in sm.measures) or '—'}</span>
                    </div>
                </div>
            </div>
            """
        semantics_block = f"""
        <div class="mt-6">
            <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Semantic Layer Metadata</h3>
            {semantics_html}
        </div>
        """
    else:
        semantics_block = """
        <div class="mt-6">
            <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Semantic Layer Metadata</h3>
            <p class="text-gray-500 dark:text-gray-400">No semantic-layer metadata for this view.</p>
        </div>
        """

    content = (
        layout.page_header(f"View: {name}", None) +
        layout.page_container(
            definition_block +
            semantics_block +
            '<div class="mt-6"><a href="/views" class="text-blue-600 dark:text-blue-400 hover:underline">&larr; Back to views</a></div>'
        )
    )

    html = layout.html_document(f"View {name} - Duckalog Dashboard", content)

    return Response(html, media_type="text/html")
