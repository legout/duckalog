## 1. Implementation
- [ ] 1.1 Add Datastar signal updates when build status changes (start/progress/complete/error)
- [ ] 1.2 Replace raw EventSource JS with Datastar-driven build status widget
- [ ] 1.3 Add retry/backoff handling for build status stream
- [ ] 1.4 Wire shutdown/cleanup of build SSE

## 2. Testing
- [ ] 2.1 SSE test: initial status + progress patch arrives
- [ ] 2.2 Error case emits status=error and message

## 3. Documentation
- [ ] 3.1 Update dashboard docs for build status behavior
