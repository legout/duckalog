# Design: Modern Dashboard UI Architecture

## Architectural Decisions

### 1. HTPY over Traditional Templating
**Decision**: Use HTPY for HTML generation instead of legacy fallback system
**Rationale**:
- Python-native HTML generation without template language complexity
- Excellent IDE support with type checking and completion
- Better integration with modern Python development workflows
- Eliminates the current type issues with starhtml/starui imports

**Impact**: Replaces the current `_Elt` fallback class and improves type safety

### 2. BasecoatUI CSS Framework + Custom HTPY Components
**Decision**: Use BasecoatUI for styling with custom HTPY components
**Rationale**:
- BasecoatUI works with any web stack, not tied to specific frameworks
- Tailwind CSS foundation provides modern, utility-first styling approach
- Custom HTPY components give full control over HTML structure and behavior
- Better separation of concerns: styling (BasecoatUI) vs structure (HTPY)
- More maintainable and extensible than pre-built component libraries

**Impact**: Creates a clean, maintainable component architecture with full customization

### 3. Datastar + datastar-python Integration
**Decision**: Fully integrate Datastar for frontend reactivity using the official Python SDK
**Rationale**:
- Declarative data attributes align with HTPY Python-native approach
- Server-Sent Events provide real-time updates without complex JavaScript
- Backend-driven state management simplifies architecture
- Official Python SDK provides framework-specific helpers for Starlette

**Impact**: Transforms static dashboard into reactive, real-time interface

### 4. Starlette Framework Preservation
**Decision**: Keep existing Starlette application structure
**Rationale**:
- Starlette is already excellent and performant
- datastar-python has built-in Starlette integration
- Preserves existing ASGI application patterns
- Minimizes disruption to core architecture

**Impact**: Enhances existing app rather than replacing it

## Component Architecture

### New Package Structure
```
src/duckalog/dashboard/
├── components/          # Custom HTPY components with BasecoatUI
│   ├── navigation.py    # Sidebar, breadcrumbs
│   ├── tables.py       # Data tables, view listings  
│   ├── cards.py        # Dashboard metrics cards
│   ├── forms.py        # Query forms, search
│   ├── layout.py       # Base layout, page structure
│   └── ui/             # Reusable UI primitives
│       ├── buttons.py  # Button components
│       ├── inputs.py   # Form input components
│       └── modals.py   # Modal dialog components
├── templates/          # HTPY page templates
│   ├── home.html       # Dashboard overview
│   ├── views.html      # Views browser
│   ├── query.html      # Query interface
│   └── detail.html     # View detail pages
├── static/            # Static assets
│   ├── datastar.js    # Local Datastar bundle
│   ├── basecoat.css   # BasecoatUI CSS framework
│   └── custom.css     # Additional custom styles
├── state.py           # Keep existing (good structure)
├── app.py             # Enhance for Datastar
├── views.py           # Rewrite with HTPY + BasecoatUI
└── run.py             # Keep existing
```

### Component Design Patterns

#### 1. HTPY + BasecoatUI Integration
```python
from htpy import *

def dashboard_card(title: str, value: str, description: str = ""):
    """Create a custom card component using HTPY + BasecoatUI."""
    return div(class_="bc-card")[
        div(class_="bc-card-header")[
            h3(title, class_="bc-card-title")
        ],
        div(class_="bc-card-body")[
            div(value, class_="bc-card-value"),
            p(description, class_="bc-card-description") if description else ""
        ]
    ]

def view_table(views: list[dict]):
    """Create a custom data table using HTPY + BasecoatUI."""
    return div(class_="bc-table-container")[
        table(class_="bc-table")[
            thead(class_="bc-table-header")[
                tr([
                    th("Name", class_="bc-table-header-cell"),
                    th("Source", class_="bc-table-header-cell"),
                    th("Status", class_="bc-table-header-cell"),
                    th("Actions", class_="bc-table-header-cell")
                ])
            ],
            tbody(class_="bc-table-body")[
                *[view_row(view) for view in views]
            ]
        ]
    ]

def navigation_sidebar(active_section: str):
    """Create a custom navigation component."""
    return nav(class_="bc-sidebar")[
        div(class_="bc-sidebar-header")[
            h2("Duckalog", class_="bc-sidebar-title")
        ],
        ul(class_="bc-sidebar-nav")[
            li([
                a("Dashboard", href="/", class_=f"bc-nav-link {'bc-nav-link-active' if active_section == 'dashboard' else ''}")
            ]),
            li([
                a("Views", href="/views", class_=f"bc-nav-link {'bc-nav-link-active' if active_section == 'views' else ''}")
            ]),
            li([
                a("Query", href="/query", class_=f"bc-nav-link {'bc-nav-link-active' if active_section == 'query' else ''}")
            ])
        ]
    ]
```

