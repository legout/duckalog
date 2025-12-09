"""Layout components for the dashboard using htpy."""

from __future__ import annotations

from typing import Any

from htpy import (
    Element,
    a,
    body,
    button,
    div,
    footer,
    h1,
    h2,
    head,
    header,
    html,
    link,
    meta,
    nav,
    p,
    script,
    span,
    svg,
    table,
    tbody,
    td,
    th,
    thead,
    title,
    tr,
)
from markupsafe import Markup


def base_layout(
    page_title: str,
    content: Element | list[Element] | str,
    *,
    datastar_js_path: str = "https://cdn.jsdelivr.net/gh/starfederation/datastar@v1.0.0-RC.6/bundles/datastar.js",
) -> Element:
    """Create the base HTML layout for all pages.

    Args:
        page_title: Title for the page
        content: Main content to render
        datastar_js_path: Path to datastar.js file (default: CDN URL for temporary delivery)

    Returns:
        Complete HTML document
    """
    return html(lang="en")[
        head[
            meta(charset="UTF-8"),
            meta(name="viewport", content="width=device-width, initial-scale=1.0"),
            title[f"{page_title} - Duckalog"],
            # Tailwind CSS via CDN (temporary measure)
            script(src="https://cdn.tailwindcss.com"),
            # Basecoat CSS via CDN (temporary measure)
            link(
                href="https://cdn.jsdelivr.net/npm/basecoat-css@latest/dist/basecoat.cdn.min.css",
                rel="stylesheet",
            ),
            # Datastar JS via CDN (temporary measure - pending bundling)
            script(type="module", src=datastar_js_path),
            # Build status initialization script
            script(type="module")[
                Markup(
                    """
                    // Initialize build status SSE when page loads
                    if (typeof window !== 'undefined') {
                        // Connect to build status SSE
                        const buildStatusElement = document.getElementById('build-status');
                        if (buildStatusElement) {
                            // Create EventSource for build status
                            const eventSource = new EventSource('/build/status');

                            eventSource.onmessage = (event) => {
                                try {
                                    const data = JSON.parse(event.data);
                                    // Update build status indicator color
                                    const indicator = document.getElementById('build-status-indicator');
                                    const progressBar = document.getElementById('build-progress-bar');

                                    if (indicator) {
                                        if (data.status === 'building') {
                                            indicator.className = 'w-3 h-3 rounded-full bg-blue-500 animate-pulse';
                                        } else if (data.status === 'complete') {
                                            indicator.className = 'w-3 h-3 rounded-full bg-green-500';
                                        } else if (data.status === 'error') {
                                            indicator.className = 'w-3 h-3 rounded-full bg-red-500';
                                        } else {
                                            indicator.className = 'w-3 h-3 rounded-full bg-gray-300';
                                        }
                                    }

                                    if (progressBar && data.progress !== undefined) {
                                        progressBar.style.width = data.progress + '%';
                                    }
                                } catch (e) {
                                    console.error('Error parsing build status:', e);
                                }
                            };

                            eventSource.onerror = (error) => {
                                console.error('SSE error:', error);
                            };
                        }

                        // Initialize theme toggle
                        const themeToggle = document.getElementById('theme-toggle');
                        if (themeToggle) {
                            // Get saved theme from localStorage or default to 'light'
                            const savedTheme = localStorage.getItem('theme') || 'light';
                            document.documentElement.classList.toggle('dark', savedTheme === 'dark');

                            // Toggle theme on click
                            const toggleTheme = () => {
                                const isDark = document.documentElement.classList.contains('dark');
                                const newTheme = isDark ? 'light' : 'dark';

                                // Update class on html element
                                document.documentElement.classList.toggle('dark', newTheme === 'dark');

                                // Save to localStorage
                                localStorage.setItem('theme', newTheme);
                            };

                            themeToggle.addEventListener('click', toggleTheme);
                            // Support keyboard navigation (Enter and Space)
                            themeToggle.addEventListener('keydown', (e) => {
                                if (e.key === 'Enter' || e.key === ' ') {
                                    e.preventDefault();
                                    toggleTheme();
                                }
                            });
                        }

                        // Initialize mobile navigation toggle
                        const mobileMenuButton = document.getElementById('mobile-menu-button');
                        const mobileMenu = document.getElementById('mobile-menu');

                        if (mobileMenuButton && mobileMenu) {
                            let isMenuOpen = false;

                            // Toggle menu on click
                            const toggleMenu = () => {
                                isMenuOpen = !isMenuOpen;
                                if (isMenuOpen) {
                                    mobileMenu.classList.remove('hidden');
                                    mobileMenuButton.setAttribute('aria-expanded', 'true');
                                    // Focus first link when menu opens
                                    const firstLink = mobileMenu.querySelector('a');
                                    if (firstLink) {
                                        setTimeout(() => firstLink.focus(), 100);
                                    }
                                } else {
                                    mobileMenu.classList.add('hidden');
                                    mobileMenuButton.setAttribute('aria-expanded', 'false');
                                }
                            };

                            mobileMenuButton.addEventListener('click', toggleMenu);
                            // Support keyboard navigation (Enter and Space)
                            mobileMenuButton.addEventListener('keydown', (e) => {
                                if (e.key === 'Enter' || e.key === ' ') {
                                    e.preventDefault();
                                    toggleMenu();
                                }
                            });

                            // Close menu when clicking on a link
                            const mobileLinks = mobileMenu.querySelectorAll('a');
                            mobileLinks.forEach(link => {
                                link.addEventListener('click', () => {
                                    isMenuOpen = false;
                                    mobileMenu.classList.add('hidden');
                                    mobileMenuButton.setAttribute('aria-expanded', 'false');
                                });
                            });
                        }

                        // Initialize view search filtering
                        const viewsContainer = document.getElementById('views-container');
                        if (viewsContainer) {
                            const viewsDataElement = document.getElementById('views-data');
                            const views = viewsDataElement
                                ? JSON.parse(viewsDataElement.getAttribute('data-views') || '[]')
                                : [];

                            // Create search input handler
                            const searchInput = document.querySelector('input[data-bind="search"]');
                            if (searchInput) {
                                let searchTimeout;
                                searchInput.addEventListener('input', (e) => {
                                    clearTimeout(searchTimeout);
                                    searchTimeout = setTimeout(() => {
                                        filterViews(e.target.value);
                                    }, 300);
                                });
                            }

                            function filterViews(query) {
                                query = query.toLowerCase().trim();
                                if (!query) {
                                    renderViews(views);
                                    return;
                                }

                                const filtered = views.filter(view => {
                                    return view.name.toLowerCase().includes(query) ||
                                           view.schema.toLowerCase().includes(query) ||
                                           (view.description && view.description.toLowerCase().includes(query)) ||
                                           view.source_type.toLowerCase().includes(query);
                                });

                                renderViews(filtered);
                            }

                            function renderViews(viewList) {
                                if (!viewList.length) {
                                    viewsContainer.innerHTML = '<p class="text-gray-500 text-center py-8">No views found</p>';
                                    return;
                                }

                                let html = '<div class="overflow-x-auto"><table class="table min-w-full divide-y divide-gray-200 dark:divide-gray-700"><thead class="bg-gray-50 dark:bg-gray-800"><tr>';
                                html += '<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Name</th>';
                                html += '<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Schema</th>';
                                html += '<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Source Type</th>';
                                html += '<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Description</th>';
                                html += '</tr></thead><tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">';

                                viewList.forEach(view => {
                                    html += '<tr>';
                                    html += `<td class="px-6 py-4 whitespace-nowrap text-sm"><a href="/views/${view.name}" class="text-indigo-600 hover:text-indigo-900 dark:text-indigo-400">${view.name}</a></td>`;
                                    html += `<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">${view.schema}</td>`;
                                    html += `<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100"><span class="badge badge-outline text-xs">${view.source_type}</span></td>`;
                                    html += `<td class="px-6 py-4 text-sm text-gray-900 dark:text-gray-100">${view.description ? view.description.substring(0, 50) + (view.description.length > 50 ? '...' : '') : ''}</td>`;
                                    html += '</tr>';
                                });

                                html += '</tbody></table></div>';
                                viewsContainer.innerHTML = html;
                            }

                            // Initial render
                            renderViews(views);
                        }
                    }
                    """
                )
            ],
        ],
        body(class_="min-h-screen bg-gray-50 dark:bg-gray-900")[
            # Navigation header
            header(class_="bg-white dark:bg-gray-800 shadow-sm")[
                nav(class_="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8")[
                    div(class_="flex justify-between h-16")[
                        div(class_="flex")[
                            div(class_="flex-shrink-0 flex items-center")[
                                span(class_="text-xl font-bold text-indigo-600")[
                                    "Duckalog"
                                ]
                            ],
                            # Desktop navigation
                            div(class_="hidden sm:ml-6 sm:flex sm:space-x-8")[
                                nav_link("/", "Home"),
                                nav_link("/views", "Views"),
                                nav_link("/query", "Query"),
                            ],
                        ],
                        # Right side: theme toggle + mobile menu button
                        div(class_="flex items-center gap-2")[
                            # Theme toggle button
                            button(
                                id="theme-toggle",
                                type="button",
                                class_="btn btn-ghost btn-icon",
                                **{
                                    "aria-label": "Toggle theme",
                                    "title": "Toggle dark/light mode",
                                },
                            )[
                                # Sun icon (for dark mode)
                                svg(
                                    id="sun-icon",
                                    xmlns="http://www.w3.org/2000/svg",
                                    width="24",
                                    height="24",
                                    viewBox="0 0 24 24",
                                    fill="none",
                                    stroke="currentColor",
                                    stroke_width="2",
                                    stroke_linecap="round",
                                    stroke_linejoin="round",
                                    class_="h-5 w-5 block dark:hidden",
                                )[
                                    circle(cx="12", cy="12", r="5"),
                                    svg_line(x1="12", y1="1", x2="12", y2="3"),
                                    svg_line(x1="12", y1="21", x2="12", y2="23"),
                                    svg_line(x1="4.22", y1="4.22", x2="5.64", y2="5.64"),
                                    svg_line(x1="18.36", y1="18.36", x2="19.78", y2="19.78"),
                                    svg_line(x1="1", y1="12", x2="3", y2="12"),
                                    svg_line(x1="21", y1="12", x2="23", y2="12"),
                                    svg_line(x1="4.22", y1="19.78", x2="5.64", y2="18.36"),
                                    svg_line(x1="18.36", y1="5.64", x2="19.78", y2="4.22"),
                                ],
                                # Moon icon (for light mode)
                                svg(
                                    id="moon-icon",
                                    xmlns="http://www.w3.org/2000/svg",
                                    width="24",
                                    height="24",
                                    viewBox="0 0 24 24",
                                    fill="none",
                                    stroke="currentColor",
                                    stroke_width="2",
                                    stroke_linecap="round",
                                    stroke_linejoin="round",
                                    class_="h-5 w-5 hidden dark:block",
                                )[
                                    path(d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"),
                                ]
                            ],
                            # Mobile menu button
                            div(class_="sm:hidden")[
                                button(
                                    id="mobile-menu-button",
                                    type="button",
                                    class_="btn btn-ghost btn-icon",
                                    **{
                                        "aria-expanded": "false",
                                        "aria-controls": "mobile-menu",
                                        "aria-label": "Open main menu",
                                    },
                                )[
                                    # Hamburger icon
                                    svg(
                                        xmlns="http://www.w3.org/2000/svg",
                                        width="24",
                                        height="24",
                                        viewBox="0 0 24 24",
                                        fill="none",
                                        stroke="currentColor",
                                        stroke_width="2",
                                        stroke_linecap="round",
                                        stroke_linejoin="round",
                                        class_="h-6 w-6",
                                    )[
                                        # Three horizontal lines (hamburger)
                                        svg_line(x1="3", y1="6", x2="21", y2="6"),
                                        svg_line(x1="3", y1="12", x2="21", y2="12"),
                                        svg_line(x1="3", y1="18", x2="21", y2="18"),
                                    ]
                                ]
                            ],
                        ],
                    ],
                    # Mobile menu (hidden by default)
                    div(
                        id="mobile-menu",
                        class_="hidden sm:hidden pb-3 pt-2 space-y-1",
                    )[
                        nav_link("/", "Home", mobile=True),
                        nav_link("/views", "Views", mobile=True),
                        nav_link("/query", "Query", mobile=True),
                    ],
                ],
            ],
            # Main content
            div(class_="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8")[content],
            # Footer
            footer(class_="bg-white dark:bg-gray-800 mt-auto")[
                div(class_="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8")[
                    p(class_="text-center text-sm text-gray-500")[
                        "Duckalog Dashboard - DuckDB Catalog Inspector"
                    ]
                ]
            ],
        ],
    ]


def svg_line(x1: str, y1: str, x2: str, y2: str) -> Element:
    """Create an SVG line element."""
    from htpy import svg as svg_element
    return svg_element(x1=x1, y1=y1, x2=x2, y2=y2)


def circle(cx: str, cy: str, r: str) -> Element:
    """Create an SVG circle element."""
    from htpy import svg as svg_element
    return svg_element(cx=cx, cy=cy, r=r)


def path(d: str) -> Element:
    """Create an SVG path element."""
    from htpy import svg as svg_element
    return svg_element(d=d)


def nav_link(href: str, label: str, *, active: bool = False, mobile: bool = False) -> Element:
    """Create a navigation link.

    Args:
        href: Link URL
        label: Link text
        active: Whether this is the active page
        mobile: Whether this is for mobile navigation

    Returns:
        Navigation link element
    """
    if mobile:
        # Mobile navigation styling
        base_class = "block px-3 py-2 rounded-md text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
        if active:
            active_class = f"{base_class} bg-indigo-50 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-200"
        else:
            active_class = base_class
    else:
        # Desktop navigation styling
        base_class = "inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
        if active:
            active_class = (
                f"{base_class} border-indigo-500 text-gray-900 dark:text-white"
            )
        else:
            active_class = (
                f"{base_class} border-transparent text-gray-500 hover:border-gray-300 "
                "hover:text-gray-700 dark:text-gray-300 dark:hover:text-white"
            )
    return a(href=href, class_=active_class)[label]


def page_header(
    title_text: str,
    *,
    subtitle: str | None = None,
    action: Element | None = None,
) -> Element:
    """Create a page header with optional subtitle and action button.

    Args:
        title_text: Main heading text
        subtitle: Optional subtitle
        action: Optional action element (e.g., button)

    Returns:
        Page header element
    """
    return div(class_="md:flex md:items-center md:justify-between mb-6")[
        div(class_="min-w-0 flex-1")[
            h1(class_="text-2xl font-bold leading-7 text-gray-900 dark:text-white sm:truncate sm:text-3xl sm:tracking-tight")[
                title_text
            ],
            (
                p(class_="mt-1 text-sm text-gray-500 dark:text-gray-400")[subtitle]
                if subtitle
                else ""
            ),
        ],
        (
            div(class_="mt-4 flex md:ml-4 md:mt-0")[action]
            if action
            else ""
        ),
    ]


def card(
    title_text: str | None = None,
    content: Element | list[Element] | str = "",
    *,
    footer_content: Element | str | None = None,
) -> Element:
    """Create a card component.

    Args:
        title_text: Optional card title
        content: Card content
        footer_content: Optional footer content

    Returns:
        Card element
    """
    return div(class_="card bg-white dark:bg-gray-800 shadow rounded-lg")[
        (
            header(class_="px-4 py-5 sm:px-6 border-b border-gray-200 dark:border-gray-700")[
                h2(class_="text-lg font-medium text-gray-900 dark:text-white")[
                    title_text
                ]
            ]
            if title_text
            else ""
        ),
        div(class_="px-4 py-5 sm:p-6")[content],
        (
            footer(class_="px-4 py-4 sm:px-6 bg-gray-50 dark:bg-gray-700 rounded-b-lg")[
                footer_content
            ]
            if footer_content
            else ""
        ),
    ]


def table_component(
    columns: list[str],
    rows: list[tuple[Any, ...]],
    *,
    id: str | None = None,
) -> Element:
    """Create a table component.

    Args:
        columns: Column headers
        rows: Table rows (list of tuples)
        id: Optional element ID

    Returns:
        Table element
    """
    attrs: dict[str, Any] = {"class_": "min-w-full divide-y divide-gray-200 dark:divide-gray-700"}
    if id:
        attrs["id"] = id

    return div(class_="overflow-x-auto")[
        table(**attrs)[
            thead(class_="bg-gray-50 dark:bg-gray-800")[
                tr[
                    (
                        th(
                            scope="col",
                            class_="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider",
                        )[col]
                        for col in columns
                    )
                ]
            ],
            tbody(class_="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700")[
                (
                    tr[
                        (
                            td(class_="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100")[
                                str(cell) if cell is not None else ""
                            ]
                            for cell in row
                        )
                    ]
                    for row in rows
                )
            ],
        ]
    ]
