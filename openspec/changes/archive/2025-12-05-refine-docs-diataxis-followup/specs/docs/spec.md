## ADDED Requirements

### Requirement: Top-Level Navigation Tabs
The documentation navigation MUST expose the main documentation sections as top-level chapters in the UI (for example via the top navigation bar), rather than hiding them only in the left sidebar.

#### Scenario: Main chapters visible in top bar
- **GIVEN** a user opens the Duckalog documentation site in a browser
- **WHEN** they look at the top navigation area
- **THEN** they see the primary documentation chapters listed as first-level entries (for example: Home, Getting Started, How-to Guides, Reference, Understanding, Examples, Legacy Guides, Security)
- **AND** selecting any of these chapters shows its contents in the left sidebar
- **SO** they can understand the overall documentation structure at a glance.

#### Scenario: Sidebar shows within-chapter navigation
- **GIVEN** a user clicks on a chapter such as "How-to Guides" or "Reference" in the top navigation
- **WHEN** the page loads
- **THEN** the left sidebar shows navigation only for that chapter’s internal pages
- **AND** the sidebar does not repeat unrelated top-level chapters
- **SO** users can focus on the current chapter while still having quick access to others from the top bar.

