"""Form components for the dashboard."""

from __future__ import annotations

import htpy as h


def query_form(sql_text: str = "", action: str = "/query", method: str = "POST") -> str:
    """Create a form for SQL queries."""
    return f"""
        <form action="{action}" method="{method}">
            <fieldset>
                <legend>SQL Query</legend>
                <textarea
                    name="sql"
                    placeholder="Enter your SQL query here..."
                    rows="10"
                    style="font-family: monospace; font-size: 0.9em;"
                >{sql_text}</textarea>
                <div style="margin-top: 1rem;">
                    <button type="submit" style="margin-right: 0.5rem;">
                        Execute Query
                    </button>
                    <button
                        type="reset"
                        style="background-color: var(--muted-color);"
                    >
                        Clear
                    </button>
                </div>
            </fieldset>
        </form>
    """


def build_form(action: str = "/build", method: str = "POST") -> h.Element:
    """Create a form for triggering catalog builds."""
    return h.form(action=action, method=method)(
        h.button(type="submit")(
            "🔄 Build Catalog"
        ),
    )


def view_search_form(query: str = "", action: str = "/views", method: str = "GET") -> str:
    """Create a form for searching views."""
    return f"""
        <form action="{action}" method="{method}">
            <fieldset>
                <legend>Search Views</legend>
                <div>
                    <input
                        type="search"
                        name="q"
                        placeholder="Search view names..."
                        value="{query}"
                    >
                    <button type="submit" style="margin-left: 0.5rem;">Search</button>
                </div>
            </fieldset>
        </form>
    """


def export_form(format_options: list[str], action: str = "/export", method: str = "POST") -> h.Element:
    """Create a form for data export."""
    return h.form(action=action, method=method)(
        h.fieldset(
            h.legend("Export Data"),
            h.div(
                h.label(for_="export_format")("Export Format:"),
                h.select(id="export_format", name="format")(
                    h.option(value=fmt, selected=(fmt == "csv"))(
                        fmt.upper()
                    ) for fmt in format_options
                ),
            ),
            h.div(style="margin-top: 1rem;")(
                h.button(type="submit")(
                    "📥 Export"
                ),
            ),
        ),
    )


def config_form(config_data: dict, action: str = "/config", method: str = "POST") -> h.Element:
    """Create a form for configuration settings."""
    return h.form(action=action, method=method)(
        h.fieldset(
            h.legend("Configuration Settings"),
            h.div(
                h.label(for_="row_limit")("Query Row Limit:"),
                h.input(
                    type="number",
                    id="row_limit",
                    name="row_limit",
                    value=str(config_data.get("row_limit", 500)),
                    min="1",
                    max="10000",
                ),
            ),
            h.div(style="margin-top: 1rem;")(
                h.button(type="submit")(
                    "Save Settings"
                ),
            ),
        ),
    )


def filter_form(filters: dict, action: str = "", method: str = "GET") -> h.Element:
    """Create a form with multiple filter options."""
    return h.form(action=action, method=method)(
        h.fieldset(
            h.legend("Filters"),
            *[h.div(
                h.label(for_=f"filter_{key}")(key.replace("_", " ").title()),
                h.select(id=f"filter_{key}", name=key)(
                    h.option(value="", selected=(not value))("All"),
                    *[h.option(value=option, selected=(option == value))(option)
                      for option in options]
                ),
            ) for key, (value, options) in filters.items()],
            h.div(style="margin-top: 1rem;")(
                h.button(type="submit")("Apply Filters"),
                h.button(
                    type="reset",
                    style="background-color: var(--muted-color); margin-left: 0.5rem;"
                )("Clear"),
            ),
        ),
    )