# Datastar Integration Guide

This guide explains how Datastar is integrated into the Duckalog dashboard for real-time, reactive user experiences.

## Overview

The Duckalog dashboard uses **Datastar.js** for client-side reactivity combined with custom **Server-Sent Events (SSE)** endpoints for real-time communication.

## Architecture

```
┌─────────────────┐    HTTP Request    ┌─────────────────┐    SSE Events    ┌─────────────────┐
│   Browser UI    │ ──────────────────► │  Litestar App  │ ──────────────────► │   Datastar.js    │
│                 │                    │                 │                    │                 │
│ - HTML/CSS/JS   │ ◄────────────────── │                 │ ◄────────────────── │ - Signal Mgmt   │
│ - Datastar.js   │    HTML Response    │ - Route Handlers│    Datastar Events│ - DOM Updates   │
│ - Tailwind CSS  │                    │ - SSE Endpoints │                    │ - Event Stream  │
└─────────────────┘                    └─────────────────┘                    └─────────────────┘
```

## Client-Side Integration

### HTML Attributes

The dashboard uses Datastar's declarative attributes for reactive behavior:

```html
<!-- Signal binding for form inputs -->
<textarea data-bind="query_sql" data-signals="query_sql">SELECT * FROM users</textarea>

<!-- Reactive form submission -->
<form data-on-submit="$$post('/query/stream')">
  <button data-on-click="$$.post('/query/stream')">Run Query</button>
</form>

<!-- Conditional display based on signals -->
<div id="loading" data-show="$query_running" class="hidden">
  <div class="loading-spinner">Executing query...</div>
</div>

<div id="success" data-show="$query_success" class="hidden">
  <div class="success-message" data-text="$query_summary">Query completed!</div>
</div>

<div id="error" data-show="$query_error" class="hidden">
  <div class="error-message" data-text="$query_error">Query failed!</div>
</div>
```

### Signal Management

Datastar uses signals to manage application state:

```javascript
// Signals are automatically created by datastar attributes
// $query_running - boolean for query execution status
// $query_error - string for error messages
// $query_results - object for query result data
// $query_complete - boolean for completion status
```

## Server-Side Implementation

### SSE Endpoint Structure

The dashboard implements Server-Sent Events endpoints that emit Datastar-compatible events:

```python
async def execute_query_stream(ctx: DashboardContext, sql: str) -> Response:
    """Execute a SQL query and stream results via Server-Sent Events."""

    async def event_stream():
        events = []

        try:
            # 1. Start event - signal query is running
            events.append("event: datastar-patch-signals\n")
            events.append(f"data: {json.dumps({\n")
            events.append(f"  'signals': {{\n")
            events.append(f"    'query_running': True,\n")
            events.append(f"    'query_error': None,\n")
            events.append(f"    'query_results': None\n")
            events.append(f"  }}\n")
            events.append(f"}})}\n\n")

            # 2. Execute the actual query
            result = ctx.run_query(sql)

            # 3. Results event - signal completion with data
            if result.error:
                events.append("event: datastar-patch-signals\n")
                events.append(f"data: {json.dumps({\n")
                events.append(f"  'signals': {{\n")
                events.append(f"    'query_running': False,\n")
                events.append(f"    'query_error': '{result.error}',\n")
                events.append(f"    'query_results': None\n")
                events.append(f"  }}\n")
                events.append(f"}})}\n\n")
            else:
                results_data = {
                    'columns': result.columns,
                    'rows': [[str(cell) for cell in row] for row in result.rows],
                    'truncated': result.truncated,
                    'row_count': len(result.rows)
                }

                events.append("event: datastar-patch-signals\n")
                events.append(f"data: {json.dumps({\n")
                events.append(f"  'signals': {{\n")
                events.append(f"    'query_running': False,\n")
                events.append(f"    'query_error': None,\n")
                events.append(f"    'query_results': {json.dumps(results_data)}\n")
                events.append(f"  }}\n")
                events.append(f"}})}\n\n")

            # 4. Completion event
            events.append("event: datastar-patch-signals\n")
            events.append(f"data: {json.dumps({\n")
            events.append(f"  'signals': {{\n")
            events.append(f"    'query_complete': True\n")
            events.append(f"  }}\n")
            events.append(f"}})}\n\n")

        except Exception as exc:
            # Error event
            events.append("event: datastar-patch-signals\n")
            events.append(f"data: {json.dumps({\n")
            events.append(f"  'signals': {{\n")
            events.append(f"    'query_running': False,\n")
            events.append(f"    'query_error': '{str(exc)}',\n")
            events.append(f"    'query_results': None\n")
            events.append(f"  }}\n")
            events.append(f"}})}\n\n")

        return "".join(events)

    content = await event_stream()

    return Response(
        content=content,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control",
        }
    )
```

