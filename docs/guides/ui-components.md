# UI Components Usage Guide

This guide explains how to use the dashboard's UI components and customize them for your own needs.

## Component Architecture

The dashboard uses a modular component-based architecture:

```
src/duckalog/dashboard/
├── components/
│   ├── layout.py     # Layout components (headers, navigation)
│   ├── forms.py      # Form components (queries, build triggers)
│   └── tables.py     # Table components (view listings, results)
└── routes/
    ├── home.py       # Home page route
    ├── views.py      # Views listing/detail routes
    ├── query.py      # Query interface route
    └── build.py      # Build management routes
```

## Layout Components

### HTML Document Wrapper

```python
from duckalog.dashboard.components import layout

# Create a complete HTML page
html = layout.html_document(
    title="Duckalog Dashboard",
    body_content="<h1>Welcome!</h1>",
    datastar_signals={"theme": "dark"}  # Optional initial signals
)
```

### Page Header

```python
from duckalog.dashboard.components import layout

# Generate a page header with title and subtitle
header_html = layout.page_header(
    title="Dashboard Overview",
    subtitle="Manage your Duckalog catalog"
)
```

### Navigation Bar

```python
from duckalog.dashboard.components import layout

# Generate navigation with active state
nav_html = layout.navigation(active_path="/views")
```

### Page Container

```python
from duckalog.dashboard.components import layout

# Wrap content in responsive container
container_html = layout.page_container("""
    <h2>Content Section</h2>
    <p>This content will be properly centered and responsive.</p>
""")
```

### Card Component

```python
from duckalog.dashboard.components import layout

# Create styled card containers
card_html = layout.card(
    content="""
        <h3>Statistics</h3>
        <p>Views: 42</p>
        <p>Tables: 15</p>
    """,
    class_name="bg-blue-50"  # Additional CSS classes
)
```

### Alert Component

```python
from duckalog.dashboard.components import layout

# Create different types of alerts
success_alert = layout.alert(
    message="Catalog built successfully!",
    alert_type="success"
)

error_alert = layout.alert(
    message="Query failed to execute",
    alert_type="error"
)

warning_alert = layout.alert(
    message="Large query result may be truncated",
    alert_type="warning"
)
```

### Loading Indicator

```python
from duckalog.dashboard.components import layout

# Show loading state
loading_html = layout.loading_indicator(
    message="Executing query..."
)
```

## Form Components

### Query Form

```python
from duckalog.dashboard.components import forms

# Create a query form with Datastar integration
query_form_html = forms.query_form(
    initial_sql="SELECT * FROM users LIMIT 10",
    datastar_signal="query_sql",  # Bind to signal
    action="/query/stream",       # Form submission endpoint
    method="POST"
)
```

### Search Form

```python
from duckalog.dashboard.components import forms

# Create a search form with reactive behavior
search_form_html = forms.search_form(
    placeholder="Search views by name...",
    datastar_signal="view_search",  # Signal for search input
    action="/views",               # Search endpoint
    method="GET"
)
```

### Build Form

```python
from duckalog.dashboard.components import forms

# Create a build trigger form
build_form_html = forms.build_form(
    action="/build/stream",  # Real-time build endpoint
    method="POST"
)
```

### Generic Button

```python
from duckalog.dashboard.components import forms

# Create buttons with different styles
primary_button = forms.button(
    text="Run Query",
    button_type="submit",
    variant="primary",
    onclick="handleQuerySubmit()"
)

secondary_button = forms.button(
    text="Cancel",
    variant="secondary",
    onclick="cancelOperation()"
)

success_button = forms.button(
    text="Export Results",
    variant="success",
    href="/export/csv"
)

# Link button (styled as button but acts as link)
link_button = forms.link_button(
    text="View Documentation",
    href="/docs",
    variant="secondary"
)
```

## Table Components

### Query Results Table

```python
from duckalog.dashboard.components import tables

# Display query results in a styled table
table_html = tables.query_results_table(
    columns=["name", "age", "department"],
    rows=[
        ("Alice", 25, "Engineering"),
        ("Bob", 30, "Marketing"),
        ("Charlie", 35, "Sales")
    ],
    truncated=False,  # Whether results were truncated
    title="User Results"  # Optional table title
)
```

