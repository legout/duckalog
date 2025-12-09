## 1. Implementation
- [ ] 1.1 Execute DuckDB queries off the event loop (executor or background task)
- [ ] 1.2 Stream rows in batches via Datastar SSE `patch_elements`
- [ ] 1.3 Add progress/loading signals and end-of-stream signal
- [ ] 1.4 Handle read-only validation and early errors via signal patches

## 2. Testing
- [ ] 2.1 Streamed query returns rows progressively
- [ ] 2.2 Large result set is paged/batched without blocking
- [ ] 2.3 Error scenario patches `error` and stops stream

## 3. Documentation
- [ ] 3.1 Update query UX docs to note streaming behavior
