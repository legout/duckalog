# Change: Complete Dashboard Modernization with Modern Stack

## Why

The current dashboard implementation has a functional backend but lacks modern UI aesthetics, interactivity, and user experience features. The existing codebase already includes `datastar.js` and attempts to use `starhtml/starui` but falls back to a 168-line custom HTML element compatibility layer when these dependencies aren't installed. This creates maintenance burden, code duplication, and a suboptimal user experience.

**Current Pain Points:**
- **No styling** - Completely unstyled HTML with raw tables and buttons
- **No interactivity** - Full page reloads for every operation
- **Poor data visualization** - Plain text tables with no formatting or pagination
- **Maintenance complexity** - Fallback compatibility layer (views.py:13-181) adds code duplication
- **Unused potential** - datastar.js is bundled but not utilized for real-time features

**Opportunity:**
The codebase is already structured for modernization with Starlette (proven stable), datastar.js bundled, and starter imports for starhtml/starui. We can build on this foundation to create a professional, responsive dashboard that matches modern data tool expectations.

## What Changes

### 1. Dependencies & Stack (**BREAKING** for `[ui]` extra)
- **Make starui and datastar-python required** in `pyproject.toml` `[ui]` extra
- **Remove fallback compatibility layer** (views.py:13-181) - simplify to ~160 fewer lines
- Update documentation to reflect required dependencies

### 2. Foundation & Styling
- Integrate **StarUI components** (Button, Card, Alert, Badge, Table, Input)
- Add **Tailwind CSS v4** via CDN for modern utility-first styling
- Create **base layout component** with consistent navigation
- Implement **responsive design** (desktop-first, mobile-friendly)

### 3. Real-time Interactivity with Datastar
- **Query execution streaming** - Stream SQL results via Server-Sent Events (SSE)
- **Real-time build status** - Live updates without page refresh
- **Progressive data loading** - Show results as they arrive, not after completion
- **Client-side filtering** - Instant search in views list using Datastar signals

### 4. Enhanced Features
- **Query history** - Browser localStorage-based, last 20 queries
- **Data export** - CSV (client-side) and Parquet (server-side) downloads
- **Syntax highlighting** - Code highlighting for SQL in query editor and view details
- **Visual query builder** - Simple SELECT builder (view picker, column selector, basic WHERE filters)
- **Better error presentation** - Formatted error messages with helpful context

### 5. User Experience Improvements
- **Loading states** - Progress indicators for long-running operations
- **Toast notifications** - Non-blocking feedback for actions
- **Keyboard shortcuts** - Common operations (Ctrl+Enter to run query)
- **Form validation** - Real-time feedback as users type
- **Table pagination** - Handle large result sets efficiently

## Impact

### Affected Specs
- **dashboard-ui** - MODIFIED: All 9 existing requirements enhanced with new capabilities
- **dashboard-ui** - ADDED: 8 new requirements for modern features

### Affected Code
- `src/duckalog/dashboard/views.py` - **MAJOR REFACTOR**
  - Remove lines 13-181 (fallback compatibility layer)
  - Rewrite all view functions to use StarUI components
  - Add new component modules for reusability
  
- `src/duckalog/dashboard/app.py` - **MODERATE CHANGES**
  - Add SSE endpoints for real-time query streaming
  - Add export endpoints (CSV, Parquet)
  - Add query builder API endpoint
  
- `src/duckalog/dashboard/state.py` - **MINOR ADDITIONS**
  - Add export methods (to_csv, to_parquet)
  - Add query result pagination helpers
  
- `pyproject.toml` - **BREAKING CHANGE**
  - Update `[ui]` extra to require: `starhtml`, `starui`, `datastar-python`
  - Remove optional fallback behavior

### Migration Path
**For users with `duckalog[ui]` already installed:**
- Upgrade will pull in new required dependencies automatically
- No code changes needed (Python API unchanged)
- UI will look different but functionality preserved

**For users without UI extra:**
- No impact - UI remains optional
- Must explicitly install `duckalog[ui]` to use dashboard

### Breaking Changes
- **BREAKING**: The `[ui]` extra now requires `starui` and `datastar-python` (previously optional with fallback)
- **Non-breaking**: Python API (`run_dashboard()`) signature unchanged
- **Non-breaking**: CLI interface unchanged
- **Non-breaking**: All existing features preserved, just enhanced

### Testing Impact
- Update `tests/test_dashboard.py` to verify new components render
- Add tests for SSE streaming endpoints
- Add tests for export functionality
- No changes needed to non-UI tests

### Documentation Impact
- Update dashboard documentation with screenshots of new UI
- Document keyboard shortcuts and new features
- Add deployment guide for production use
- Update security documentation (read-only SQL, localhost binding)

## Estimated Effort
- **Phase 1** (Foundation): 4-5 hours
- **Phase 2** (Real-time features): 4-5 hours  
- **Phase 3** (Enhancements): 4-5 hours
- **Phase 4** (Advanced features): 3-4 hours
- **Total**: 15-19 hours (2-3 focused development days)

## Success Criteria
1. ✅ All existing dashboard tests pass
2. ✅ New UI components render correctly in all pages
3. ✅ Query execution streams results in real-time
4. ✅ Build status updates without page refresh
5. ✅ Export functionality works for CSV and Parquet
6. ✅ Visual query builder generates valid SQL
7. ✅ Responsive design works on desktop and mobile
8. ✅ No console errors or warnings in browser
9. ✅ Documentation updated with new features
10. ✅ `openspec validate --strict` passes