### View Listing Table

```python
from duckalog.dashboard.components import tables

# Display catalog views in a table
views_data = [
    {"name": "users", "source": "sql", "database": "catalog.duckdb", "table": "", "semantic": "yes"},
    {"name": "orders", "source": "csv", "database": "", "table": "orders.csv", "semantic": "no"},
]

table_html = tables.views_table(
    views=views_data,
    title="Catalog Views"
)
```

## Datastar Integration Examples

### Reactive Form with Loading State

```python
def create_reactive_form():
    """Create a form with real-time feedback."""
    return f"""
    <form data-on-submit="$$post('/query/stream')" class="space-y-4">
        <!-- Input bound to signal -->
        <textarea
            name="sql"
            rows="6"
            class="w-full p-2 border rounded"
            placeholder="Enter SQL query..."
            data-bind="query_sql"
            data-signals="query_sql"
        >SELECT 1 as test</textarea>

        <!-- Submit button with loading indicator -->
        <button
            type="submit"
            class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            data-indicator="query-submit-loading"
        >
            Execute Query
        </button>

        <!-- Loading state - shown when query_running is true -->
        <div
            id="query-loading"
            data-show="$query_running"
            class="hidden mt-4"
        >
            <div class="flex items-center space-x-2 text-blue-600">
                <div class="animate-spin h-4 w-4">⟳</div>
                <span>Executing query...</span>
            </div>
        </div>

        <!-- Error state - shown when query_error exists -->
        <div
            id="query-error"
            data-show="$query_error"
            class="hidden mt-4"
        >
            <div class="bg-red-50 text-red-800 p-3 rounded">
                <strong>Error:</strong> <span data-text="$query_error"></span>
            </div>
        </div>

        <!-- Results container -->
        <div id="query-results" class="mt-4">
            <!-- Results will be injected here by server -->
        </div>
    </form>
    """
```

### Real-time Build Status

```python
def create_build_status_component():
    """Create a component showing real-time build status."""
    return f"""
    <div class="space-y-4">
        <!-- Build trigger button -->
        <button
            data-on-click="$$.post('/build/stream')"
            class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            data-indicator="build-submit-loading"
        >
            Build Catalog
        </button>

        <!-- Build status indicators -->
        <div id="build-status" class="space-y-2">
            <!-- Loading state -->
            <div
                data-show="$build_running"
                class="hidden p-3 bg-blue-50 text-blue-800 rounded"
            >
                <div class="flex items-center space-x-2">
                    <div class="animate-spin h-4 w-4">⟳</div>
                    <span>Building catalog...</span>
                </div>
            </div>

            <!-- Success state -->
            <div
                data-show="$build_success"
                class="hidden p-3 bg-green-50 text-green-800 rounded"
            >
                <div class="flex items-center space-x-2">
                    <span>✓</span>
                    <span data-text="$build_summary">Build completed successfully!</span>
                </div>
            </div>

            <!-- Error state -->
            <div
                data-show="$build_error"
                class="hidden p-3 bg-red-50 text-red-800 rounded"
            >
                <div class="flex items-center space-x-2">
                    <span>✗</span>
                    <span data-text="$build_error">Build failed!</span>
                </div>
            </div>
        </div>
    </div>
    """
```

## Custom Component Creation

### Creating Custom Layout Components

```python
def create_dashboard_stats(stats: dict[str, Any]) -> str:
    """Create a custom statistics dashboard component."""
    return f"""
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div class="bg-white p-6 rounded-lg shadow">
            <h3 class="text-lg font-semibold text-gray-900 mb-2">Views</h3>
            <p class="text-3xl font-bold text-blue-600">{stats.get('views', 0)}</p>
            <p class="text-sm text-gray-600">Total catalog views</p>
        </div>

        <div class="bg-white p-6 rounded-lg shadow">
            <h3 class="text-lg font-semibold text-gray-900 mb-2">Tables</h3>
            <p class="text-3xl font-bold text-green-600">{stats.get('tables', 0)}</p>
            <p class="text-sm text-gray-600">Source tables</p>
        </div>

        <div class="bg-white p-6 rounded-lg shadow">
            <h3 class="text-lg font-semibold text-gray-900 mb-2">Size</h3>
            <p class="text-3xl font-bold text-purple-600">{stats.get('size_mb', '0')} MB</p>
            <p class="text-sm text-gray-600">Database size</p>
        </div>
    </div>
    """
```

