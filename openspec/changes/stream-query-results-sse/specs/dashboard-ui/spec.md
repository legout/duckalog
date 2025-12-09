## MODIFIED Requirements

### Requirement: Query Runner with Streaming and Limits
The dashboard SHALL provide a read-only query runner with streaming results and guardrails.

#### Scenario: Query submission and streaming
- **WHEN** a SELECT query is submitted
- **THEN** results stream via SSE in batches using Datastar patch events
- **AND** rows render progressively in the table as batches arrive
- **AND** blocking DuckDB work is offloaded from the event loop so the UI remains responsive.

#### Scenario: Row limit and truncation
- **WHEN** a query returns more than the configured row limit (default 500; configurable via CLI and UI)
- **THEN** only the allowed rows are delivered
- **AND** the UI indicates results were truncated.

#### Scenario: Timeout and cancellation
- **WHEN** a query exceeds the max execution time or the client disconnects
- **THEN** execution is cancelled and the user sees a timeout/cancel notice.

#### Scenario: Error handling
- **WHEN** a query fails validation or execution
- **THEN** the error message is surfaced clearly without exposing internal stack traces.
