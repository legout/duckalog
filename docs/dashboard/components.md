# UI Component Usage Guide

## Overview

This guide demonstrates how to use and create UI components in the Duckalog dashboard using htpy and Datastar.

## Table of Contents

- [Layout Components](#layout-components)
- [Data Display](#data-display)
- [Forms](#forms)
- [Navigation](#navigation)
- [Feedback](#feedback)
- [Creating Custom Components](#creating-custom-components)

## Layout Components

### Base Layout

The foundation for all dashboard pages:

```python
from duckalog.dashboard.components import base_layout

def my_page():
    content = div[
        h1["My Page"],
        p["Content goes here"]
    ]

    return base_layout("Page Title", content)
```

### Page Header

Add titles and subtitles to pages:

```python
from duckalog.dashboard.components import page_header

def my_page():
    content = [
        page_header(
            "Dashboard",
            subtitle="Welcome to your dashboard",
            action=button["New Item"]
        ),
        div[...content...]
    ]

    return base_layout("Dashboard", content)
```

### Card Container

Organize content into cards:

```python
from duckalog.dashboard.components import card

def views_page():
    content = [
        card("Views", views_div),
        card("Statistics", stats_div),
        card("Recent Activity", activity_div)
    ]

    return base_layout("Views", content)
```

## Data Display

### Table Component

Display tabular data:

```python
from duckalog.dashboard.components import table_component

def views_table(views):
    headers = ["Name", "Schema", "Type", "Description"]

    rows = [
        [
            view["name"],
            view["schema"],
            view["source_type"],
            view.get("description", "")
        ]
        for view in views
    ]

    return table_component(headers, rows)
```

### Custom Table with htpy

For more control:

```python
def custom_table(headers, rows):
    return div(class_="overflow-x-auto")[
        table(class_="table min-w-full divide-y divide-gray-200")[
            thead(class_="bg-gray-50 dark:bg-gray-800")[
                tr[
                    th(class_="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider")[
                        header
                    ]
                    for header in headers
                ]
            ],
            tbody(class_="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700")[
                tr[
                    td(class_="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100")[
                        cell
                    ]
                    for cell in row
                ]
                for row in rows
            ]
        ]
    ]
```

### Responsive Table

Tables with horizontal scroll on mobile:

```python
def responsive_table(headers, rows):
    return div(class_="overflow-x-auto shadow ring-1 ring-black ring-opacity-5 md:rounded-lg")[
        table(class_="min-w-full divide-y divide-gray-300 dark:divide-gray-700")[
            # ... table content
        ]
    ]
```

## Forms

### Text Input

```python
from htpy import input, label, div

def text_input_field(label_text, bind_to, placeholder=""):
    return div(class_="space-y-1")[
        label(for_=bind_to, class_="block text-sm font-medium")[
            label_text
        ],
        input(
            id=bind_to,
            type="text",
            class_="input w-full",
            placeholder=placeholder,
            **{
                "data-bind": bind_to
            }
        )
    ]
```

### Textarea

```python
from htpy import textarea

def sql_input():
    return textarea(
        id="sql-input",
        rows="6",
        class_="mt-1 block w-full rounded-md border-gray-300 shadow-sm",
        placeholder="SELECT * FROM table",
        **{
            "data-bind": "sql"
        }
    )
```

### Select Dropdown

```python
def select_field(options, bind_to):
    return select(class_="select w-full", **{
        "data-bind": bind_to
    })[
        option(value="", disabled=True, selected=True)[
            "Select an option"
        ],
        *[
            option(value=opt["value"])[opt["label"]]
            for opt in options
        ]
    ]
```

### Checkbox

```python
def checkbox_field(label_text, bind_to):
    return div(class_="flex items-center")[
        input(
            type="checkbox",
            class_="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded",
            **{
                "data-bind": bind_to,
                "data-checked": f"${bind_to}"
            }
        ),
        label(class_="ml-2 block text-sm")[
            label_text
        ]
    ]
```

### Form with Validation

```python
def query_form():
    return form(class_="space-y-4")[
        div[
            label(for_="sql", class_="block text-sm font-medium")[
                "SQL Query"
            ],
            textarea(
                id="sql",
                rows="6",
                class_="mt-1 block w-full rounded-md border-gray-300",
                **{
                    "data-bind": "sql",
                    "data-validate": "required"
                }
            )
        ],
        div(
            id="error",
            class_="text-sm text-red-600",
            **{"data-show": "$error"}
        )[f"{$error}"],
        button(
            type="submit",
            class_="btn btn-primary",
            **{
                "data-on-click": "$$post('/query/execute')",
                "data-indicator": "loading"
            }
        )[
            "Execute Query"
        ],
        span(**{"data-show": "$loading"})["Running..."]
    ]
```

## Navigation

### Navigation Links

```python
from duckalog.dashboard.components import nav_link

def navigation():
    return nav(class_="flex space-x-4")[
        nav_link("/", "Home"),
        nav_link("/views", "Views"),
        nav_link("/query", "Query")
    ]
```

### Breadcrumbs

```python
def breadcrumbs(items):
    return nav(class_="flex", aria_label="Breadcrumb")[
        ol(class_="flex items-center space-x-2")[
            li(class_="flex items-center")[
                a(href="/", class_="text-gray-500 hover:text-gray-700")[
                    "Home"
                ]
            ],
            *[
                li(class_="flex items-center")[
                    span(class_="mx-2 text-gray-400")["/"],
                    a(
                        href=item["href"],
                        class_="text-gray-500 hover:text-gray-700"
                    )[item["label"]]
                ]
                for item in items
            ]
        ]
    ]
```

### Tabs

```python
def tab_interface(tabs, active_tab):
    return div(class_="border-b border-gray-200 dark:border-gray-700")[
        nav(class_="-mb-px flex space-x-8")[
            *[
                a(
                    href=tab["href"],
                    class_=f"py-2 px-1 border-b-2 font-medium text-sm {
                        'border-indigo-500 text-indigo-600' if tab['id'] == active_tab
                        else 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }"
                )[tab["label"]]
                for tab in tabs
            ]
        ]
    ]
```

## Feedback

### Alert Messages

```python
def alert(message, type_="info"):
    """Display alert messages.

    Args:
        message: Alert text
        type_: info, success, warning, error
    """
    type_classes = {
        "info": "bg-blue-50 border-blue-200 text-blue-800",
        "success": "bg-green-50 border-green-200 text-green-800",
        "warning": "bg-yellow-50 border-yellow-200 text-yellow-800",
        "error": "bg-red-50 border-red-200 text-red-800"
    }

    return div(
        class_=f"rounded-md border p-4 {type_classes.get(type_, type_classes['info'])}",
        **{
            "data-show": f"$showAlert && $alertType === '{type_}'"
        }
    )[
        div(class_="flex")[
            div(class_="ml-3")[
                p(class_="text-sm font-medium")[f"{$alertMessage}"]
            ]
        ]
    ]
```

### Loading Spinner

```python
def spinner(size="md"):
    """Show loading spinner.

    Args:
        size: sm, md, lg
    """
    size_classes = {
        "sm": "h-4 w-4",
        "md": "h-8 w-8",
        "lg": "h-12 w-12"
    }

    return div(
        class_="flex justify-center",
        **{
            "data-show": "$loading"
        }
    )[
        div(class_="animate-spin rounded-full border-b-2 border-indigo-600 " +
            size_classes.get(size, size_classes["md"]))
    ]
```

### Progress Bar

```python
def progress_bar(value, max_value=100):
    """Show progress bar.

    Args:
        value: Current value
        max_value: Maximum value
    """
    percentage = min(100, (value / max_value) * 100)

    return div(class_="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700")[
        div(
            class_="bg-blue-600 h-2.5 rounded-full transition-all duration-300",
            style=f"width: {percentage}%"
        )
    ]
```

### Status Badge

```python
def status_badge(status):
    """Show status badge.

    Args:
        status: Status text
    """
    status_classes = {
        "complete": "bg-green-100 text-green-800",
        "building": "bg-blue-100 text-blue-800",
        "error": "bg-red-100 text-red-800",
        "idle": "bg-gray-100 text-gray-800"
    }

    return span(
        class_="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium " +
               status_classes.get(status.lower(), status_classes["idle"])
    )[status]
```

## Creating Custom Components

### Component Structure

```python
from htpy import div, Element
from typing import Any

def custom_component(
    title: str,
    content: Element | list[Element] | str,
    *,
    action: Element | None = None,
    **kwargs: Any
) -> Element:
    """Custom card component with action button.

    Args:
        title: Card title
        content: Card content
        action: Optional action button
        **kwargs: Additional HTML attributes

    Returns:
        HTPy element
    """
    return div(class_="bg-white shadow rounded-lg p-6", **kwargs)[
        div(class_="flex items-center justify-between mb-4")[
            h3(class_="text-lg font-medium")[title],
            action
        ],
        div(content)
    ]
```

### Using Custom Component

```python
def my_page():
    action_btn = button(
        class_="btn btn-primary",
        **{
            "data-on-click": "$$post('/api/create')"
        }
    )["Create Item"]

    content = div[
        p["This is the card content"]
    ]

    card = custom_component(
        "My Card",
        content,
        action=action_btn
    )

    return base_layout("Custom Component", card)
```

### Composable Components

Build complex UIs from simple components:

```python
def data_table_with_search(headers, rows):
    """Table with built-in search."""
    search_input = input(
        type="text",
        placeholder="Search...",
        class_="input w-full mb-4",
        **{
            "data-bind": "search",
            "data-debounce": "300"
        }
    )

    table = custom_table(headers, rows)

    return div[
        search_input,
        table
    ]
```

### Component with Datastar

```python
def reactive_counter():
    """Counter with reactive updates."""
    return div(class_="text-center")[
        button(
            class_="btn btn-ghost btn-icon",
            **{
                "data-on-click": "decrement()"
            }
        )["-"],
        span(
            class_="mx-4 text-2xl font-bold",
            **{"data-text": "$count"}
        )["0"],
        button(
            class_="btn btn-ghost btn-icon",
            **{
                "data-on-click": "increment()"
            }
        )["+"]
    ]

# Add to base_layout signals
signals = {
    "count": 0
}
```

## Styling Best Practices

### Use Tailwind Classes

```python
# Good - semantic Tailwind classes
div(class_="flex items-center justify-between p-4 bg-white rounded-lg shadow")

# Bad - custom classes
div(class_="my-custom-div another-class")
```

### Responsive Design

```python
# Good - responsive classes
div(class_="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4")

# Bad - non-responsive
div(class_="grid grid-cols-3 gap-4")
```

### Dark Mode Support

```python
# Good - dark mode classes
div(class_="bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100")

# Bad - no dark mode
div(class_="bg-white text-gray-900")
```

### Consistent Spacing

```python
# Use consistent spacing scale
div(class_="space-y-4")  # 1rem gap
div(class_="space-y-6")  # 1.5rem gap
div(class_="space-y-8")  # 2rem gap
```

## Accessibility

### ARIA Labels

```python
# Good - has accessible name
button(
    aria_label="Close dialog",
    class_="btn btn-ghost"
)[...]

# Bad - no accessible name
button(class_="btn btn-ghost")[...]
```

### Semantic HTML

```python
# Good - semantic elements
header[...]
nav[...]
main[...]
section[...]
article[...]
footer[...]

# Bad - generic divs
div[...]
div[...]
div[...]
```

### Focus Management

```python
# Open modal and focus first input
def open_modal():
    modal = document.getElementById('modal')
    first_input = modal.querySelector('input')
    if first_input:
        first_input.focus()
```

## Component Testing

### Unit Testing Components

```python
import pytest
from htpy import render
from duckalog.dashboard.components.layout import card

def test_card_renders_title():
    result = card("Test Title", "Test Content")
    html = render(result)
    assert "Test Title" in html
    assert "Test Content" in html
```

### Integration Testing

```python
from litestar.testing import TestClient

def test_query_form(client: TestClient):
    response = client.get("/query")
    assert response.status_code == 200
    assert 'data-bind="sql"' in response.text
    assert 'data-on-click="$$post' in response.text
```

## Performance Tips

### Minimize DOM Updates

```python
# Good - batch updates
yield SSE.patch_elements(
    render_full_table(data),
    selector="#table",
    mode="morph"
)

# Bad - many small updates
for item in data:
    yield SSE.patch_elements(
        f"<tr>...</tr>",
        selector="#table",
        mode="append"
    )
```

### Use Keys for Lists

```python
# When rendering lists, ensure stable keys
div[
    tr(key=item["id"])[...]  # if supported
    for item in items
]
```

### Lazy Load Components

```python
# Load heavy components on demand
div(**{
    "data-show": "$showHeavyComponent"
})[
    heavy_component()
]
```

## Common Patterns

### Search with Results

```python
def search_with_results():
    return div(class_="space-y-4")[
        # Search input
        input(
            placeholder="Search...",
            class_="input w-full",
            **{
                "data-bind": "search",
                "data-debounce": "300"
            }
        ),

        # Results
        div(id="search-results")[
            # Results will be patched via Datastar
        ]
    ]
```

### Modal Dialog

```python
def modal_dialog(title, content, footer):
    return div(
        id="modal",
        class_="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full hidden",
        **{
            "data-show": "$showModal"
        }
    )[
        div(class_="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white")[
            # Header
            div(class_="flex items-center justify-between mb-4")[
                h3(class_="text-xl font-bold")[title],
                button(
                    class_="text-gray-400 hover:text-gray-600",
                    **{
                        "data-on-click": "closeModal()"
                    }
                )["×"]
            ],

            # Content
            div(class_="mb-4")[content],

            # Footer
            div(class_="flex justify-end space-x-2")[footer]
        ]
    ]
```

### Pagination

```python
def pagination(current_page, total_pages):
    return nav(class_="flex items-center justify-between")[
        div(class_="flex-1 flex justify-between sm:hidden")[
            button(
                class_="btn",
                **{
                    "data-show": f"$currentPage > 1",
                    "data-on-click": f"goToPage({current_page - 1})"
                }
            )["Previous"],
            button(
                class_="btn",
                **{
                    "data-show": f"$currentPage < {total_pages}",
                    "data-on-click": f"goToPage({current_page + 1})"
                }
            )["Next"]
        ],
        div(class_="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between")[
            div[
                p(class_="text-sm text-gray-700")[
                    f"Showing page {current_page} of {total_pages}"
                ]
            ],
            div(className="hidden md:-mt-px md:flex")[
                # Page numbers
                *[
                    a(
                        href="#",
                        class_=f"px-4 py-2 border text-sm font-medium {'bg-indigo-50 border-indigo-500 text-indigo-600' if i == current_page else 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'}",
                        **{
                            "data-on-click": f"goToPage({i})"
                        }
                    )[str(i)]
                    for i in range(1, total_pages + 1)
                ]
            ]
        ]
    ]
```

## References

- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [htpy Documentation](https://htpy.dev/)
- [Datastar Documentation](https://github.com/ubio/datastar)
