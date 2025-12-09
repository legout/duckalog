## 1. Implementation
- [x] 1.1 Add startup/shutdown hooks to open/close DB connections
- [x] 1.2 Move DuckDB work to threadpool or managed pool for concurrency
- [x] 1.3 Turn off Litestar debug by default; allow override
- [x] 1.4 Add simple `/health` or internal check

## 2. Testing
- [x] 2.1 Test graceful shutdown closes connection
- [x] 2.2 Concurrency test with parallel read queries

## 3. Documentation
- [x] 3.1 Document runtime guarantees and debug toggle
