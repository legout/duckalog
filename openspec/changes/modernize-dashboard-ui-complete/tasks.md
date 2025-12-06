# Tasks: Complete Dashboard Modernization

## 1. Foundation & Dependencies

- [ ] 1.1 Update `pyproject.toml` `[ui]` extra with required dependencies
  - [ ] 1.1.1 Add `starhtml>=0.1.0`
  - [ ] 1.1.2 Add `starui>=0.1.8`
  - [ ] 1.1.3 Add `datastar-python>=0.1.0`
  - [ ] 1.1.4 Keep existing: `starlette>=0.27.0`, `uvicorn[standard]>=0.24.0`
  - [ ] 1.1.5 Keep existing: `pyarrow>=10.0.0`, `pandas>=1.5.0` (for export)
  - [ ] 1.1.6 Add `python-multipart>=0.0.20` if not present (for form handling)

- [ ] 1.2 Create component module structure
  - [ ] 1.2.1 Create `src/duckalog/dashboard/components/__init__.py`
  - [ ] 1.2.2 Create `src/duckalog/dashboard/components/layout.py`
  - [ ] 1.2.3 Create `src/duckalog/dashboard/components/tables.py`
  - [ ] 1.2.4 Create `src/duckalog/dashboard/components/query_editor.py`
  - [ ] 1.2.5 Create `src/duckalog/dashboard/components/query_builder.py`

- [ ] 1.3 Move and organize static assets
  - [ ] 1.3.1 Move `src/duckalog/static/datastar.js` to `src/duckalog/dashboard/static/datastar.js`
  - [ ] 1.3.2 Create `src/duckalog/dashboard/static/themes.css` (optional custom styles)
  - [ ] 1.3.3 Update static file serving in `app.py` if needed

## 2. Base Layout Component

- [ ] 2.1 Implement base layout in `components/layout.py`
  - [ ] 2.1.1 Create `base_page()` function with HTML structure
  - [ ] 2.1.2 Add CDN links for Tailwind CSS v4
  - [ ] 2.1.3 Add Datastar.js script tag
  - [ ] 2.1.4 Create navigation component with links to all sections
  - [ ] 2.1.5 Add responsive container with proper spacing
  - [ ] 2.1.6 Add optional toast notification container

- [ ] 2.2 Create navigation component
  - [ ] 2.2.1 Implement navbar with logo/title
  - [ ] 2.2.2 Add navigation links (Home, Views, Query, Build Status)
  - [ ] 2.2.3 Style with StarUI components
  - [ ] 2.2.4 Add active state indication
  - [ ] 2.2.5 Make responsive (collapsible on mobile)

## 3. Remove Fallback Compatibility Layer

- [ ] 3.1 Refactor `src/duckalog/dashboard/views.py`
  - [ ] 3.1.1 Remove lines 13-181 (fallback `_Elt`, `sh`, and `ui` classes)
  - [ ] 3.1.2 Update imports to use real `starhtml` and `starui`
  - [ ] 3.1.3 Verify no references to fallback classes remain
  - [ ] 3.1.4 Update type hints if needed

## 4. Refactor Existing Pages with StarUI

- [ ] 4.1 Refactor home page (`home_page()` in views.py)
  - [ ] 4.1.1 Use base_page layout
  - [ ] 4.1.2 Convert catalog summary to Card component
  - [ ] 4.1.3 Use Badge for counts
  - [ ] 4.1.4 Use Button components for navigation and actions
  - [ ] 4.1.5 Add build status indicator with Alert component
  - [ ] 4.1.6 Test rendering and navigation

- [ ] 4.2 Refactor views list page (`views_page()` in views.py)
  - [ ] 4.2.1 Use base_page layout
  - [ ] 4.2.2 Convert table to StarUI Table component
  - [ ] 4.2.3 Add search input with Datastar `data-bind`
  - [ ] 4.2.4 Add Badge for semantic layer indicator
  - [ ] 4.2.5 Implement client-side filtering with Datastar signals
  - [ ] 4.2.6 Add pagination controls
  - [ ] 4.2.7 Test search and filtering

- [ ] 4.3 Refactor view detail page (`view_detail_page()` in views.py)
  - [ ] 4.3.1 Use base_page layout
  - [ ] 4.3.2 Use Card for view definition
  - [ ] 4.3.3 Add syntax highlighting for SQL (use Code component or highlight.js)
  - [ ] 4.3.4 Use separate Card for semantic layer info
  - [ ] 4.3.5 Add tabs for different sections (Definition, Schema, Semantic)
  - [ ] 4.3.6 Test with views that have/don't have semantic models

- [ ] 4.4 Refactor query page (`query_page()` in views.py)
  - [ ] 4.4.1 Use base_page layout
  - [ ] 4.4.2 Create query editor component with syntax highlighting
  - [ ] 4.4.3 Add Button components for actions (Run, Clear, Export)
  - [ ] 4.4.4 Convert results table to Table component
  - [ ] 4.4.5 Add loading state indicator
  - [ ] 4.4.6 Add error Alert component for query errors
  - [ ] 4.4.7 Add truncation indicator when results are limited
  - [ ] 4.4.8 Test with various query types

