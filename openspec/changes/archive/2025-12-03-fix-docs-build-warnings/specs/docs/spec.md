## MODIFIED Requirements

### Requirement: Eliminate navigation warnings
The MkDocs build process SHALL complete without warnings about pages existing in the docs directory but not included in the navigation configuration, and the navigation MUST expose all maintained core guides, examples, and API reference pages.

#### Scenario: No documentation warnings during build
- **GIVEN** a MkDocs site configuration for Duckalog
- **WHEN** `mkdocs build` or `mkdocs serve` is executed
- **THEN** there are no warnings about pages in `docs/` that are unintentionally excluded from navigation
- **AND** all maintained pages under `docs/examples/` have corresponding navigation entries (directly or via a navigable parent section)
- **AND** key guides for security, path resolution, and user usage are reachable via the documented navigation structure.

### Requirement: Example navigation completeness
The navigation configuration SHALL include entries for all maintained examples under `docs/examples/`, organized within the Examples section.

#### Scenario: User discovers examples via navigation
- **GIVEN** the user is browsing the documentation site
- **WHEN** they open the Examples section from the top navigation
- **THEN** they see navigation entries for each maintained example page (including, but not limited to, DuckDB Secrets, DuckDB Settings, environment variables, local attachments, multi-source analytics, simple parquet, and path-resolution examples)
- **AND** selecting any example entry opens the corresponding example page
- **SO** users can reliably discover and access practical examples without relying on hidden or unlinked pages.

### Requirement: API reference without documentation warnings
The generated API reference documentation SHALL build without mkdocstrings/Griffe warnings for public APIs, ensuring that all documented functions and methods have appropriate type information.

#### Scenario: API reference build is warning-free
- **GIVEN** the Python API is documented via mkdocstrings in `docs/reference/api.md`
- **WHEN** `mkdocs build` or `mkdocs serve` runs and generates the API reference
- **THEN** there are no mkdocstrings/Griffe warnings about missing type annotations for documented public functions or return values
- **AND** the generated API documentation reflects accurate signatures and types for the public API surface.

