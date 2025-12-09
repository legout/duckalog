# Change: Improve build status streaming with Datastar

## Why
Current dashboard wires build status via a raw `EventSource` and never emits Datastar patch events when status changes, so indicators never update during a build. We need a Datastar-first flow that streams status/progress as signals.

## What Changes
- Emit build status updates as Datastar SSE patches whenever `_build_status` mutates.
- Replace manual EventSource script with Datastar attributes on the build status widget.
- Add heartbeat/backoff handling via Datastar signals.
- Update docs/tests for build status streaming.

## Impact
- Specs: `dashboard-ui`
- Code: `src/duckalog/dashboard/routes/query.py`, `components/layout.py`
- Tests: add/adjust SSE build tests
