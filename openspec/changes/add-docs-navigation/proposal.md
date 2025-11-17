## Why

The MkDocs site has example documentation pages that exist in the filesystem but are not included in the navigation configuration. Specifically, `docs/examples/duckdb-secrets.md` and `docs/examples/duckdb-settings.md` are missing from the navigation, which means users cannot easily discover and access these important examples through the documentation site.

The missing pages document:
- DuckDB Secrets: How to manage credentials for external services like S3, Azure, GCS, and databases
- DuckDB Settings: How to configure DuckDB session parameters for performance and behavior control

Both features are already implemented and documented, but not discoverable through the site navigation.

## What Changes

- Update the `mkdocs.yml` navigation configuration to include the missing example pages
- Add entries for "DuckDB Secrets" and "DuckDB Settings" under the Examples section
- Ensure consistent ordering and naming with other example pages
- Maintain the existing documentation structure and hierarchy

## Impact

- Users can now discover and access all example documentation through the site navigation
- Improves documentation completeness and user experience
- Ensures all implemented features have corresponding accessible documentation
- Resolves the MkDocs warning about pages not included in navigation configuration