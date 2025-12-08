"""Table components for the dashboard."""

from __future__ import annotations

import htpy as h


def data_table(
    headers: list[str],
    rows: list[list[str]],
    caption: str = "",
    sortable: bool = False
) -> h.Element:
    """Create a modern data table with responsive design."""
    return h.table(
        h.caption(caption) if caption else "",
        h.thead(
            h.tr(
                h.th(scope="col")(header) for header in headers
            )
        ),
        h.tbody(
            h.tr(
                h.td(scope="row")(cell) for cell in row
            ) for row in rows
        ),
    )


def view_table(views: list[dict]) -> str:
    """Create a specialized table for catalog views."""
    if not views:
        return "<p>No views found in the catalog.</p>"

    headers = ["Name", "Source", "Database", "Table", "Semantic Models"]
    rows_html = ""

    for view in views:
        row_html = f"""
            <tr>
                <td><a href="/views/{view['name']}">{view['name']}</a></td>
                <td>{view.get('source', 'sql')}</td>
                <td>{view.get('database', '')}</td>
                <td>{view.get('table', '')}</td>
                <td>{view.get('semantic', 'no')}</td>
            </tr>
        """
        rows_html += row_html

    headers_html = "".join(f"<th>{header}</th>" for header in headers)

    return f"""
        <table>
            <caption>Catalog Views ({len(views)} total)</caption>
            <thead>
                <tr>{headers_html}</tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    """


def query_results_table(columns: list[str], rows: list[tuple], truncated: bool = False) -> str:
    """Create a table for query results."""
    if not columns:
        return "<p>No results to display.</p>"

    headers_html = "".join(f"<th>{col}</th>" for col in columns)
    rows_html = ""

    for row in rows:
        cells_html = "".join(f"<td>{str(cell)}</td>" for cell in row)
        rows_html += f"<tr>{cells_html}</tr>"

    note_text = "Results truncated" if truncated else f"Showing all {len(rows)} rows"

    return f"""
        <div>
            <table>
                <caption>Query Results ({len(rows)} rows)</caption>
                <thead>
                    <tr>{headers_html}</tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
            <small style="color: var(--muted-color)">{note_text}</small>
        </div>
    """


def search_form(query: str = "", action: str = "/search", method: str = "GET") -> h.Element:
    """Create a search form component."""
    return h.form(action=action, method=method)(
        h.fieldset(
            h.input(
                type="search",
                name="q",
                placeholder="Search...",
                value=query,
            ),
            h.button(type="submit")("Search"),
        ),
    )


def pagination_info(
    current_page: int,
    total_pages: int,
    total_items: int,
    items_per_page: int
) -> h.Element:
    """Display pagination information."""
    start_item = (current_page - 1) * items_per_page + 1
    end_item = min(start_item + items_per_page - 1, total_items)

    return h.small(
        f"Showing {start_item}-{end_item} of {total_items} items (page {current_page} of {total_pages})"
    )


def status_badge(status: str, text: str = None) -> h.Element:
    """Create a status badge with appropriate styling."""
    status_map = {
        "success": ("✅", "Success"),
        "error": ("❌", "Error"),
        "warning": ("⚠️", "Warning"),
        "info": ("ℹ️", "Info"),
        "loading": ("🔄", "Loading"),
    }

    icon, default_text = status_map.get(status, ("", status))
    display_text = text or default_text

    return h.span(style=f"background-color: var(--{status}-color); color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8em;")(
        f"{icon} {display_text}" if icon else display_text
    )