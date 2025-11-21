## ADDED Requirements

### Requirement: Serve Datastar assets locally
The dashboard MUST load Datastar from a locally served, pinned bundle to avoid external CDN dependencies.

#### Scenario: Dashboard works offline with pinned Datastar
- **WHEN** the UI is started without internet access
- **THEN** the dashboard still loads the Datastar script from a local path served by the backend
- **AND** the served script uses a pinned version (no RC/unpinned CDN URLs)
- **AND** Content-Type for the asset is set correctly for browsers to execute it.