## 5. Real-time Query Execution with Datastar

- [ ] 5.1 Add SSE endpoint for query streaming in `app.py`
  - [ ] 5.1.1 Create `POST /query-stream` endpoint
  - [ ] 5.1.2 Import datastar_py SSE and DatastarResponse
  - [ ] 5.1.3 Implement async generator for streaming results
  - [ ] 5.1.4 Stream table rows in chunks (100 rows per chunk)
  - [ ] 5.1.5 Handle errors gracefully in stream
  - [ ] 5.1.6 Add completion signal when done

- [ ] 5.2 Update query page to use SSE
  - [ ] 5.2.1 Add Datastar `data-on:submit` to form
  - [ ] 5.2.2 Add loading indicator with `data-indicator`
  - [ ] 5.2.3 Add results container with ID for SSE patches
  - [ ] 5.2.4 Update UI to show progress during streaming
  - [ ] 5.2.5 Test with small and large result sets
  - [ ] 5.2.6 Test error handling

## 6. Real-time Build Status

- [ ] 6.1 Add SSE endpoint for build status in `app.py`
  - [ ] 6.1.1 Create `GET /build-status` endpoint
  - [ ] 6.1.2 Stream build status updates
  - [ ] 6.1.3 Send completion signal when build finishes
  - [ ] 6.1.4 Handle build errors in stream

- [ ] 6.2 Update home page with real-time build status
  - [ ] 6.2.1 Add Datastar `data-on:load` to fetch status
  - [ ] 6.2.2 Add status indicator that updates via SSE
  - [ ] 6.2.3 Show build progress (if possible)
  - [ ] 6.2.4 Update button state during build
  - [ ] 6.2.5 Test build trigger and status updates

## 7. Query History

- [ ] 7.1 Implement query history component
  - [ ] 7.1.1 Create history panel in query_editor.py
  - [ ] 7.1.2 Add localStorage save/load functions (Datastar signals)
  - [ ] 7.1.3 Store last 20 queries with timestamp
  - [ ] 7.1.4 Add UI to view history
  - [ ] 7.1.5 Add click handlers to load query from history
  - [ ] 7.1.6 Add clear history button
  - [ ] 7.1.7 Test persistence across page reloads

## 8. Data Export

- [ ] 8.1 Implement CSV export (client-side)
  - [ ] 8.1.1 Add "Export CSV" button to query results
  - [ ] 8.1.2 Implement JavaScript function to convert table to CSV
  - [ ] 8.1.3 Trigger browser download
  - [ ] 8.1.4 Limit to 10,000 rows with warning
  - [ ] 8.1.5 Test with various data types

- [ ] 8.2 Implement Parquet export (server-side)
  - [ ] 8.2.1 Add `GET /export/parquet` endpoint in `app.py`
  - [ ] 8.2.2 Accept SQL query as parameter
  - [ ] 8.2.3 Use DuckDB COPY command to generate Parquet file
  - [ ] 8.2.4 Return FileResponse with Parquet file
  - [ ] 8.2.5 Clean up temp files
  - [ ] 8.2.6 Limit to 1,000,000 rows with warning
  - [ ] 8.2.7 Add "Export Parquet" button to query results
  - [ ] 8.2.8 Test with various data types and sizes

- [ ] 8.3 Add export methods to `state.py`
  - [ ] 8.3.1 Create `export_to_parquet(sql: str, path: str)` method
  - [ ] 8.3.2 Create `get_export_formats()` helper
  - [ ] 8.3.3 Add error handling for export limits

## 9. Syntax Highlighting

- [ ] 9.1 Add syntax highlighting library
  - [ ] 9.1.1 Choose library (Highlight.js or Prism.js)
  - [ ] 9.1.2 Add CDN link to base layout
  - [ ] 9.1.3 Configure for SQL syntax

- [ ] 9.2 Apply syntax highlighting
  - [ ] 9.2.1 Update query editor to use highlighting
  - [ ] 9.2.2 Apply to view detail page SQL display
  - [ ] 9.2.3 Add line numbers option
  - [ ] 9.2.4 Test with complex SQL queries

## 10. Visual Query Builder

- [ ] 10.1 Create query builder UI in `components/query_builder.py`
  - [ ] 10.1.1 Create view selection dropdown (populated from ctx.view_list())
  - [ ] 10.1.2 Create column selection checkboxes (loaded via AJAX when view selected)
  - [ ] 10.1.3 Create filter builder UI (column, operator, value inputs)
  - [ ] 10.1.4 Add "Add Filter" button
  - [ ] 10.1.5 Create SQL preview panel
  - [ ] 10.1.6 Add "Copy SQL" and "Run Query" buttons

- [ ] 10.2 Add query builder API endpoints in `app.py`
  - [ ] 10.2.1 Create `GET /query-builder/views` endpoint (return view list)
  - [ ] 10.2.2 Create `GET /query-builder/columns/<view>` endpoint (return columns)
  - [ ] 10.2.3 Create `POST /query-builder/generate` endpoint (generate SQL)
  - [ ] 10.2.4 Validate inputs and sanitize generated SQL

