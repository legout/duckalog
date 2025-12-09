## MODIFIED Requirements

### Requirement: Build Trigger and Status Streaming
The dashboard SHALL trigger builds and stream their status safely.

#### Scenario: Debounced build trigger
- **WHEN** a user clicks “Build catalog” repeatedly
- **THEN** only one build starts until the current build finishes or fails.

#### Scenario: Status stream
- **WHEN** a build runs
- **THEN** progress and final status stream over SSE using Datastar patch events that update `status`, `progress`, `message`, and `error` signals
- **AND** clients see live updates in the UI without custom `EventSource` wiring
- **AND** the stream includes a short failure summary and any created/updated counts when applicable.

#### Scenario: Concurrency guard
- **WHEN** a second build request arrives during an active build
- **THEN** it is rejected with an informative message.
