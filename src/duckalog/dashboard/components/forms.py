"""Form components for the dashboard."""

from __future__ import annotations

from typing import Any


def search_form(
    placeholder: str = "Search...",
    datastar_signal: str | None = None,
    action: str = "",
    method: str = "GET",
) -> str:
    """Generate a search form with optional Datastar integration."""
    input_attrs = f'data-bind="{datastar_signal}"' if datastar_signal else ""

    return f"""
    <form action="{action}" method="{method}" class="mb-6">
        <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
                </svg>
            </div>
            <input
                type="text"
                placeholder="{placeholder}"
                class="block w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                {input_attrs}
            />
        </div>
    </form>
    """


def query_form(
    initial_sql: str = "",
    datastar_signal: str | None = None,
    action: str = "/query",
    method: str = "POST",
) -> str:
    """Generate a query form with SQL textarea and Datastar integration."""
    textarea_attrs = f'data-bind="{datastar_signal}"' if datastar_signal else ""

    return f"""
    <form action="{action}" method="{method}" class="space-y-4" data-on-submit="$$post('{action}')">
        <div>
            <label for="sql" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                SQL Query
            </label>
            <textarea
                id="sql"
                name="sql"
                rows="8"
                class="block w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
                placeholder="Enter SQL query..."
                {textarea_attrs}
                data-signals="query_sql"
            >{initial_sql}</textarea>
        </div>
        <div class="flex items-center space-x-4">
            <button
                type="submit"
                class="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800"
                data-indicator="query-loading"
                data-on-click="$$.post('/query/stream')"
            >
                Run Query
            </button>
            <button
                type="button"
                onclick="document.getElementById('sql').value = ''"
                class="px-6 py-2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 font-medium rounded-lg transition-colors"
            >
                Clear
            </button>
        </div>
        <div id="query-loading" data-show="$query_running" class="hidden">
            <div class="flex items-center space-x-2 text-blue-600 dark:text-blue-400">
                <svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span class="text-sm">Executing query...</span>
            </div>
        </div>
    </form>
    """


def build_form(action: str = "/build", method: str = "POST") -> str:
    """Generate a form for triggering catalog builds with Datastar integration."""
    return f"""
    <form action="{action}" method="{method}" data-on-submit="$$post('/build/stream')">
        <button
            type="submit"
            class="w-full sm:w-auto px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800"
            data-indicator="build-loading"
        >
            <svg class="inline w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
            </svg>
            Build Catalog
        </button>
        <div id="build-loading" data-show="$build_running" class="hidden mt-4">
            <div class="flex items-center space-x-2 text-green-600 dark:text-green-400">
                <svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span class="text-sm">Building catalog...</span>
            </div>
        </div>
        <div id="build-success" data-show="$build_success" class="hidden mt-4">
            <div class="flex items-center space-x-2 text-green-600 dark:text-green-400">
                <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                <span class="text-sm" data-text="$build_summary">Catalog built successfully!</span>
            </div>
        </div>
        <div id="build-error" data-show="$build_error" class="hidden mt-4">
            <div class="flex items-center space-x-2 text-red-600 dark:text-red-400">
                <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                <span class="text-sm" data-text="$build_error">Build failed!</span>
            </div>
        </div>
    </form>
    """


def button(
    text: str,
    button_type: str = "button",
    variant: str = "primary",
    href: str | None = None,
    onclick: str | None = None,
    disabled: bool = False,
    datastar_attrs: dict[str, str] | None = None,
) -> str:
    """Generate a button with various styles."""
    variants = {
        "primary": "bg-blue-600 hover:bg-blue-700 text-white",
        "secondary": "bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200",
        "success": "bg-green-600 hover:bg-green-700 text-white",
        "danger": "bg-red-600 hover:bg-red-700 text-white",
        "warning": "bg-yellow-600 hover:bg-yellow-700 text-white",
    }

    base_classes = "px-4 py-2 font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 dark:focus:ring-offset-gray-800 disabled:opacity-50 disabled:cursor-not-allowed"
    variant_classes = variants.get(variant, variants["primary"])

    attrs = ""
    if datastar_attrs:
        for key, value in datastar_attrs.items():
            attrs += f' data-{key}="{value}"'

    if disabled:
        attrs += " disabled"

    if onclick:
        attrs += f' onclick="{onclick}"'

    button_html = f'<button type="{button_type}" class="{base_classes} {variant_classes}"{attrs}>{text}</button>'

    if href:
        return f'<a href="{href}" class="inline-block">{button_html}</a>'

    return button_html


def link_button(text: str, href: str, variant: str = "secondary") -> str:
    """Generate a link styled as a button."""
    return button(text, button_type="button", variant=variant, href=href)
