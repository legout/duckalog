# Design: Complete Dashboard Modernization

## Context

The duckalog dashboard provides a local web UI for browsing catalog metadata, running ad-hoc SQL queries, and triggering catalog builds. The current implementation:
- Uses Starlette as the ASGI framework (stable, working well)
- Already bundles datastar.js (v1.0.0-RC.6) but doesn't use it
- Attempts to import starhtml/starui but falls back to 168 lines of custom HTML element classes
- Has no CSS framework, resulting in completely unstyled raw HTML
- Uses traditional request/response cycles with full page reloads

**Constraints:**
- Local-first deployment (default localhost binding)
- Python-only stack (no JavaScript build tools)
- Minimal dependencies
- Optional UI (via `[ui]` extra in pyproject.toml)

**Stakeholders:**
- Data engineers using duckalog for catalog management
- Developers exploring catalog structure and testing queries
- DevOps/Platform teams deploying duckalog in local environments

## Goals / Non-Goals

### Goals
1. ✅ **Modern, professional UI** - Replace unstyled HTML with shadcn/ui-inspired components
2. ✅ **Real-time interactivity** - Use Datastar SSE for streaming query results and build status
3. ✅ **Better UX** - Add query history, data export, syntax highlighting, visual query builder
4. ✅ **Simplify codebase** - Remove 168-line fallback layer, use proper dependencies
5. ✅ **Responsive design** - Desktop-first, but usable on mobile devices
6. ✅ **Maintain stability** - Keep Starlette, preserve existing Python API

### Non-Goals
- ❌ Multi-user authentication (remains local-only for now)
- ❌ Cloud deployment features (CORS, CDN integration, etc.)
- ❌ Full SQL IDE capabilities (keep query builder simple)
- ❌ Real-time collaboration features
- ❌ Framework migration (staying with Starlette)

## Decisions

### Decision 1: Keep Starlette, Enhance with Datastar
**What:** Continue using Starlette as the web framework, add Datastar for real-time features.

**Why:**
- Starlette is proven stable in current implementation
- Switching frameworks (Litestar, Sanic) would require significant rewrite for minimal benefit
- Datastar is already bundled and perfect for Python-first hypermedia apps
- SSE (Server-Sent Events) natural fit for streaming query results

**Alternatives considered:**
- **Litestar**: More features, better for complex apps, but adds complexity and requires rewrite
- **Sanic**: Fast but different async paradigm, would require rewrite
- **FastAPI**: Overkill for this use case, no significant benefit over Starlette

**Trade-offs:**
- ✅ No rewrite needed, can focus on features
- ✅ Datastar provides exactly what we need (SSE, reactive signals)
- ⚠️ Less "batteries included" than Litestar, but we don't need those batteries

### Decision 2: StarUI for Components (Require as Dependency)
**What:** Use StarUI component library and make it a required dependency in `[ui]` extra.

**Why:**
- StarUI provides shadcn/ui-inspired components in pure Python
- Already attempted in codebase (with fallback)
- Tailwind CSS v4 integration built-in
- Python-native, no separate template files
- Type-safe component approach

**Alternatives considered:**
- **BasecoatUI**: Generic Tailwind components, but not Python-specific, less integration
- **Custom Tailwind + raw HTML**: Flexible but requires more manual work, no component library benefits
- **Keep fallback layer**: Maintains current mess, duplicates code, harder to maintain

**Migration path:**
- Remove fallback compatibility layer (views.py:13-181)
- Require `starui>=0.1.8` in `[ui]` extra
- Document that users must install with `pip install duckalog[ui]`
- Existing users with `[ui]` extra will get new deps automatically on upgrade

**Trade-offs:**
- ✅ Clean, maintainable code (-168 lines of fallback)
- ✅ Modern components with good DX
- ⚠️ **BREAKING**: Makes dependencies required (but only for optional UI extra)
- ⚠️ StarUI is still early (v0.1.8), but actively maintained and stable enough

### Decision 3: Datastar for Real-time Features
**What:** Use Datastar + datastar-python for SSE-based real-time updates.

**Why:**
- Perfect for Python-first apps (no frontend build step)
- SSE ideal for query result streaming (one-way server → client)
- Reactive signals for client-side UI state (search filters, tabs)
- Already bundled in src/duckalog/static/datastar.js

