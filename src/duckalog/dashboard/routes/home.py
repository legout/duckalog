"""Home page route handler."""

from __future__ import annotations

import json

from litestar import Controller, get
from litestar.response import Response

from ..components import base_layout, page_header, card
from ..state import DashboardContext
from htpy import button, div, p, span


class HomeController(Controller):
    """Home page controller."""

    path = "/"

    @get()
    async def index(self, ctx: DashboardContext) -> Response[str]:
        """Render the home page with catalog overview."""
        stats = ctx.get_catalog_stats()
        views = ctx.get_views()

        content = div(class_="space-y-6")[
            page_header(
                "Dashboard",
                subtitle=f"Catalog: {ctx.config_path}",
                action=button(
                    type="button",
                    class_="btn btn-primary",
                    **{
                        "data-on-click": "$$post('/build')",
                        "data-signal": "buildTrigger",
                    },
                )["Build Catalog"],
            ),
            # Build Status Card
            card(
                "Build Status",
                div(
                    id="build-status",
                    class_="space-y-3",
                    **{
                        "data-signals": json.dumps(
                            {
                                "status": "idle",
                                "progress": 0,
                                "message": "No build in progress",
                                "timestamp": None,
                                "error": None,
                            }
                        )
                    },
                )[
                    div(class_="flex items-center gap-3")[
                        div(
                            id="build-status-indicator",
                            class_="w-3 h-3 rounded-full bg-gray-300",
                        ),
                        span(
                            id="build-status-text",
                            class_="text-sm font-medium",
                            **{"data-text": "$message"},
                        )["No build in progress"],
                    ],
                    div(
                        class_="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700",
                        id="build-progress-container",
                        **{"data-show": "$status"},
                    )[
                        div(
                            class_="bg-blue-600 h-2.5 rounded-full transition-all duration-300",
                            style="width: 0%",
                            id="build-progress-bar",
                            **{"data-style": "width: $progress + '%'"},
                        )
                    ],
                    div(
                        id="build-error",
                        class_="mt-2 p-3 bg-red-50 dark:bg-red-900 rounded-md hidden",
                        **{"data-show": "$error"},
                    )[
                        p(
                            class_="text-sm text-red-700 dark:text-red-200",
                            **{"data-text": "$error"},
                        )
                    ],
                ],
            ),
            # Stats cards
            div(class_="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3")[
                card(
                    "Total Views",
                    div(class_="text-3xl font-bold text-indigo-600")[
                        str(stats["total_views"])
                    ],
                ),
                card(
                    "Schemas",
                    div(class_="text-3xl font-bold text-indigo-600")[
                        str(stats["schemas"])
                    ],
                ),
                card(
                    "Database",
                    div(class_="text-sm text-gray-600 dark:text-gray-300")[
                        ctx.db_path or "In-memory"
                    ],
                ),
            ],
            # Recent views
            card(
                "Views",
                div(class_="space-y-2")[
                    (
                        div(class_="flex items-center justify-between p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded")[
                            div[
                                span(class_="font-medium text-gray-900 dark:text-white")[
                                    view["name"]
                                ],
                                span(class_="ml-2 text-sm text-gray-500")[
                                    f"({view['schema']})"
                                ],
                            ],
                            span(class_="badge badge-outline text-xs")[
                                view["source_type"]
                            ],
                        ]
                        for view in views[:10]
                    )
                ]
                if views
                else p(class_="text-gray-500")["No views defined in this catalog."],
            ),
        ]

        html = str(base_layout("Home", content))
        return Response(content=html, media_type="text/html")
