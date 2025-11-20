# Change: Harden UI query handling and config writes

## Why
The current Datastar UI still allows arbitrary SQL and unsafe identifier handling, rewrites YAML configs as JSON without reloads, blocks the event loop with DuckDB work, and ships a dead Datastar fallback plus wide‑open CORS. This leaves users exposed to injection, stale in‑memory config, frozen UIs, and supply‑chain/CSRF risks even on localhost.

## What Changes
- Enforce read‑only, single‑statement SQL execution with identifier quoting/parameterization for view‑driven queries and exports
- Preserve YAML/JSON formatting and reload in‑memory config after successful writes
- Move DuckDB/catalog operations off the event loop to avoid UI stalls
- Make Datastar the single dashboard path (remove dead fallback) and actually use the Python SDK for UI updates/streams
- Default CORS to a localhost/same‑origin allow‑list and disable credentials unless explicitly configured

## Impact
- Affected specs: web-ui
- Affected code: `src/duckalog/ui.py` (UI endpoints, dashboard), config persistence helpers, Datastar integration points, CORS setup
- Related work: overlaps with `secure-and-simplify-ui`; this change is narrower and focuses on correctness/safety without removing endpoints