**Implementation pattern:**
```python
from datastar_py import ServerSentEventGenerator as SSE
from datastar_py.starlette import DatastarResponse

@app.get("/query-stream")
async def query_stream(request):
    sql = request.query_params.get("sql")
    
    async def stream():
        result = ctx.run_query(sql)
        # Stream results in chunks
        for chunk in paginate(result.rows, 100):
            yield SSE.patch_elements(
                render_rows(chunk),
                selector="#results tbody",
                mode="append"
            )
    
    return DatastarResponse(stream())
```

**Alternatives considered:**
- **WebSockets**: Bidirectional, but overkill for our use case (mostly server → client)
- **HTMX**: Popular, but requires more manual SSE setup, less Python-friendly
- **Polling**: Simple but inefficient, not real-time

**Trade-offs:**
- ✅ True real-time updates without polling
- ✅ Efficient for streaming large result sets
- ✅ Python-native SDK with Starlette integration
- ⚠️ Requires learning Datastar patterns (but simpler than React/Vue)

### Decision 4: Simple Visual Query Builder
**What:** Build a simple SELECT query builder, NOT a full SQL IDE.

**Scope:**
- ✅ View selection (dropdown)
- ✅ Column selection (checkboxes)
- ✅ Simple WHERE filters (column, operator, value)
- ✅ SQL preview (generated query display)
- ❌ JOINs (too complex for simple builder)
- ❌ Subqueries, CTEs (too complex)
- ❌ Aggregations, GROUP BY (future enhancement)

**Why:**
- Provides quick exploration without writing SQL
- Keeps complexity manageable (2-3 hours implementation)
- Covers 80% of common exploration queries
- Users can copy generated SQL to editor for complex modifications

**Implementation approach:**
```python
# Backend API endpoint
@app.post("/query-builder/generate")
async def generate_query(request):
    data = await request.json()
    view = data["view"]
    columns = data["columns"]  # ["id", "name", "email"]
    filters = data["filters"]  # [{"col": "status", "op": "=", "val": "active"}]
    
    sql = f"SELECT {', '.join(columns)}\nFROM {view}"
    if filters:
        where_clauses = [f"{f['col']} {f['op']} '{f['val']}'" for f in filters]
        sql += f"\nWHERE {' AND '.join(where_clauses)}"
    
    return {"sql": sql}
```

