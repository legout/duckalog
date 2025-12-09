## 1. Foundation Setup
- [x] 1.1 Update `pyproject.toml` UI dependencies (replace starhtml/starui with litestar/htpy/datastar-py)
- [x] 1.2 Create new dashboard directory structure (components/, routes/)
- [x] 1.3 Remove old fallback HTML implementation from views.py (N/A - dashboard was deleted, rebuilt from scratch)
- [x] 1.4 Configure Litestar app factory with static file serving
- [x] 1.5 Confirm no legacy dashboard files are restored; rebuild routes/components/state from scratch

## 2. Core Dashboard Implementation
- [x] 2.1 Implement base layout component with Tailwind CSS integration
- [x] 2.2 Create Litestar route handlers (home, views, query)
- [x] 2.3 Integrate datastar-py for SSE support
- [x] 2.4 Implement DashboardContext state management for Litestar
- [x] 2.5 Add proper HTML templates with Datastar attributes

## 3. Datastar Integration
- [x] 3.1 Add signal-based state management for query results
- [x] 3.2 Implement SSE endpoint for real-time build status updates
- [x] 3.3 Add reactive view search with Datastar signals
- [x] 3.4 Implement streaming query results via server-sent events
- [x] 3.5 Configure datastar.js bundle serving from static files

## 4. UI Components
- [x] 4.1 Create layout components (header, navigation, footer)
- [x] 4.2 Implement table component with htpy for view listings
- [x] 4.3 Build query form component with real-time feedback
- [x] 4.4 Add card components for dashboard metrics
- [x] 4.5 Implement responsive navigation with mobile support

## 5. Styling and Theming
- [x] 5.1 Integrate Tailwind CSS for utility-first styling
- [x] 5.2 Add Basecoat CSS for component styling
- [x] 5.3 Implement dark/light theme toggle
- [x] 5.4 Add responsive design breakpoints
- [x] 5.5 Create consistent color scheme and typography

## 6. CLI Integration
- [x] 6.1 Re-enable `duckalog ui` command in cli.py
- [x] 6.2 Add dependency check with clear error messages
- [x] 6.3 Implement proper CLI options (host, port, row-limit, db)
- [x] 6.4 Add startup messages and server information
- [x] 6.5 Handle graceful shutdown on Ctrl+C (handled by uvicorn)

## 7. Testing
- [x] 7.1 Update test_dashboard.py for Litestar implementation
- [x] 7.2 Add tests for Datastar SSE endpoints
- [x] 7.3 Test real-time query result streaming
- [x] 7.4 Add responsive design tests
- [x] 7.5 Test CLI command with various options
- [x] 7.6 Add integration tests for view search and filtering

## 8. Documentation
- [ ] 8.1 Update dashboard documentation with new architecture
- [ ] 8.2 Document Datastar integration patterns
- [ ] 8.3 Add UI component usage examples
- [ ] 8.4 Document CLI command options
- [ ] 8.5 Create migration guide from old dashboard
- [ ] 8.6 Add screenshots to documentation

## 9. Performance Optimization
- [ ] 9.1 Implement connection pooling for SSE
- [ ] 9.2 Add pagination for large result sets
- [ ] 9.3 Optimize static file serving with caching
- [x] 9.4 Add loading indicators for async operations
- [ ] 9.5 Implement graceful degradation for low bandwidth

## 10. Final Polish
- [x] 10.1 Add comprehensive error handling
- [ ] 10.2 Implement accessibility features (ARIA labels, keyboard navigation)
- [x] 10.3 Add user feedback for all actions
- [ ] 10.4 Test on multiple browsers and devices
- [ ] 10.5 Run Lighthouse audit and address issues
- [ ] 10.6 Final code review and cleanup
