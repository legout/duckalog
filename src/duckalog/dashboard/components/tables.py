"""Table components for displaying data."""

from __future__ import annotations

from typing import Any, Iterable


def data_table(
    columns: list[str],
    rows: Iterable[Iterable[Any]],
    searchable: bool = False,
    datastar_signal: str | None = None,
) -> str:
    """Generate a responsive data table with optional Datastar integration."""
    # Generate column headers
    header_cells = "".join(
        f'<th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">{col}</th>'
        for col in columns
    )

    # Generate table rows
    table_rows = ""
    for row in rows:
        cells = "".join(
            f'<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">{str(cell) if cell is not None else ""}</td>'
            for cell in row
        )
        table_rows += f'<tr class="hover:bg-gray-50 dark:hover:bg-gray-700">{cells}</tr>'

    search_input = ""
    if searchable and datastar_signal:
        search_input = f"""
        <div class="mb-4">
            <label for="search" class="sr-only">Search</label>
            <div class="relative">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
                    </svg>
                </div>
                <input
                    type="text"
                    id="search"
                    class="block w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Search..."
                    data-bind="{datastar_signal}"
                    data-on-input="$$put('/api/search', {{body: {{q: $el.value}}}})"
                />
            </div>
        </div>
        """

    table_html = f"""
    <div class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
        <table class="min-w-full divide-y divide-gray-300 dark:divide-gray-600">
            <thead class="bg-gray-50 dark:bg-gray-800">
                <tr>
                    {header_cells}
                </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                {table_rows if table_rows else '<tr><td colspan="' + str(len(columns)) + '" class="px-6 py-4 text-center text-gray-500 dark:text-gray-400">No data</td></tr>'}
            </tbody>
        </table>
    </div>
    """

    return f"""
    <div class="space-y-4">
        {search_input}
        {table_html}
    </div>
    """


def view_list_table(views: list[dict[str, Any]], datastar_signal: str | None = None) -> str:
    """Generate a table for listing views."""
    columns = ["Name", "Source", "URI", "Database", "Table", "Semantic"]
    rows = []
    for view in views:
        rows.append([
            view.get("name", ""),
            view.get("source", ""),
            view.get("uri", ""),
            view.get("database", ""),
            view.get("table", ""),
            view.get("semantic", "no"),
        ])

    return data_table(columns, rows, searchable=True, datastar_signal=datastar_signal)


def query_results_table(columns: list[str], rows: list[tuple], truncated: bool = False) -> str:
    """Generate a table for displaying query results."""
    # Generate header
    header_cells = "".join(
        f'<th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">{col}</th>'
        for col in columns
    )

    # Generate rows
    table_rows = ""
    for row in rows:
        cells = "".join(
            f'<td class="px-6 py-4 text-sm text-gray-900 dark:text-gray-100">{str(cell) if cell is not None else "NULL"}</td>'
            for cell in row
        )
        table_rows += f'<tr>{cells}</tr>'

    truncated_msg = ""
    if truncated:
        truncated_msg = """
        <div class="mt-4 p-3 bg-yellow-50 dark:bg-yellow-900 rounded-lg">
            <p class="text-sm text-yellow-800 dark:text-yellow-200">
                <svg class="inline w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
                </svg>
                Results truncated for display
            </p>
        </div>
        """

    return f"""
    <div class="space-y-4">
        <div class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
            <table class="min-w-full divide-y divide-gray-300 dark:divide-gray-600">
                <thead class="bg-gray-50 dark:bg-gray-800">
                    <tr>
                        {header_cells}
                    </tr>
                </thead>
                <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                    {table_rows if table_rows else '<tr><td colspan="' + str(len(columns)) + '" class="px-6 py-4 text-center text-gray-500 dark:text-gray-400">No results</td></tr>'}
                </tbody>
            </table>
        </div>
        {truncated_msg}
    </div>
    """


def build_status_table(build_status: dict[str, Any] | None) -> str:
    """Generate a table for build status information."""
    if not build_status:
        content = """
        <div class="text-center py-8 text-gray-500 dark:text-gray-400">
            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            <p class="mt-2">No builds have been run yet</p>
        </div>
        """
        return card(content)

    success = build_status.get("success")
    status_icon = "✅" if success else "❌" if success is False else "⏳"
    status_text = "Success" if success else "Failed" if success is False else "In Progress"
    status_color = "text-green-800 dark:text-green-200 bg-green-50 dark:bg-green-900" if success else "text-red-800 dark:text-red-200 bg-red-50 dark:bg-red-900" if success is False else "text-yellow-800 dark:text-yellow-200 bg-yellow-50 dark:bg-yellow-900"

    content = f"""
    <div class="space-y-4">
        <div class="flex items-center justify-between">
            <h3 class="text-lg font-medium text-gray-900 dark:text-white">Build Status</h3>
            <span class="px-3 py-1 rounded-full text-sm font-medium {status_color}">
                {status_icon} {status_text}
            </span>
        </div>
        <dl class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
                <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">Started</dt>
                <dd class="mt-1 text-sm text-gray-900 dark:text-gray-100">{build_status.get('started_at', 'N/A')}</dd>
            </div>
            <div>
                <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">Completed</dt>
                <dd class="mt-1 text-sm text-gray-900 dark:text-gray-100">{build_status.get('completed_at', 'N/A')}</dd>
            </div>
            <div>
                <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">Duration</dt>
                <dd class="mt-1 text-sm text-gray-900 dark:text-gray-100">{build_status.get('duration_seconds', 'N/A')}s</dd>
            </div>
            <div>
                <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">Summary</dt>
                <dd class="mt-1 text-sm text-gray-900 dark:text-gray-100">{build_status.get('summary', 'N/A')}</dd>
            </div>
        </dl>
        {f'<p class="mt-4 text-sm text-red-600 dark:text-red-400">{build_status.get("message", "")}</p>' if build_status.get("message") else ""}
    </div>
    """

    return card(content)


def card(title: str, content: str) -> str:
    """Generate a card component (imported from layout if needed)."""
    return f"""
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">{title}</h3>
        {content}
    </div>
    """