**Trade-offs:**
- ✅ Useful for quick exploration
- ✅ Low complexity, quick to implement
- ⚠️ Limited to simple queries (but that's intentional)

### Decision 5: Export Formats and Approach
**What:** Support CSV (client-side) and Parquet (server-side) export.

**Why:**
- **CSV**: Universal format, small files can be generated client-side
- **Parquet**: Native DuckDB format, efficient for large datasets, requires server-side generation
- Excel/JSON excluded for simplicity (can add later if needed)

**Implementation:**
```python
# CSV: Generate client-side from table data
# In frontend (Datastar signal):
<button data-on:click="exportToCSV($results)">Export CSV</button>

# Parquet: Server-side generation
@app.get("/export/parquet")
async def export_parquet(request):
    sql = request.query_params.get("sql")
    result = ctx.run_query(sql)
    
    # Use DuckDB to write Parquet
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".parquet")
    conn.execute(f"COPY ({sql}) TO '{temp_file.name}' (FORMAT PARQUET)")
    
    return FileResponse(temp_file.name, filename="query_result.parquet")
```

**Trade-offs:**
- ✅ CSV for quick, small exports
- ✅ Parquet for efficient large dataset exports
- ⚠️ Parquet requires server roundtrip (but that's expected for large data)

### Decision 6: File Structure Reorganization
**What:** Add component modules, keep existing structure mostly intact.

**New structure:**
```
src/duckalog/dashboard/
├── __init__.py           # Existing
├── app.py                # Modified: Add SSE endpoints, export routes
├── run.py                # Unchanged
├── state.py              # Modified: Add export methods
├── views.py              # MAJOR REFACTOR: Remove fallback, use StarUI
├── components/           # NEW: Reusable UI components
│   ├── __init__.py
│   ├── layout.py         # Base layout, navigation, page structure
│   ├── tables.py         # Table component with pagination
│   ├── query_editor.py   # SQL editor with syntax highlighting
│   └── query_builder.py  # Visual query builder UI
└── static/               # NEW: Static assets
    ├── datastar.js       # Moved from parent static/
    └── themes.css        # Optional custom theme tweaks
```

**Why:**
- Separates concerns (views generate pages, components are reusable)
- Makes testing easier (can test components in isolation)
- Keeps app.py focused on routing
- Keeps state.py focused on business logic

**Trade-offs:**
- ✅ Better organization, easier maintenance
- ✅ Reusable components across pages
- ⚠️ More files (but clearer responsibilities)

## Risks / Trade-offs

### Risk 1: StarUI Maturity
**Risk:** StarUI is relatively new (v0.1.8, 2 GitHub stars)
**Likelihood:** Medium
**Impact:** Medium (could have bugs or breaking changes)

**Mitigation:**
- Pin specific version in requirements (`starui==0.1.8`)
- Test all components thoroughly before release
- Have fallback plan: could switch to manual Tailwind + HTML if needed
- Components are simple enough to replace if necessary

### Risk 2: Breaking Change for UI Users
**Risk:** Making starui/datastar-python required breaks installations without them
**Likelihood:** High (this is intentional)
**Impact:** Low (UI is optional extra, easy to upgrade)

**Mitigation:**
- Clear documentation of changes in CHANGELOG
- Migration guide for upgrading
- Version bump to indicate breaking change (0.4.x → 0.5.0)
- UI remains optional (`[ui]` extra), core library unaffected

### Risk 3: Increased Bundle Size
**Risk:** Adding CSS/JS dependencies increases package size
**Likelihood:** Low (using CDN for Tailwind, datastar.js already bundled)
**Impact:** Low

**Mitigation:**
- Use CDN for Tailwind CSS (no bundle size impact)
- datastar.js already included (37KB)
- Total increase: ~0KB (already have datastar.js)

### Risk 4: Learning Curve for Contributors
**Risk:** New patterns (Datastar, StarUI) may confuse contributors
**Likelihood:** Medium
**Impact:** Low

**Mitigation:**
- Comprehensive inline code comments
- Update contributor docs with examples
- Datastar is simpler than React/Vue (less learning needed)
- StarUI follows familiar shadcn/ui patterns

## Migration Plan

### Phase 1: Foundation (Non-breaking prep)
1. Update `pyproject.toml` to add new dependencies to `[ui]` extra
2. Create `components/` module structure
3. Add base layout component with navigation
4. No changes to existing routes yet

### Phase 2: Views Refactor (Breaking change)
1. Remove fallback compatibility layer (views.py:13-181)
2. Rewrite view functions to use StarUI components
3. Add Tailwind CSS + Datastar CDN links to base layout
4. Update tests to verify new components

### Phase 3: Real-time Features (Additive)
1. Add SSE endpoints for query streaming
2. Add real-time build status updates
3. Implement progressive table loading

### Phase 4: Enhanced Features (Additive)
1. Add query history (localStorage)
2. Add export endpoints
3. Add syntax highlighting
4. Add visual query builder

### Rollback Strategy
If issues arise post-deployment:
1. **Immediate:** Pin to previous version in requirements
2. **Short-term:** Re-add fallback layer as temporary fix
3. **Long-term:** Fix issues in new implementation, release patch

### Testing Strategy
- Unit tests for all new components
- Integration tests for SSE endpoints
- E2E tests for complete user flows
- Manual testing on multiple browsers
- Test with and without JavaScript enabled (graceful degradation)

## Open Questions

1. ~~**Color scheme**: Neutral grays vs. terminal-inspired green/cyan accents?~~
   - **Resolved**: Keep flexible, allow theme customization via CSS variables

2. **Query history limit**: How many queries to store? 
   - **Proposed**: 20 queries (localStorage limit ~5MB, should be plenty)

3. **Table pagination**: Default rows per page?
   - **Proposed**: 50 rows default, configurable (25, 50, 100, 500)

4. **Syntax highlighting library**: Which to use?
   - **Proposed**: Highlight.js (lightweight, no build step) or Prism.js

5. **Dark mode**: Include in initial release or future enhancement?
   - **Proposed**: Future enhancement (Phase 5+), focus on light mode first

6. **Export limits**: Max rows for exports to prevent memory issues?
   - **Proposed**: CSV: 10,000 rows (client-side), Parquet: 1,000,000 rows (server-side)

7. **Keyboard shortcuts**: Which ones to support initially?
   - **Proposed**: Ctrl/Cmd+Enter (run query), Ctrl/Cmd+K (focus search)