#### 2. Datastar Reactive Patterns
```python
from datastar_py.starlette import datastar_response, read_signals, ServerSentEventGenerator as SSE

@datastar_route("/api/views/search")
@datastar_response
async def search_views(request):
    """Reactive view search with real-time updates."""
    signals = await read_signals(request)
    query = signals.get('searchQuery', '')
    filter_type = signals.get('filterType', 'all')
    
    views = await get_filtered_views(query, filter_type)
    
    # Return reactive HTML update
    yield SSE.patch_elements(
        render_views_table(views),
        selector="#views-table"
    )
    
    # Update view count signal
    yield SSE.patch_signals({"viewCount": len(views)})
```

#### 3. State Management
```python
@dataclass
class DashboardSignals:
    """Centralized dashboard state for Datastar."""
    selected_view: str | None = None
    search_query: str = ""
    filter_type: str = "all"
    build_status: str = "idle"
    view_count: int = 0
    
    def to_datastar_signals(self) -> dict:
        """Convert to Datastar signals format."""
        return {
            "selectedView": self.selected_view,
            "searchQuery": self.search_query,
            "filterType": self.filter_type,
            "buildStatus": self.build_status,
            "viewCount": self.view_count
        }
```

## Data Flow Architecture

### 1. Request Flow
```
User Request → Starlette Route → HTPY View → StarUI Component
     ↓              ↓              ↓              ↓
Datastar Signals → State Update → Reactive HTML → Browser Update
```

### 2. Real-time Update Flow
```
Backend Event → SSE Generator → Datastar Framework → Browser DOM Update
     ↓              ↓                 ↓                    ↓
Build Complete → Signal Patch → Attribute Change → UI Re-render
```

### 3. User Interaction Flow
```
User Action → Datastar Attribute → Backend Endpoint → State Update → UI Response
     ↓              ↓                   ↓               ↓           ↓
Click Button → data-on:click=@post() → Route Handler → Signal Update → Patch DOM
```

## Security Considerations

### 1. Existing Security Preservation
- Maintain all current read-only SQL enforcement
- Preserve admin token protection for mutating operations
- Keep CORS protection and localhost restriction by default
- Continue atomic configuration update patterns

### 2. New Security Features
- Add CSRF protection for Datastar endpoints
- Implement rate limiting for real-time features
- Add input validation for reactive components
- Ensure secure WebSocket/SSE connections

### 3. Asset Security
- Serve Datastar script locally to prevent supply chain attacks
- Implement Subresource Integrity (SRI) for bundled assets
- Add Content Security Policy headers
- Validate all dynamic HTML content

## Performance Strategy

### 1. Bundle Optimization
- Tree-shake unused StarUI components
- Lazy load non-critical JavaScript features
- Minimize Datastar bundle size
- Implement code splitting for large features

### 2. Rendering Performance
- Use HTPY's efficient HTML generation
- Implement virtual scrolling for large view lists
- Add progressive loading for heavy components
- Optimize Datastar signal update frequency

### 3. Caching Strategy
- Cache frequently accessed view metadata
- Implement client-side caching for query results
- Add service worker for offline functionality
- Use HTTP caching headers appropriately

## Migration Strategy

### 1. Backward Compatibility
- Maintain all existing API endpoints
- Preserve Python API (`run_dashboard`) interface
- Keep existing test expectations
- Support legacy configurations

### 2. Gradual Migration
- Phase 1: Replace HTML generation while preserving functionality
- Phase 2: Add StarUI components incrementally
- Phase 3: Integrate Datastar features alongside existing UI
- Phase 4: Enable real-time features and remove legacy patterns

### 3. Rollback Plan
- Feature flags for new components
- Ability to disable Datastar features
- Fallback to previous rendering method if needed
- Preserve old asset paths during transition

## Testing Strategy

### 1. Component Testing
- Unit tests for all HTPY components
- StarUI component integration tests
- Datastar signal handling tests
- Accessibility compliance testing

### 2. End-to-End Testing
- Complete user workflow testing
- Real-time feature validation
- Cross-browser compatibility
- Mobile responsiveness testing

### 3. Performance Testing
- Bundle size monitoring
- Loading time benchmarks
- Real-time update latency testing
- Memory usage monitoring

## Risk Assessment

### Technical Risks
- **HTPY Learning Curve**: Mitigate with comprehensive examples and documentation
- **Datastar Integration Complexity**: Use official Python SDK and examples
- **Performance Regression**: Continuous monitoring and optimization
- **Browser Compatibility**: Test across modern browsers

### User Experience Risks
- **Feature Regression**: Maintain all existing functionality during migration
- **Learning Curve**: Provide clear migration guides and help system
- **Accessibility**: Regular testing with assistive technologies
- **Mobile Experience**: Responsive design from the start

### Project Risks
- **Scope Creep**: Strict adherence to defined phases and requirements
- **Timeline Delays**: Flexible implementation with MVP-first approach
- **Dependency Issues**: Pin versions and provide fallbacks
- **Test Coverage**: Automated testing throughout implementation

This design provides a solid foundation for transforming the duckalog dashboard into a modern, professional, and highly usable interface while preserving all existing functionality and meeting the comprehensive requirements already defined in the dashboard-ui specification.