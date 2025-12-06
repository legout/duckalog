# Design: Dashboard UI Refactoring with Datastar

## Context

The current dashboard implementation is fundamentally broken:
- Uses `starhtml` and `starui` dependencies that aren't installed
- Falls back to 180 lines of custom HTML element generation
- Produces unstyled HTML with no modern UI patterns
- Has `datastar.js` bundled but not integrated
- CLI command is completely disabled

**Stakeholders**: End users who need to inspect DuckDB catalogs, developers maintaining the dashboard

**Constraints**:
- Must remain compatible with existing Duckalog catalog engine
- Should work offline (no CDN dependencies)
- Must be installable via optional `[ui]` dependency group
- Python 3.12+ required

## Goals / Non-Goals

### Goals
- Functional dashboard with modern UI that loads without errors
- Real-time updates via Datastar for improved UX
- Responsive design supporting mobile/tablet
- Clean, maintainable codebase with proper separation of concerns
- Type-safe component architecture

### Non-Goals
- Not building a full-featured database admin tool
- Not supporting database writes (read-only queries only)
- Not implementing authentication/authorization (local dashboard only)
- Not supporting custom plugins or extensions in v1

## Decisions

### Decision 1: Litestar over Starlette
**Rationale**: 
- Better async support with modern Python features
- Built-in dependency injection simplifies state management
- Superior type safety and IDE support
- Active development and growing ecosystem
- Performance improvements over Starlette

**Alternatives Considered**:
- **Starlette**: Current choice, but lacks features needed for complex UI
- **Sanic**: Fast but less Pythonic, smaller ecosystem
- **FastAPI**: Too heavy for a simple dashboard, adds unnecessary overhead

### Decision 2: h2py for HTML Templating
**Rationale**:
- Pythonic syntax that feels natural
- Type-safe with IDE completion
- Works well with Datastar attributes
- No template language to learn
- Direct Python control flow

**Alternatives Considered**:
- **rustytags**: Rust-based, adds compilation complexity
- **Jinja2**: String templates lack type safety
- **htmx**: Requires separate template files

### Decision 3: starui for Components
**Rationale**:
- Designed specifically for Datastar ecosystem
- Provides shadcn/ui-style modern components
- Type-safe Python API
- Integrates seamlessly with h2py

**Alternatives Considered**:
- **basecoatui**: Works with any stack but less Datastar-optimized
- **Custom components**: Too much effort to replicate starui quality

### Decision 4: Datastar for Reactivity
**Rationale**:
- Server-driven architecture fits Duckalog's backend focus
- No complex JavaScript build process required
- Efficient SSE-based updates
- Signals provide clean state management
- Official Python SDK available

**Alternatives Considered**:
- **HTMX**: Popular but less powerful state management
- **Alpine.js**: Requires more client-side logic
- **React/Vue**: Massive overkill, requires build tooling

### Decision 5: Tailwind CSS for Styling
**Rationale**:
- Utility-first approach is fast and flexible
- Works well with Python-generated HTML
- starui components use Tailwind
- No CSS file to maintain separately
- Can use CDN or compile for production

**Alternatives Considered**:
- **Bootstrap**: Too opinionated, harder to customize
- **Custom CSS**: Time-consuming, harder to maintain

## Technical Architecture

### Directory Structure
```
src/duckalog/dashboard/
├── __init__.py           # Public exports
├── app.py                # Litestar app factory
├── state.py              # DashboardContext and state management
├── components/           # Reusable UI components
│   ├── __init__.py
│   ├── layout.py         # Page layout (header, nav, footer)
│   ├── tables.py         # Data tables for views
│   └── forms.py          # Query forms and inputs
└── routes/               # Route handlers
    ├── __init__.py
    ├── home.py           # Dashboard home page
    ├── views.py          # View listing and detail
    └── query.py          # Query interface with SSE
```

### Component Hierarchy
```
App (Litestar)
├── Static Files (/static)
├── Routes
│   ├── GET / → home_page()
│   ├── GET /views → views_list()
│   ├── GET /views/{name} → view_detail()
│   ├── GET /query → query_form()
│   └── POST /query/execute → query_stream() [SSE]
└── State (DashboardContext)
    ├── Config
    ├── DuckDB Connection
    └── Build Status
```

### Data Flow

**Query Execution Flow**:
1. User enters SQL in form with `data-bind` attribute
2. Signal `sql_query` updates on input change
3. Form submit triggers `data-on-submit="$$post('/query/execute')"`
4. Server receives request via Litestar route
5. DuckDB executes query in background
6. Results streamed via SSE with `ServerSentEventGenerator`
7. Datastar patches DOM with results table
8. Loading indicator controlled by `data-indicator`

**Build Status Flow**:
1. User clicks "Build Catalog" button
2. POST to `/build` triggers background build
3. SSE connection at `/build/status` streams updates
4. Datastar patches build status signals
5. UI updates in real-time without page reload

## Risks / Trade-offs

### Risk: Litestar Learning Curve
**Impact**: Medium  
**Mitigation**: Comprehensive documentation, examples in code comments, reference existing Litestar apps

### Risk: Datastar Maturity
**Impact**: Low  
**Probability**: Low - Datastar is stable at v1.0.0  
**Mitigation**: Fallback to basic HTML forms if SSE fails, graceful degradation

### Risk: Dependency Bloat
**Impact**: Medium  
**Probability**: Medium  
**Mitigation**: Keep dependencies in optional `[ui]` group, core Duckalog unaffected

### Trade-off: Python-Generated HTML vs Templates
**Benefit**: Type safety, no template language to learn  
**Cost**: More verbose than string templates  
**Decision**: Accept verbosity for type safety and maintainability

### Trade-off: Server-Driven vs Client-Heavy
**Benefit**: No JavaScript build process, simpler deployment  
**Cost**: More server load for SSE connections  
**Decision**: Dashboard is low-traffic, server load acceptable

## Migration Plan

### Phase 1: Foundation (Breaking)
1. Update dependencies in `pyproject.toml`
2. Remove old `views.py` fallback implementation
3. Create new directory structure
4. Implement basic Litestar app

### Phase 2: Core Features
1. Implement home page with dashboard metrics
2. Add view listing and detail pages
3. Create query interface with basic submission
4. Enable CLI command

### Phase 3: Datastar Integration
1. Add SSE endpoints for query streaming
2. Implement real-time build status
3. Add signal-based state management
4. Integrate starui components

### Phase 4: Polish
1. Add Tailwind styling and themes
2. Implement responsive design
3. Add error handling and user feedback
4. Comprehensive testing

### Rollback Plan
If critical issues arise:
1. Revert to commented-out dashboard code
2. Provide static HTML fallback
3. Document known issues for next iteration

### Compatibility
- **Breaking**: Complete API change for `duckalog.dashboard` module
- **Migration**: Users must reinstall UI dependencies
- **Documentation**: Update all dashboard references

## Open Questions

1. **Q**: Should we support custom themes beyond dark/light?  
   **A**: Not in v1; add as enhancement if requested

2. **Q**: Do we need pagination for view listings?  
   **A**: Yes, implement for catalogs with >100 views

3. **Q**: Should query history be persisted to disk?  
   **A**: Not in v1; use browser localStorage if needed

4. **Q**: What's the connection limit for SSE?  
   **A**: Start with 10 concurrent connections, tune based on usage

5. **Q**: Should we support exporting query results?  
   **A**: Yes, add CSV/JSON export buttons in Phase 4
