## 1. Implementation

- [ ] 1.1 Confirm framework and libraries for the dashboard (Starlette, StarUI, BasecoatUI, Datastar + datastar-python, h2py/rustytags-style HTML DSL).
- [ ] 1.2 Refactor `src/duckalog/dashboard` into clear modules (`app.py`, `state.py`, `html.py`, `datastar.py`).
- [ ] 1.3 Implement a base layout that:
  - [ ] 1.3.1 Uses StarUI components and BasecoatUI-compatible classes.
  - [ ] 1.3.2 Includes the local Datastar bundle (`/static/datastar.js`) in all dashboard pages.
- [ ] 1.4 Implement Datastar integration:
  - [ ] 1.4.1 Define server-side signals for catalog summary, views listing, query state, and build status.
  - [ ] 1.4.2 Add a Starlette SSE endpoint that streams Datastar events using datastar-python helpers.
  - [ ] 1.4.3 Wire Datastar attributes (`data-*`) into the HTML DSL for buttons, links, and forms.
- [ ] 1.5 Implement dashboard views:
  - [ ] 1.5.1 Home/overview page with metrics cards and build controls.
  - [ ] 1.5.2 Views listing with search and navigation to view detail.
  - [ ] 1.5.3 View detail page showing view definition and semantic-layer metadata.
  - [ ] 1.5.4 Query page with textarea and Datastar-driven results panel.
- [ ] 1.6 Harden backend behavior:
  - [ ] 1.6.1 Enforce read-only (`SELECT`-only) queries in the dashboard query endpoint.
  - [ ] 1.6.2 Ensure consistent row limiting and truncation messaging.
  - [ ] 1.6.3 Improve error reporting for build and query operations for UI consumption.
- [ ] 1.7 Implement or re-enable `duckalog ui` in `src/duckalog/cli.py` to launch the dashboard with host/port/row-limit options.

## 2. Testing

- [ ] 2.1 Update or add tests for the Starlette dashboard routes (home, views, view detail, query).
- [ ] 2.2 Add tests verifying that `/static/datastar.js` is served locally and referenced in dashboard HTML.
- [ ] 2.3 Add tests for Datastar integration:
  - [ ] 2.3.1 Presence of Datastar-related attributes (`data-*`) in rendered HTML.
  - [ ] 2.3.2 SSE endpoint returns well-formed Datastar events.
- [ ] 2.4 Add tests for query behavior:
  - [ ] 2.4.1 Read-only enforcement (reject DDL/DML).
  - [ ] 2.4.2 Row limit and truncation messaging.
  - [ ] 2.4.3 Clear error messages for invalid SQL or missing views.
- [ ] 2.5 Add tests for build behavior:
  - [ ] 2.5.1 Successful builds update summary/build-status signals.
  - [ ] 2.5.2 Failed builds surface friendly error messages without breaking the UI.
- [ ] 2.6 Add tests for `duckalog ui` CLI:
  - [ ] 2.6.1 Launches dashboard with a given config path.
  - [ ] 2.6.2 Prints the expected URL and warnings for non-loopback hosts.

## 3. Documentation

- [ ] 3.1 Verify that the `ui-dashboard` guide matches the new behavior and screenshots/layout.
- [ ] 3.2 Update documentation to explicitly mention the chosen stack:
  - Starlette, StarUI, BasecoatUI, Datastar, datastar-python, and h2py/rustytags-style HTML.
- [ ] 3.3 Document read-only query behavior and row limiting for the dashboard.
- [ ] 3.4 Ensure CLI docs for `duckalog ui` are accurate and include example usage.

