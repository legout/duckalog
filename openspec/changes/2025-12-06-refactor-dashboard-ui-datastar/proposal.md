# Change: Refactor Dashboard UI with Datastar and Modern Components

## Why

The current dashboard implementation at `src/duckalog/dashboard/` is non-functional and produces an unsatisfactory user experience due to several critical issues:

1. **Missing Core Dependencies**: The dashboard attempts to use `starhtml` and `starui` libraries that are not installed, falling back to a minimal 180-line HTML element implementation that generates unstyled, basic HTML.

2. **No Styling**: The dashboard produces barebones HTML with no CSS framework, no component library, and no modern UI patterns, resulting in a plain, unprofessional appearance.

3. **Datastar Not Integrated**: While `datastar.js` is vendored in the static files, it is not referenced in the generated HTML and the dashboard provides no reactivity or real-time updates despite having the infrastructure for it.

4. **CLI Command Disabled**: The `duckalog ui` command is commented out in `cli.py`, making the dashboard inaccessible to users via the command line.

5. **Tech Stack Mismatch**: The codebase references dependencies (`starhtml`, `starui`) that don't align with the intended architecture and are not properly integrated.

This change will modernize the dashboard to provide:
- A functional, accessible UI for inspecting DuckDB catalogs
- Real-time updates via Datastar for query results and build status
- Modern, responsive design with proper component architecture
- Seamless integration with the existing Duckalog catalog engine

## What Changes

### Core Architecture
- **Framework Migration**: Refactor from the current broken Starlette implementation to **Litestar** for better async support, built-in dependency injection, and improved performance.
- **HTML Templating**: Replace the custom HTML fallback with **h2py** for Pythonic, type-safe HTML generation that integrates naturally with Datastar.
- **Component Library**: Integrate **starui** components designed specifically for the Datastar ecosystem, providing modern, accessible UI primitives.
- **Reactivity Layer**: Properly integrate **datastar-python** SDK for server-sent events, signal-based state management, and real-time DOM updates.

### Implementation Details
- **New Dashboard Structure**:
  ```
  src/duckalog/dashboard/
  ├── __init__.py
  ├── app.py              # Litestar app factory
  ├── components/         # Reusable UI components
  │   ├── __init__.py
  │   ├── layout.py       # Page layout components
  │   ├── tables.py       # Data table components
  │   └── forms.py        # Form and input components
  ├── routes/             # Route handlers
  │   ├── __init__.py
  │   ├── home.py         # Dashboard home
  │   ├── views.py        # View management
  │   └── query.py        # Query interface
  └── state.py            # Shared state management
  ```

- **Static File Serving**: Configure Litestar to serve CSS and JavaScript from `src/duckalog/static/`
- **Datastar Integration**:
  - Add datastar attributes to HTML elements for reactivity
  - Implement SSE endpoints for real-time updates
  - Use signal-based state for query results and build status

### User Experience Improvements
- **Visual Design**:
  - Integrate Tailwind CSS for modern, responsive styling
  - Implement dark/light theme support
  - Add consistent spacing, typography, and color scheme
  
- **Functionality**:
  - Real-time query result streaming
  - Live build status updates without page refresh
  - Interactive view search and filtering
  - Responsive design for mobile/tablet access

### CLI Restoration
- Re-enable the `duckalog ui` command in `cli.py`
- Add proper error handling for missing UI dependencies
- Provide clear installation instructions when UI extras not installed

### Dependency Updates
Update `pyproject.toml` optional dependencies:
```toml
[project.optional-dependencies]
ui = [
    "litestar>=2.0.0",
    "datastar-python>=1.0.0",
    "starui>=0.1.0",
    "uvicorn[standard]>=0.24.0",
    "python-multipart>=0.0.20",
]
```

## Impact

### Affected Specs
- `specs/dashboard-ui/spec.md` - Complete rewrite of UI requirements with new component architecture and Datastar integration

### Affected Code
- `src/duckalog/dashboard/` - Complete refactor of all dashboard files
- `src/duckalog/cli.py` - Re-enable UI command and add dependency checks
- `pyproject.toml` - Update UI dependencies
- `tests/test_dashboard.py` - Update tests for new architecture
- `tests/test_ui.py` - Update UI integration tests

### Breaking Changes
- **BREAKING**: Dashboard implementation completely refactored; any external code importing from `duckalog.dashboard` may break
- **BREAKING**: UI dependencies changed from `starhtml` to `litestar` + `datastar-python`
- **Migration**: Users must reinstall UI extras: `pip install duckalog[ui]`

### User Experience Impact
- Users will have access to a functional, modern dashboard
- Real-time updates improve workflow efficiency
- Responsive design enables mobile/tablet usage
- Clear visual hierarchy improves data comprehension

## Risks and Trade-offs

### Dependency Risk
- Adding Litestar and datastar-python increases the dependency footprint
- **Mitigation**: Keep dependencies in optional `[ui]` group; core functionality unaffected

### Migration Complexity
- Complete rewrite may introduce temporary bugs
- **Mitigation**: Comprehensive test coverage, phased rollout

### Learning Curve
- Team needs to learn Litestar and Datastar patterns
- **Mitigation**: Document patterns, provide examples, reference architecture

### Alternative Considered: Minimal Fix
- Could have kept Starlette and just added basic CSS
- **Rejected**: Would not address fundamental architecture issues or provide modern UX

### Performance Trade-off
- SSE connections for real-time updates consume server resources
- **Mitigation**: Implement connection limits, graceful degradation for high load

## Success Criteria

1. Dashboard loads without errors on `duckalog ui` command
2. All routes respond correctly (home, views, query)
3. Real-time updates work via Datastar SSE
4. Mobile-responsive design with Lighthouse score > 90
5. Query results display within 1 second
6. Comprehensive test coverage (>90%)
