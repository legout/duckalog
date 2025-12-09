# Datastar Integration Patterns

## Overview

This document describes common patterns for using Datastar in the Duckalog dashboard, including server-side implementation and client-side usage.

## Table of Contents

- [Server-Sent Events (SSE)](#server-sent-events-sse)
- [Signal-Based State](#signal-based-state)
- [Reactive DOM Updates](#reactive-dom-updates)
- [Form Handling](#form-handling)
- [Event Handling](#event-handling)
- [Error Handling](#error-handling)

## Server-Sent Events (SSE)

### Basic SSE Endpoint

```python
from litestar import get
from datastar_py.litestar import datastar_response
from datastar_py import ServerSentEventGenerator as SSE
from typing import AsyncGenerator

@get("/api/stream")
@datastar_response
async def stream_endpoint() -> AsyncGenerator:
    """Stream data via SSE."""
    # Send initial data
    yield SSE.patch_signals({"status": "connected", "count": 0})

    # Stream updates
    for i in range(10):
        await asyncio.sleep(1)
        yield SSE.patch_signals({"count": i})

    # Signal completion
    yield SSE.patch_signals({"status": "complete"})
```

### SSE with Query Execution

```python
@post("/query/execute")
@datastar_response
async def execute_query(request: Request, ctx: DashboardContext) -> AsyncGenerator:
    """Execute query and stream results."""
    signals = await read_signals(request)
    sql = signals.get("sql", "").strip()

    if not sql:
        yield SSE.patch_signals({"error": "No query provided", "loading": False})
        return

    # Set loading state
    yield SSE.patch_signals({"error": "", "loading": True})

    try:
        # Execute query
        columns, rows = ctx.execute_query(sql)

        # Stream results
        if columns:
            yield SSE.patch_elements(
                build_table_html(columns, rows),
                selector="#query-results",
                mode="morph"
            )

        yield SSE.patch_signals({"loading": False, "rowCount": len(rows)})

    except Exception as e:
        yield SSE.patch_signals({"error": str(e), "loading": False})
```

### SSE with Build Status

```python
@get("/build/status")
@datastar_response
async def build_status() -> AsyncGenerator:
    """Stream build status updates."""
    global _build_status

    # Send initial status
    yield SSE.patch_signals(_build_status)

    # Send heartbeat every 30 seconds
    heartbeat_interval = 30
    heartbeat_count = 0

    try:
        while True:
            await asyncio.sleep(heartbeat_interval)
            heartbeat_count += 1
            yield SSE.patch_signals({"heartbeat": heartbeat_count})
    except asyncio.CancelledError:
        # Client disconnected
        pass
```

## Signal-Based State

### Defining Signals

Signals are JavaScript objects stored in the browser:

```javascript
// Example signal structure
const signals = {
  // Form state
  sql: "",
  loading: false,
  error: "",

  // Data
  results: [],
  rowCount: 0,

  // UI state
  search: "",
  theme: "light",

  // Metadata
  lastUpdated: null
};
```

### Initializing Signals in HTML

```python
from htpy import div

# Static signals (constant values)
div(**{"data-signals": '{"theme": "light", "version": "1.0"}'})[...]

# Or with Python dict
signals = {
    "theme": "light",
    "search": "",
    "filtered": []
}
div(**{"data-signals": json.dumps(signals)})[...]
```

### Reading Signals in Handler

```python
from datastar_py.litestar import read_signals

@post("/api/action")
@datastar_response
async def handle_action(request: Request) -> AsyncGenerator:
    """Handle action with signal data."""
    signals = await read_signals(request)

    sql = signals.get("sql", "")
    search = signals.get("search", "")

    # Process based on signals
    result = process_data(sql, search)

    # Update signals
    yield SSE.patch_signals({
        "results": result,
        "lastUpdated": datetime.utcnow().isoformat()
    })
```

## Reactive DOM Updates

### Patch Signals (Update State)

```python
# Update single signal
yield SSE.patch_signals({"loading": True})

# Update multiple signals
yield SSE.patch_signals({
    "loading": False,
    "error": "",
    "results": data
})
```

### Patch Elements (Update DOM)

```python
# Replace element content
html = '<div id="results"><p>New content</p></div>'
yield SSE.patch_elements(
    html,
    selector="#results",
    mode="morph"  # Options: append, prepend, replace, morph
)

# Update specific element
yield SSE.patch_elements(
    '<span class="badge">5 results</span>',
    selector="#result-count",
    mode="replace"
)
```

### Element Mode Options

- **append** - Add to end of element
- **prepend** - Add to beginning
- **replace** - Replace entire element
- **morph** - Merge new content (default)

## Form Handling

### HTML Form with Datastar Binding

```python
from htpy import form, input, textarea, button

def query_form():
    return form[
        textarea(
            id="sql-input",
            **{"data-bind": "sql", "rows": 6}
        )[...],
        button(
            type="button",
            **{
                "data-on-click": "$$post('/query/execute')",
                "data-indicator": "loading"
            }
        )["Execute Query"],
        span(**{"data-show": "$loading"})["Running..."]
    ]
```

### Form Validation

```python
@post("/query/execute")
@datastar_response
async def execute_query(request: Request, ctx: DashboardContext) -> AsyncGenerator:
    signals = await read_signals(request)
    sql = signals.get("sql", "").strip()

    # Validate
    if not sql:
        yield SSE.patch_signals({"error": "Please enter a SQL query"})
        return

    if len(sql) > 10000:
        yield SSE.patch_signals({"error": "Query too long (max 10000 chars)"})
        return

    # Proceed with execution
    yield SSE.patch_signals({"error": "", "loading": True})
    # ... execution code
```

### Debounced Input

Client-side debouncing for search:

```python
# HTML with debounce attribute (if supported)
input(
    **{"data-bind": "search", "data-debounce": "300"}
)
```

Or manual debouncing in JavaScript:

```javascript
const searchInput = document.querySelector('input[data-bind="search"]');
if (searchInput) {
    let timeout;
    searchInput.addEventListener('input', (e) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            filterViews(e.target.value);
        }, 300);
    });
}
```

## Event Handling

### Click Events

```python
# Basic click
button(**{"data-on-click": "alert('Clicked!')"})["Click Me"]

# POST request
button(**{"data-on-click": "$$post('/api/action')"})["Submit"]

# With data
button(**{
    "data-on-click": "$$post('/api/action', {id: 123})"
})["Delete Item"]

# With custom data
button(**{
    "data-on-click": "$$post('/api/action', {custom: 'data'})"
})["Custom"]
```

### Input Events

```python
# Bind to signal
input(**{"data-bind": "search"})

# With debounce
input(**{"data-bind": "search", "data-debounce": "500"})

# Custom handler
input(**{
    "data-bind": "query",
    "data-on-input": "handleInput($event)"
})
```

### Custom Event Handlers

In JavaScript:

```javascript
// Define handler function
function handleInput(event) {
    const value = event.target.value;
    // Process input
    console.log('Input:', value);
}
```

## Error Handling

### Server-Side Error Handling

```python
@post("/query/execute")
@datastar_response
async def execute_query(request: Request, ctx: DashboardContext) -> AsyncGenerator:
    signals = await read_signals(request)

    try:
        # Try execution
        columns, rows = ctx.execute_query(signals.get("sql", ""))

        # Success - update UI
        yield SSE.patch_signals({
            "error": "",
            "loading": False,
            "rowCount": len(rows)
        })

        # Update results
        yield SSE.patch_elements(
            render_results(columns, rows),
            selector="#results",
            mode="morph"
        )

    except EngineError as e:
        # Database error
        yield SSE.patch_signals({
            "error": f"Database error: {str(e)}",
            "loading": False
        })

    except Exception as e:
        # Unexpected error
        yield SSE.patch_signals({
            "error": f"Unexpected error: {str(e)}",
            "loading": False
        })
```

### Client-Side Error Handling

```python
# Display error in HTML
div(id="error-display", **{"data-show": "$error"})[
    span(class_="text-red-600")[f"{$error}"]
]
```

Or with custom error display:

```python
div(id="error-display")[
    span(**{"data-text": "$error"})[...]
]
```

### Error Recovery

```python
# Clear error on new action
@post("/query/execute")
@datastar_response
async def execute_query(request: Request) -> AsyncGenerator:
    # Clear previous error
    yield SSE.patch_signals({"error": ""})

    try:
        # Attempt operation
        result = await risky_operation()
        yield SSE.patch_signals({"result": result})
    except Exception as e:
        yield SSE.patch_signals({"error": str(e)})
```

## Best Practices

### 1. Signal Naming

```javascript
// Good - descriptive names
{
  "isLoading": false,
  "errorMessage": "",
  "searchQuery": "",
  "filteredResults": []
}

// Bad - unclear names
{
  "l": false,
  "e": "",
  "q": "",
  "r": []
}
```

### 2. Signal Structure

```javascript
// Good - organized by feature
{
  "query": {
    "sql": "",
    "loading": false,
    "results": [],
    "error": ""
  },
  "search": {
    "term": "",
    "filters": [],
    "active": false
  }
}
```

### 3. Error Messages

```python
# Good - specific error
yield SSE.patch_signals({"error": "Query failed: table 'users' does not exist"})

# Bad - generic error
yield SSE.patch_signals({"error": "Error occurred"})
```

### 4. Loading States

```python
# Set loading at start
yield SSE.patch_signals({"loading": True})

# Clear at end
yield SSE.patch_signals({"loading": False})
```

### 5. Optimistic Updates

```python
# Update UI immediately
yield SSE.patch_signals({"items": newItems, "saving": True})

# Then persist to server
try:
    await save_to_database(newItems)
    yield SSE.patch_signals({"saving": False, "saved": True})
except Exception as e:
    yield SSE.patch_signals({
        "saving": False,
        "error": "Failed to save",
        "items": originalItems  # Rollback
    })
```

## Common Patterns

### Search with Filtering

```python
# Python - Filter data
def filter_views(views, search_term):
    if not search_term:
        return views

    term = search_term.lower()
    return [
        v for v in views
        if term in v["name"].lower()
        or term in v.get("description", "").lower()
    ]

# Python - Stream results
@post("/views/filter")
@datastar_response
async def filter_views(request: Request):
    signals = await read_signals(request)
    search = signals.get("search", "")

    views = get_all_views()
    filtered = filter_views(views, search)

    yield SSE.patch_signals({"filtered": filtered})
    yield SSE.patch_elements(
        render_view_table(filtered),
        selector="#views-table",
        mode="morph"
    )

# HTML
input(**{"data-bind": "search", "data-debounce": "300"})
div(id="views-table")
```

### Real-Time Status Updates

```python
# Python - Update status
async def update_build_status(status_data):
    global _build_status
    _build_status.update(status_data)

# Python - Stream status
@get("/build/status")
@datastar_response
async def build_status():
    yield SSE.patch_signals(_build_status)

    while True:
        await asyncio.sleep(5)
        yield SSE.patch_signals(_build_status)

# HTML - Display status
div(id="build-status")[
    span(**{"data-text": "$status"})[...],
    progress(**{"data-text": "$progress"})[...]
]
```

## Debugging

### Console Logging

```python
# Add logging to handlers
import logging

logger = logging.getLogger(__name__)

@post("/query/execute")
@datastar_response
async def execute_query(request: Request):
    signals = await read_signals(request)
    logger.info(f"Received signals: {signals}")

    # ... handler code
```

### Browser DevTools

- Open DevTools → Network → WS/SSE tab
- View SSE stream in real-time
- Inspect signal updates
- Check for errors

### Signal Inspector

```javascript
// Add to page for debugging
window.dumpSignals = () => {
    const signals = document.querySelector('[data-signals]');
    if (signals) {
        console.log('Signals:', JSON.parse(signals.getAttribute('data-signals')));
    }
};

// Call in console: dumpSignals()
```

## Performance Tips

### 1. Minimize Signal Updates

```python
# Good - batch updates
yield SSE.patch_signals({
    "loading": True,
    "results": [],
    "error": ""
})

# Bad - multiple separate updates
yield SSE.patch_signals({"loading": True})
yield SSE.patch_signals({"results": []})
yield SSE.patch_signals({"error": ""})
```

### 2. Use Element Patches for Large HTML

```python
# Good - single patch for table
yield SSE.patch_elements(
    render_large_table(columns, rows),
    selector="#results",
    mode="morph"
)

# Bad - many small patches
for i, row in enumerate(rows):
    yield SSE.patch_elements(
        f"<tr>...</tr>",
        selector=f"#row-{i}",
        mode="append"
    )
```

### 3. Debounce User Input

```python
# Add debounce to search
input(**{"data-bind": "search", "data-debounce": "300"})
```

## References

- [Datastar Documentation](https://github.com/ubio/datastar)
- [Datastar-Python SDK](https://github.com/datastar-py/datastar-py)
- [Litestar Documentation](https://litestar.dev/)
