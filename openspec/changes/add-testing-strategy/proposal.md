## Why

The PRD defines a testing strategy for config loading, SQL generation, and the engine, but this guidance is not yet captured in OpenSpec.
Without a spec-backed testing strategy, it is harder to ensure consistent coverage, offline-friendly tests, and alignment between implementation and product expectations.

## What Changes

- Introduce a `testing-strategy` capability spec that defines:
  - Minimum expected unit test coverage for config, SQL generation, and engine behavior.
  - Expectations for integration tests using temporary DuckDB files and lightweight attachment fixtures.
  - Offline-friendly and deterministic testing constraints (no network or external services by default).
- Clarify which behaviors MUST be covered by tests when adding or changing capabilities (e.g., new source types or CLI behaviors).

## Impact

- Provides a shared contract for how new features and changes should be tested.
- Encourages reliable, deterministic tests that match the PRD’s expectations (config, sqlgen, engine, env interpolation).
- Makes it easier to maintain quality over time as new capabilities are added.