### Event Format

Datastar expects SSE events in this format:

```
event: datastar-patch-signals
data: {"signals": {"signal_name": "signal_value"}}

event: datastar-patch-elements
data: {"selector": "#element-id", "mode": "outer", "elements": "<div>Updated content</div>"}
```

## Real-time Features

### Query Execution Flow

1. **User Input**: User enters SQL in form with `data-bind="query_sql"`
2. **Form Submission**: Form with `data-on-submit="$$post('/query/stream')"`
3. **Loading State**: `data-show="$query_running"` displays loading indicator
4. **Streaming Results**: SSE events update `data-text="$query_results"`
5. **Error Handling**: Error signals show/hide error messages

### Build Status Flow

1. **Trigger Build**: Button with `data-on-click="$$.post('/build/stream')"`
2. **Build Status**: Server streams build progress updates
3. **UI Updates**: Signals control loading, success, and error states
4. **Completion**: Final signal indicates build completion

## Component Integration

### Form Components

```python
def query_form(initial_sql: str = "", datastar_signal: str | None = None) -> str:
    """Generate a query form with Datastar integration."""
    return f"""
    <form action="/query/stream" method="POST" data-on-submit="$$post('/query/stream')" class="space-y-4">
        <div>
            <label for="sql" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                SQL Query
            </label>
            <textarea
                id="sql"
                name="sql"
                rows="8"
                class="block w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                placeholder="Enter SQL query..."
                data-signals="query_sql"
            >{initial_sql}</textarea>
        </div>
        <div class="flex items-center space-x-4">
            <button
                type="submit"
                class="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
                data-indicator="query-loading"
            >
                Run Query
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
```

### Layout Components

```python
def html_document(title: str, body_content: str) -> str:
    """Generate a complete HTML document with Datastar integration."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="/static/datastar.js"></script>
</head>
<body class="bg-gray-50 dark:bg-gray-900 min-h-screen">
    {body_content}
</body>
</html>"""
```

## Performance Considerations

### Efficient Streaming

- **Batch Events**: Group multiple signal updates in single SSE events
- **Minimal JSON**: Only send data that has changed
- **Connection Management**: Proper headers for SSE optimization

### Client-Side Optimization

- **Signal Debouncing**: Prevent excessive updates for rapid user input
- **Progressive Enhancement**: Fallback to basic HTML if JavaScript fails
- **Memory Management**: Clean up old signal values to prevent memory leaks

## Debugging Datastar Integration

### Browser Console

Use the browser console to monitor Datastar activity:

```javascript
// Check current signal values
console.log('Current signals:', window.$);

// Monitor signal changes
document.addEventListener('datastar-signal-patch', (event) => {
    console.log('Signal patch:', event.detail);
});

// Monitor DOM updates
document.addEventListener('datastar-patch-elements', (event) => {
    console.log('DOM patch:', event.detail);
});
```

### Server-Side Logging

Add logging to SSE endpoints:

```python
import logging

logger = logging.getLogger(__name__)

async def query_stream(ctx: DashboardContext, sql: str) -> Response:
    logger.info(f"Query stream started for SQL: {sql[:50]}...")

    try:
        # ... query execution logic ...
        logger.info(f"Query completed successfully, {len(result.rows)} rows")
    except Exception as exc:
        logger.error(f"Query failed: {exc}")
```

## Best Practices

1. **Consistent Signal Naming**: Use clear, descriptive signal names
2. **Error Handling**: Always include error signals for user feedback
3. **Loading States**: Show loading indicators for async operations
4. **Progressive Enhancement**: Ensure functionality works without JavaScript
5. **Signal Cleanup**: Reset signals when operations complete
6. **Performance**: Batch multiple signal updates when possible

## Migration from Traditional AJAX

If you're converting from traditional AJAX to Datastar:

**Before (AJAX):**
```javascript
fetch('/api/query', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => {
  document.getElementById('results').innerHTML = data.html;
  hideLoading();
})
.catch(error => {
  showError(error.message);
});
```

**After (Datastar):**
```html
<form data-on-submit="$$post('/query/stream')">
  <div data-show="$query_running">Loading...</div>
  <div data-show="$query_error" data-text="$query_error"></div>
  <div id="results"><!-- Updated by server --></div>
</form>
```

The Datastar approach eliminates client-side JavaScript complexity and provides automatic reactive behavior.