## 1. Implementation
- [x] Pin a specific Datastar bundle version and vendor it (or fetch at build time) into the package for local serving
- [x] Serve the bundled asset via Starlette static routing and update dashboard HTML to use the local path
- [x] Keep SSE/Datastar Python SDK integration intact after asset switch

## 2. Testing
- [x] Add tests that the dashboard loads without external network access and serves the Datastar script locally
- [x] Verify correct Content-Type for the bundled asset

## 3. Documentation
- [x] Document the pinned Datastar version and local-asset behavior, including how to update the bundle when needed
- [x] Note offline support and removal of CDN dependency
