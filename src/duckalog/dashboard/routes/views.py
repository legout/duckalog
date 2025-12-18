"""Views listing and detail route handlers."""

from __future__ import annotations

import json

from litestar import Controller, get
from litestar.response import Response
from litestar.exceptions import NotFoundException

from ..components import base_layout, page_header, card
from ..state import DashboardContext
from htpy import a, code, div, input, p, pre, span


class ViewsController(Controller):
    """Views listing and detail controller."""

    path = "/views"

    @get()
    async def list_views(self, ctx: DashboardContext) -> Response[str]:
        """Render the views listing page."""
        views = ctx.get_views()

        # Convert views to table format
        columns = ["Name", "Schema", "Source Type", "Description"]
        rows = [
            (
                a(
                    href=f"/views/{v['name']}",
                    class_="text-indigo-600 hover:text-indigo-900 dark:text-indigo-400",
                )[v["name"]],
                v["schema"],
                span(class_="badge badge-outline text-xs")[v["source_type"]],
                v["description"][:50] + "..." if len(v["description"]) > 50 else v["description"],
            )
            for v in views
        ]

        content = [
            page_header(
                "Views",
                subtitle=f"{len(views)} views in catalog",
            ),
            # Search card
            card(
                "Search Views",
                div(**{"data-signals": '{"search": "", "filtered": []}'})[
                    div(class_="space-y-4")[
                        div[
                            input(
                                type="text",
                                placeholder="Search views by name, schema, or description...",
                                class_="input w-full",
                                **{
                                    "data-bind": "search",
                                    "aria-label": "Search views",
                                },
                            ),
                        ],
                    ],
                ],
            ),
        ]

        # Add views table card
        if views:
            views_div = div(id="views-container")
            # Store views data for JavaScript
            content.extend([
                div(
                    id="views-data",
                    data_views=json.dumps(views),
                    style="display: none;",
                ),
                card("Views", views_div),
            ])
        else:
            content.append(card("Views", p(class_="text-gray-500")["No views defined."]))

        # Wrap in container
        content = div(class_="space-y-6")[content]

        html = str(base_layout("Views", content))
        return Response(content=html, media_type="text/html")

    @get("/{view_name:str}")
    async def view_detail(
        self, view_name: str, ctx: DashboardContext
    ) -> Response[str]:
        """Render a view detail page."""
        view = ctx.get_view(view_name)
        if not view:
            raise NotFoundException(f"View '{view_name}' not found")

        # Build content sections
        sections = [
            page_header(
                view["name"],
                subtitle=view["description"] or "No description",
            ),
        ]

        # Info card
        info_content = div(class_="grid grid-cols-2 gap-4")[
            div[
                p(class_="text-sm font-medium text-gray-500")["Schema"],
                p(class_="mt-1 text-sm text-gray-900 dark:text-white")[
                    view["schema"]
                ],
            ],
            div[
                p(class_="text-sm font-medium text-gray-500")["Source Type"],
                p(class_="mt-1")[
                    span(class_="badge badge-outline")[
                        view["source"] if view["source"] else "sql"
                    ]
                ],
            ],
        ]
        sections.append(card("View Information", info_content))

        # SQL card if available
        if view["sql"]:
            sql_content = pre(
                class_="bg-gray-100 dark:bg-gray-900 p-4 rounded-md overflow-x-auto"
            )[code(class_="text-sm text-gray-800 dark:text-gray-200")[view["sql"]]]
            sections.append(card("SQL Definition", sql_content))

        # Columns card if available (removed since ViewConfig doesn't store columns)

        content = div(class_="space-y-6")[sections]
        html = str(base_layout(f"View: {view_name}", content))
        return Response(content=html, media_type="text/html")
