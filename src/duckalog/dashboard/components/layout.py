"""Layout components for the dashboard."""

from __future__ import annotations

from typing import Any


def html_document(title: str, body_content: str, datastar_signals: dict[str, Any] | None = None) -> str:
    """Generate a complete HTML document with Datastar integration."""
    # Base HTML structure with Tailwind CSS
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            darkMode: 'class',
            theme: {{
                extend: {{
                    colors: {{
                        primary: {{
                            50: '#eff6ff',
                            100: '#dbeafe',
                            500: '#3b82f6',
                            600: '#2563eb',
                            700: '#1d4ed8',
                        }}
                    }}
                }}
            }}
        }}
    </script>
    <script src="/static/datastar.js"></script>
</head>
<body class="bg-gray-50 dark:bg-gray-900 min-h-screen">
    {body_content}
    <script>
        // Theme toggle
        function toggleTheme() {{
            document.documentElement.classList.toggle('dark');
            localStorage.setItem('theme', document.documentElement.classList.contains('dark') ? 'dark' : 'light');
        }}

        // Initialize theme
        if (localStorage.getItem('theme') === 'dark' || (!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches)) {{
            document.documentElement.classList.add('dark');
        }}
    </script>
</body>
</html>"""
    return html


def page_header(title: str, subtitle: str | None = None) -> str:
    """Generate a page header with title and optional subtitle."""
    subtitle_html = f'<p class="text-sm text-gray-600 dark:text-gray-400 mt-1">{subtitle}</p>' if subtitle else ''
    return f"""
    <header class="bg-white dark:bg-gray-800 shadow">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div class="flex items-center justify-between">
                <div>
                    <h1 class="text-3xl font-bold text-gray-900 dark:text-white">{title}</h1>
                    {subtitle_html}
                </div>
                <button
                    onclick="toggleTheme()"
                    class="p-2 rounded-lg bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                    aria-label="Toggle theme"
                >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/>
                    </svg>
                </button>
            </div>
        </div>
    </header>
    """


def navigation(active_path: str = "/") -> str:
    """Generate navigation bar."""
    nav_items = [
        ("/", "Home"),
        ("/views", "Views"),
        ("/query", "Query"),
    ]

    nav_links = ""
    for path, label in nav_items:
        is_active = "bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300" if path == active_path else "text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
        nav_links += f"""
        <a href="{path}" class="px-4 py-2 rounded-lg {is_active} transition-colors">
            {label}
        </a>
        """

    return f"""
    <nav class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex space-x-4 py-4">
                {nav_links}
            </div>
        </div>
    </nav>
    """


def page_container(content: str) -> str:
    """Wrap content in a page container."""
    return f"""
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {content}
    </div>
    """


def card(content: str, class_name: str = "") -> str:
    """Generate a card component."""
    return f"""
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 {class_name}">
        {content}
    </div>
    """


def alert(message: str, alert_type: str = "info") -> str:
    """Generate an alert component."""
    type_styles = {
        "info": "bg-blue-50 dark:bg-blue-900 text-blue-800 dark:text-blue-200 border-blue-200 dark:border-blue-700",
        "success": "bg-green-50 dark:bg-green-900 text-green-800 dark:text-green-200 border-green-200 dark:border-green-700",
        "warning": "bg-yellow-50 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 border-yellow-200 dark:border-yellow-700",
        "error": "bg-red-50 dark:bg-red-900 text-red-800 dark:text-red-200 border-red-200 dark:border-red-700",
    }

    style = type_styles.get(alert_type, type_styles["info"])

    return f"""
    <div class="border rounded-lg p-4 {style}">
        {message}
    </div>
    """


def loading_indicator(message: str = "Loading...") -> str:
    """Generate a loading indicator."""
    return f"""
    <div class="flex items-center justify-center p-8">
        <svg class="animate-spin h-8 w-8 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span class="ml-2 text-gray-700 dark:text-gray-300">{message}</span>
    </div>
    """
