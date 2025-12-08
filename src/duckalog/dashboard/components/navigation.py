"""Navigation components for the dashboard."""

from __future__ import annotations

import htpy as h


def sidebar(active_section: str = "") -> h.Element:
    """Create a sidebar navigation with current section highlighting."""
    nav_items = [
        ("Dashboard", "/", "home"),
        ("Views", "/views", "list"),
        ("Query", "/query", "search"),
    ]

    return h.nav(
        h.ul(
            *[h.li(
                h.a(
                    href=url,
                    style="font-weight: bold;" if active_section == key else ""
                )(
                    h.span(style="margin-right: 0.5rem;")(icon),
                    label
                )
            ) for label, url, key in nav_items]
        )
    )


def header(title: str, subtitle: str = "") -> str:
    """Create a page header with title and optional subtitle."""
    subtitle_html = f"<p>{subtitle}</p>" if subtitle else ""
    return f"""
        <header>
            <h1>{title}</h1>
            {subtitle_html}
            <hr style="margin: 1rem 0;">
        </header>
    """


def footer() -> str:
    """Create a footer with links and information."""
    return """
        <footer style="margin-top: 2rem; padding-top: 1rem; border-top: 1px solid var(--muted-color);">
            <p style="color: var(--muted-color); font-size: 0.875em;">
                Duckalog Dashboard - Modern DuckDB Catalog Explorer
            </p>
            <p style="font-size: 0.875em;">
                <a href="https://github.com/legout/duckalog" target="_blank">GitHub Repository</a>
                •
                <a href="https://legout.github.io/duckalog/" target="_blank">Documentation</a>
            </p>
        </footer>
    """


def tab_navigation(tabs: list[tuple[str, str, str]], active_tab: str) -> h.Element:
    """Create tab navigation for different views or sections.

    Args:
        tabs: List of (label, url, key) tuples
        active_tab: Key of the currently active tab
    """
    return h.nav(
        h.ul(
            *[h.li(
                h.a(
                    href=url,
                    style="font-weight: bold;" if key == active_tab else ""
                )(label)
            ) for label, url, key in tabs]
        )
    )


def action_bar(actions: list) -> str:
    """Create an action bar with buttons and controls."""
    actions_html = "".join(str(action) for action in actions)
    return f"""
        <div style="margin-bottom: 1rem; padding: 1rem; background-color: var(--muted-background-color); border-radius: 4px;">
            {actions_html}
        </div>
    """


def quick_links(links: list[tuple[str, str]]) -> str:
    """Create a list of quick navigation links.

    Args:
        links: List of (label, url) tuples
    """
    link_html = "".join(
        f'<li style="margin-bottom: 0.5rem;"><a href="{url}" style="text-decoration: none;">→ {label}</a></li>'
        for label, url in links
    )
    return f"""
        <nav>
            <ul style="list-style-type: none; padding: 0;">
                {link_html}
            </ul>
        </nav>
    """


def back_button(url: str, text: str = "← Back") -> str:
    """Create a back navigation button."""
    return f"""
        <a href="{url}" style="text-decoration: none; margin-bottom: 1rem; display: inline-block;">
            <button type="button" style="background-color: var(--muted-color);">
                {text}
            </button>
        </a>
    """


def breadcrumb(items: list[tuple[str, str]]) -> str:
    """Create breadcrumb navigation.

    Args:
        items: List of (label, url) tuples. Last item should have empty URL for current page.
    """
    if not items:
        return ""

    crumbs = []
    for i, (label, url) in enumerate(items):
        is_last = i == len(items) - 1
        if is_last:
            crumbs.append(f'<li>{label}</li>')
        else:
            crumbs.append(f'<li><a href="{url}">{label}</a></li>')

    crumbs_html = "".join(crumbs)
    return f'<nav><ul>{crumbs_html}</ul></nav>'


def view_navigation(current_view: str = "") -> h.Element:
    """Create navigation specifically for view-related pages."""
    view_actions = [
        ("View List", "/views", "list"),
        ("SQL Query", "/query", "search"),
        ("Build Catalog", "/build", "refresh"),
    ]

    return h.div(style="margin-bottom: 1rem;")(
        h.h3("View Navigation"),
        h.ul(
            *[h.li(style="display: inline-block; margin-right: 1rem;")(
                h.a(href=url)(
                    h.span(style="margin-right: 0.5rem;")(icon),
                    label
                )
            ) for label, url, icon in view_actions]
        ),
    )


def semantic_model_navigation(models: list[tuple[str, str]]) -> h.Element:
    """Create navigation for semantic models.

    Args:
        models: List of (model_name, model_url) tuples
    """
    if not models:
        return h.p("No semantic models found.")

    return h.nav(
        h.h4("Semantic Models"),
        h.ul(
            *[h.li(
                h.a(href=url)(model_name)
            ) for model_name, url in models]
        )
    )