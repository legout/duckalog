"""Base dashboard components using HTPY and modern CSS patterns."""

from __future__ import annotations

import htpy as h


def page(title: str, children: list) -> str:
    """Base page template with modern layout."""
    content = "".join(str(child) for child in children)
    return f"""
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>{title}</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
            <link rel="stylesheet" href="/static/styles.css">
            <script type="module" src="/static/datastar.js"></script>
        </head>
        <body>
            <nav class="container-fluid">
                <ul>
                    <li><strong>Duckalog</strong></li>
                </ul>
                <ul>
                    <li><a href="/">Dashboard</a></li>
                    <li><a href="/views">Views</a></li>
                    <li><a href="/query">Query</a></li>
                </ul>
            </nav>
            <main class="container">
                {content}
            </main>
        </body>
    </html>
    """


def card(title: str, content, actions: list = None) -> h.Element:
    """Create a modern card component."""
    if actions:
        actions_html = "".join(str(action) for action in actions)
        return f"""
            <article>
                <header>
                    <h3>{title}</h3>
                    <div>{actions_html}</div>
                </header>
                <div>{content}</div>
            </article>
        """
    else:
        return f"""
            <article>
                <header>
                    <h3>{title}</h3>
                </header>
                <div>{content}</div>
            </article>
        """


def alert(message: str, level: str = "info") -> str:
    """Create an alert message with proper styling."""
    role_map = {
        "info": "status",
        "success": "status",
        "warning": "alert",
        "error": "alert"
    }

    role = role_map.get(level, "status")
    return f"""
        <div role="{role}">
            <article>
                <header>
                    <p>{message}</p>
                </header>
            </article>
        </div>
    """


def loading_spinner(text: str = "Loading...") -> h.Element:
    """Create a loading indicator."""
    return h.div(
        h.article(
            h.header(h.p(children=text)),
        )
    )


def breadcrumb(items: list[tuple[str, str]]) -> h.Element:
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
            crumbs.append(h.li(children=label))
        else:
            crumbs.append(h.li(h.a(href=url, children=label)))

    return h.nav(
        h.ul(crumbs)
    )


def button(
    text: str,
    onclick: str = None,
    primary: bool = False,
    disabled: bool = False,
    **kwargs
) -> h.Element:
    """Create a modern button component."""
    attrs = {
        "type": kwargs.get("type", "button"),
        "disabled": disabled,
    }

    if primary:
        attrs["class"] = "primary"

    attrs.update({k: v for k, v in kwargs.items() if k != "type"})

    return h.button(attrs, children=text)


def form_input(
    name: str,
    label: str,
    placeholder: str = "",
    value: str = "",
    input_type: str = "text",
    required: bool = False
) -> h.Element:
    """Create a form input with label."""
    return h.div(
        h.label(html_for=name, children=label),
        h.input(
            type=input_type,
            id=name,
            name=name,
            placeholder=placeholder,
            value=value,
            required=required
        ),
    )


def form_textarea(
    name: str,
    label: str,
    placeholder: str = "",
    value: str = "",
    rows: int = 4,
    required: bool = False
) -> h.Element:
    """Create a form textarea with label."""
    return h.div(
        h.label(html_for=name, children=label),
        h.textarea(
            id=name,
            name=name,
            placeholder=placeholder,
            rows=rows,
            required=required,
            children=value
        ),
    )