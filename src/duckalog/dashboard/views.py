"""Modern dashboard views using HTPY components."""

from __future__ import annotations

from starlette.responses import HTMLResponse
import htpy as h

from .components import page, card, button, forms, tables, navigation, base
from .components.reactive import (
    build_status_card,
    live_search_form,
    real_time_notification_center,
    reactive_query_editor,
)
from .state import DashboardContext, QueryResult, summarize_config


def _div_with_children(class_name: str = "", style: str = "", children: list[str] = None) -> str:
    """Helper function to create div with HTML content as strings."""
    attrs = []
    if class_name:
        attrs.append(f'class="{class_name}"')
    if style:
        attrs.append(f'style="{style}"')

    attr_str = " " + " ".join(attrs) if attrs else ""
    children_content = "".join(children or [])

    return f"<div{attr_str}>{children_content}</div>"


def _grid_with_children(style: str = "", children: list[str] = None) -> str:
    """Helper function to create grid layout with HTML content."""
    return _div_with_children(style=style, children=children)


def home_page(ctx: DashboardContext) -> HTMLResponse:
    """Modern home page with professional layout and metrics cards."""
    summary = summarize_config(ctx)
    last = ctx.last_build

    # Create status indicator
    status_badge = "success" if last and last.success else "error" if last and last.success is False else "info"
    status_text = (
        "✅ Build completed successfully" if last and last.success
        else "❌ Build failed" if last and last.success is False
        else "— No builds run yet"
    )
    if last and last.completed_at:
        status_text += f" at {last.completed_at.strftime('%Y-%m-%d %H:%M:%S')}"

    # Create metrics cards with string-based content to avoid HTPY issues
    config_content = f"""
        <p>Path: {summary['config_path']}</p>
        <p>DuckDB: {summary['database']}</p>
        <p>Total items: {summary['views']} views, {summary['attachments']} attachments, {summary['semantic_models']} semantic models</p>
    """

    views_content = f"""
        <p>Total catalog views: {summary['views']}</p>
        <p>Views with semantic models: {summary['semantic_models']}</p>
        <p>View detailed information and semantic layer definitions</p>
    """

    build_duration = f"{last.duration_seconds or 0:.2f}s" if last else "No recent builds"
    build_content = f"""
        <p>Status: {status_text}</p>
        <p>Build duration: {build_duration}</p>
        <p>Trigger new builds to refresh catalog data</p>
    """

    config_card = card(
        "Configuration",
        config_content,
        [button("🔧 Edit", href="/config", primary=False)]
    )

    views_card = card(
        "Views Overview",
        views_content,
        [button("📊 Browse Views", href="/views", primary=True)]
    )

    build_card = build_status_card()

    navigation_links = [
        ("📊 Browse Views", "/views"),
        ("🔍 Run Query", "/query"),
        ("⚙️ Configuration", "/config"),
    ]

    # Create grid layout as string to avoid HTPY nesting issues
    grid_html = _grid_with_children(
        style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; margin: 2rem 0;",
        children=[str(config_card), str(views_card), str(build_card)]
    )

    content = [
        navigation.header("Dashboard Overview", "Manage and explore your DuckDB catalog"),
        grid_html,
        navigation.quick_links(navigation_links),
        real_time_notification_center(),
        navigation.footer(),
    ]

    page_html = page("Duckalog Dashboard", content)
    return HTMLResponse(str(page_html))


def views_page(ctx: DashboardContext, q: str | None) -> HTMLResponse:
    """Modern views browser with search and filtering capabilities."""
    rows = ctx.view_list()
    if q:
        q_lower = q.lower()
        rows = [r for r in rows if q_lower in r["name"].lower()]

    search_form = live_search_form()
    views_table = tables.view_table(rows)
    breadcrumb_items = [("Dashboard", "/"), ("Views", "/views")]

    content = [
        navigation.breadcrumb(breadcrumb_items),
        navigation.header("Catalog Views", f"Found {len(rows)} view{'s' if len(rows) != 1 else ''}"),

        navigation.action_bar([search_form]),

        views_table,

        navigation.back_button("/", "← Back to Dashboard"),
        navigation.footer(),
    ]

    page_html = page("Catalog Views", content)
    return HTMLResponse(str(page_html))


