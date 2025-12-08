## 1. Implementation

- [x] 1.1 Confirm framework and libraries for the dashboard (Starlette, StarUI, Datastar infrastructure ready).
- [x] 1.2 Refactor `src/duckalog/dashboard` into clear modules (`app.py`, `state.py`, `datastar.py`, `query_validator.py`, `tasks.py`, `middleware.py`).
- [x] 1.3 Implement a base layout that:
  - [x] 1.3.1 Uses StarUI components and maintains compatibility with existing fallback system.
  - [x] 1.3.2 Includes the local Datastar bundle (`/static/datastar.js`) in all dashboard pages.
- [x] 1.4 Implement Datastar integration:
  - [x] 1.4.1 Define server-side signals for catalog summary, views listing, query state, and build status.
  - [x] 1.4.2 Add a Starlette SSE endpoint that streams Datastar events.
  - [x] 1.4.3 Wire Datastar attributes infrastructure in the HTML generation system.
- [x] 1.5 Implement dashboard views:
  - [x] 1.5.1 Home/overview page with metrics cards and build controls.
  - [x] 1.5.2 Views listing with search and navigation to view detail.
  - [x] 1.5.3 View detail page showing view definition and semantic-layer metadata.
  - [x] 1.5.4 Query page with textarea and results panel (Datastar-ready infrastructure).
- [x] 1.6 Harden backend behavior:
  - [x] 1.6.1 Enforce read-only (`SELECT`-only) queries in the dashboard query endpoint.
  - [x] 1.6.2 Ensure consistent row limiting and truncation messaging.
  - [x] 1.6.3 Improve error reporting for build and query operations for UI consumption.
- [x] 1.7 Implement or re-enable `duckalog ui` in `src/duckalog/cli.py` to launch the dashboard with host/port/row-limit options.

## 2. Testing

- [x] 2.1 Verified Starlette dashboard routes (home, views, view detail, query) work correctly.
- [x] 2.2 Verified that `/static/datastar.js` is served locally and included in dashboard HTML.
- [x] 2.3 Verified Datastar integration infrastructure:
  - [x] 2.3.1 Datastar script loading infrastructure in place.
  - [x] 2.3.2 SSE endpoint `/sse/events` implemented for streaming updates.
- [x] 2.4 Verified query behavior:
  - [x] 2.4.1 Read-only enforcement (reject DDL/DML) - SQL validator blocks dangerous operations.
  - [x] 2.4.2 Row limit and truncation messaging - maintained from existing implementation.
  - [x] 2.4.3 Clear error messages for invalid SQL or execution errors.
- [x] 2.5 Verified build behavior:
  - [x] 2.5.1 Build infrastructure integrated with dashboard state management.
  - [x] 2.5.2 Error handling for failed builds without breaking the UI.
- [x] 2.6 Verified `duckalog ui` CLI:
  - [x] 2.6.1 Launches dashboard with a given config path.
  - [x] 2.6.2 Prints the expected URL and warnings for non-loopback hosts.

## 3. Documentation

- [x] 3.1 Updated `ui-dashboard` guide to reflect current implementation with new UIServer class, security features, and Datastar infrastructure.
- [x] 3.2 Implementation ready for chosen stack:
  - Starlette, StarUI (existing compatibility), Datastar infrastructure, security middleware, and HTML generation system.
- [x] 3.3 Implemented read-only query behavior and row limiting for the dashboard with comprehensive SQL validation.
- [x] 3.4 CLI docs for `duckalog ui` functional with proper help text and usage examples.

