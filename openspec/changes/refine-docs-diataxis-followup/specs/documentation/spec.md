## ADDED Requirements

### Requirement: Unified Intro and Quickstart
The project SHALL maintain a consistent high-level introduction and quickstart across `README.md` and `docs/index.md`, with a clearly defined single source of truth.

#### Scenario: README quickstart matches docs quickstart
- **GIVEN** a new user browsing the GitHub repository
- **WHEN** they read the quickstart in `README.md`
- **AND** then follow the link to the documentation homepage (`docs/index.md`)
- **THEN** they see an equivalent high-level introduction and quickstart flow (same main steps and expectations)
- **AND** there are no contradictory or obviously outdated differences between the two entry points
- **SO** they can move between README and docs without confusion.

#### Scenario: Single canonical intro snippet
- **GIVEN** a maintainer updating the introductory and quickstart text
- **WHEN** they follow the documented process for editing this content
- **THEN** they only need to update a single canonical location (for example a shared snippet or the docs index)
- **AND** the README automatically reuses or mirrors that content according to the documented policy
- **SO** the risk of the two entry points drifting out of sync is minimized.

### Requirement: Architecture Document in Explanation Section
The architecture document SHALL live under the “Explanation/Understanding” section of the documentation while remaining easy to discover from the main index.

#### Scenario: Architecture appears in Understanding section
- **GIVEN** a user navigates to the “Understanding” or “Explanation” section of the docs
- **WHEN** they scan the entries in that section
- **THEN** they find the architecture document listed there (for example as `Architecture`)
- **AND** the document URL and file path reflect that it belongs to the explanation layer (for example under `explanation/`)
- **SO** the architecture content is clearly categorized as explanation rather than a top-level miscellaneous page.

#### Scenario: Architecture discoverable from main index
- **GIVEN** a developer browsing the documentation from the homepage
- **WHEN** they look for an overview of Duckalog’s architecture
- **THEN** they can navigate to the architecture document either via the “Understanding/Explanation” section or via an obvious link from the main index
- **AND** the architecture document clearly links out to deeper design and implementation guides where applicable
- **SO** new contributors can quickly find and use the architecture documentation.