def view_detail_page(ctx: DashboardContext, name: str) -> HTMLResponse:
    """Modern view detail page with enhanced semantic model display."""
    view = ctx.get_view(name)
    if view is None:
        return HTMLResponse("View not found", status_code=404)

    semantic_models = ctx.semantic_for_view(name)

    # Build definition display
    definition_parts = []
    if view.sql:
        definition_parts.append(view.sql)
    else:
        definition_parts.append(f"Source: {view.source or 'sql'}")
        if view.uri:
            definition_parts.append(f"URI: {view.uri}")
        if view.database:
            definition_parts.append(f"Database: {view.database}")
        if view.table:
            definition_parts.append(f"Table: {view.table}")

    # Create semantic models section
    semantic_content = []
    if semantic_models:
        for sm in semantic_models:
            semantic_content.append(
                card(
                    f"Semantic Model: {sm.name}",
                    f"""
                        <p>Description: {sm.description or 'No description'}</p>
                        <p>Dimensions: {', '.join(d.name for d in sm.dimensions) or 'None'}</p>
                        <p>Measures: {', '.join(m.name for m in sm.measures) or 'None'}</p>
                    """
                )
            )
    else:
        semantic_content.append(
            base.alert("No semantic-layer metadata available for this view.", "info")
        )

    breadcrumb_items = [
        ("Dashboard", "/"),
        ("Views", "/views"),
        (name, f"/views/{name}")
    ]

    content = [
        navigation.breadcrumb(breadcrumb_items),
        navigation.header(f"View Details: {name}", "View definition and semantic metadata"),

        _grid_with_children(
            style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin: 2rem 0;",
            children=[
                str(card(
                    "View Definition",
                    f'<pre style="background-color: #f5f5f5; padding: 1rem; border-radius: 4px; overflow-x: auto;">{"\\n".join(definition_parts)}</pre>'
                )),
                _div_with_children(children=[str(item) for item in semantic_content])
            ]
        ),

        navigation.back_button("/views", "← Back to Views"),
        navigation.footer(),
    ]

    page_html = page(f"View: {name}", content)
    return HTMLResponse(str(page_html))


def query_page(result: QueryResult | None = None, sql_text: str = "") -> HTMLResponse:
    """Modern query interface with enhanced result display."""
    breadcrumb_items = [("Dashboard", "/"), ("Query", "/query")]

    # Build results section
    results_content = []
    if result:
        if result.error:
            results_content.append(base.alert(f"Query Error: {result.error}", "error"))
        else:
            results_table = tables.query_results_table(result.columns, result.rows, result.truncated)
            results_content.append(results_table)
    else:
        results_content.append(base.alert("Run a query to see results here.", "info"))

    content = [
        navigation.breadcrumb(breadcrumb_items),
        navigation.header("Ad-hoc SQL Query", "Execute queries against your DuckDB catalog"),

        _div_with_children(style="margin: 2rem 0;", children=[reactive_query_editor()]),

        _div_with_children(style="margin: 2rem 0;", children=[str(item) for item in results_content]),

        navigation.back_button("/", "← Back to Dashboard"),
        navigation.footer(),
    ]

    page_html = page("SQL Query", content)
    return HTMLResponse(str(page_html))


def build_status_fragment(status) -> str:
    """Legacy function for build status (kept for compatibility)."""
    if status is None:
        return "No builds have been run yet."
    if status.success:
        return f"Last build succeeded in {status.duration_seconds or 0:.2f}s"
    return f"Last build failed: {status.message or 'unknown error'}"