- [ ] 10.3 Integrate query builder with query page
  - [ ] 10.3.1 Add tab or drawer to switch between editor and builder
  - [ ] 10.3.2 Connect builder to query execution
  - [ ] 10.3.3 Allow copying generated SQL to editor
  - [ ] 10.3.4 Test complete flow

## 11. Responsive Design & UX Polish

- [ ] 11.1 Responsive design
  - [ ] 11.1.1 Test all pages on mobile viewports
  - [ ] 11.1.2 Add responsive table scrolling
  - [ ] 11.1.3 Make navigation collapsible on mobile
  - [ ] 11.1.4 Adjust card layouts for small screens
  - [ ] 11.1.5 Test on actual mobile devices

- [ ] 11.2 Loading states
  - [ ] 11.2.1 Add spinners for all async operations
  - [ ] 11.2.2 Disable buttons during operations
  - [ ] 11.2.3 Show progress indicators where applicable
  - [ ] 11.2.4 Add skeleton loaders for content

- [ ] 11.3 Error handling
  - [ ] 11.3.1 Style all error messages with Alert component
  - [ ] 11.3.2 Add helpful context to error messages
  - [ ] 11.3.3 Add retry buttons where appropriate
  - [ ] 11.3.4 Test error scenarios

- [ ] 11.4 Keyboard shortcuts
  - [ ] 11.4.1 Add Ctrl/Cmd+Enter to run query
  - [ ] 11.4.2 Add Ctrl/Cmd+K to focus search
  - [ ] 11.4.3 Add Esc to close modals/drawers
  - [ ] 11.4.4 Document shortcuts in UI

## 12. Testing

- [ ] 12.1 Update existing tests
  - [ ] 12.1.1 Update `tests/test_dashboard.py` for new component rendering
  - [ ] 12.1.2 Fix any broken assertions from UI changes
  - [ ] 12.1.3 Ensure all existing routes still work

- [ ] 12.2 Add new tests
  - [ ] 12.2.1 Test SSE query streaming endpoint
  - [ ] 12.2.2 Test build status streaming endpoint
  - [ ] 12.2.3 Test CSV export functionality
  - [ ] 12.2.4 Test Parquet export endpoint
  - [ ] 12.2.5 Test query builder SQL generation
  - [ ] 12.2.6 Test query builder validation

- [ ] 12.3 Integration tests
  - [ ] 12.3.1 Test complete query execution flow
  - [ ] 12.3.2 Test complete build trigger flow
  - [ ] 12.3.3 Test export with real data
  - [ ] 12.3.4 Test error scenarios

## 13. Documentation

- [ ] 13.1 Update dashboard documentation
  - [ ] 13.1.1 Add screenshots of new UI
  - [ ] 13.1.2 Document all features (query history, export, builder)
  - [ ] 13.1.3 Document keyboard shortcuts
  - [ ] 13.1.4 Update installation instructions
  - [ ] 13.1.5 Add troubleshooting section

- [ ] 13.2 Update API documentation
  - [ ] 13.2.1 Document `run_dashboard()` parameters
  - [ ] 13.2.2 Document new configuration options
  - [ ] 13.2.3 Add code examples

- [ ] 13.3 Update CHANGELOG
  - [ ] 13.3.1 Document all new features
  - [ ] 13.3.2 Note breaking changes in `[ui]` extra
  - [ ] 13.3.3 Add migration guide

## 14. Cleanup & Validation

- [ ] 14.1 Code cleanup
  - [ ] 14.1.1 Remove any unused imports
  - [ ] 14.1.2 Add docstrings to new functions
  - [ ] 14.1.3 Add type hints where missing
  - [ ] 14.1.4 Format code with ruff

- [ ] 14.2 Final validation
  - [ ] 14.2.1 Run `openspec validate modernize-dashboard-ui-complete --strict`
  - [ ] 14.2.2 Run all tests: `pytest tests/test_dashboard.py -v`
  - [ ] 14.2.3 Manual testing of all features
  - [ ] 14.2.4 Check browser console for errors
  - [ ] 14.2.5 Verify no console warnings
  - [ ] 14.2.6 Test with JavaScript disabled (graceful degradation)

## 15. Deployment Preparation

- [ ] 15.1 Version bump
  - [ ] 15.1.1 Update version in `pyproject.toml` (0.4.x → 0.5.0 for breaking change)
  - [ ] 15.1.2 Update `__init__.py` version if needed

- [ ] 15.2 Build and test package
  - [ ] 15.2.1 Build package: `python -m build`
  - [ ] 15.2.2 Test installation in fresh virtualenv
  - [ ] 15.2.3 Verify `duckalog[ui]` installs all dependencies

- [ ] 15.3 Final checks
  - [ ] 15.3.1 Review all changed files
  - [ ] 15.3.2 Ensure CHANGELOG is complete
  - [ ] 15.3.3 Ensure documentation is up to date
  - [ ] 15.3.4 Run final validation: `openspec validate --strict`