### Creating Custom Form Components

```python
def create_export_form(results_available: bool = False) -> str:
    """Create an export form component."""
    disabled = "disabled" if not results_available else ""
    disabled_class = "opacity-50 cursor-not-allowed" if not results_available else ""

    return f"""
    <div class="mt-4 p-4 border rounded-lg">
        <h3 class="text-lg font-semibold mb-3">Export Results</h3>

        <form data-on-submit="$$post('/export')" class="flex items-center space-x-4">
            <select name="format" class="px-3 py-2 border rounded" {disabled}>
                <option value="csv">CSV</option>
                <option value="json">JSON</option>
                <option value="parquet">Parquet</option>
            </select>

            <button
                type="submit"
                class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 {disabled_class}"
                {disabled}
            >
                Download Results
            </button>
        </form>

        {'' if results_available else '<p class="text-sm text-gray-600 mt-2">Run a query first to enable export</p>'}
    </div>
    """
```

## Styling Customization

### Using Tailwind CSS Classes

All components use Tailwind CSS classes for styling. You can customize the appearance by:

```python
# Custom card with different colors
custom_card = layout.card(
    content="Important notice",
    class_name="bg-yellow-50 border-yellow-200 border"  # Yellow theme
)

# Custom button with additional styling
custom_button = forms.button(
    text="Special Action",
    variant="primary",
    datastar_attrs={
        "loading": "submit-loading",  # Custom signal for loading state
        "disabled": "!form_invalid"   # Disable when form is invalid
    }
)
```

### Custom CSS Integration

For additional customization, you can inject custom CSS:

```python
def create_custom_styled_component() -> str:
    return """
    <style>
        .custom-highlight {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem;
            border-radius: 0.5rem;
        }

        .custom-animate {
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
    </style>

    <div class="custom-highlight custom-animate">
        <h3>Custom Styled Component</h3>
        <p>This uses custom CSS for unique styling.</p>
    </div>
    """
```

## Testing Components

### Component Testing Pattern

```python
def test_query_form_component():
    """Test the query form component generation."""
    from duckalog.dashboard.components import forms

    # Generate form
    form_html = forms.query_form(
        initial_sql="SELECT 1",
        datastar_signal="test_signal"
    )

    # Verify expected content
    assert "data-bind=\"test_signal\"" in form_html
    assert "SELECT 1" in form_html
    assert "data-signals=\"query_sql\"" in form_html
    assert "data-on-submit" in form_html

def test_alert_components():
    """Test alert component variants."""
    from duckalog.dashboard.components import layout

    success = layout.alert("Success!", "success")
    error = layout.alert("Error!", "error")

    assert "bg-green-50" in success  # Success styling
    assert "bg-red-50" in error     # Error styling
```

## Best Practices

1. **Consistent Styling**: Use Tailwind classes consistently across components
2. **Accessibility**: Include proper ARIA labels and semantic HTML
3. **Responsive Design**: Test components on different screen sizes
4. **Signal Naming**: Use descriptive signal names for clarity
5. **Error Handling**: Always include error states in reactive components
6. **Loading States**: Show loading indicators for async operations
7. **Progressive Enhancement**: Ensure components work without JavaScript

## Advanced Usage

### Dynamic Component Selection

```python
def create_component_based_on_user_role(role: str) -> str:
    """Create different components based on user permissions."""
    if role == "admin":
        return forms.build_form()  # Admin can trigger builds
    else:
        return layout.alert(
            "Build functionality requires admin privileges",
            "warning"
        )
```

### Component Composition

```python
def create_dashboard_page(user_role: str, catalog_stats: dict):
    """Compose multiple components into a complete page."""

    header = layout.page_header("Dashboard", "Manage your catalog")
    nav = layout.navigation(active_path="/")
    stats = create_dashboard_stats(catalog_stats)
    build_component = create_component_based_on_user_role(user_role)

    content = header + nav + layout.page_container(
        stats + build_component
    )

    return layout.html_document("Dashboard", content)
```

This component system provides a flexible, reusable foundation for building responsive, interactive dashboard interfaces with real-time capabilities.