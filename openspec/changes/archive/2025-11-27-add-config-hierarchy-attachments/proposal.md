# Change: Add hierarchical Duckalog config attachments

## Why
Users want to compose catalogs from reusable Duckalog configs or prebuilt DuckDB catalogs without duplicating definitions. The current attachment feature only accepts database connection parameters, so parent configs cannot trigger building and attaching child configs automatically.

## What Changes
- Add a new `attachments.duckalog[]` entry type that points to another Duckalog config, with alias, config path, optional database override, and read-only flag.
- During catalog build, build each attached Duckalog config first, then attach its resulting DuckDB file to the parent connection with the configured alias.
- Detect and fail on cyclic attachment graphs; resolve config and database paths relative to the parent config location.
- Update validation, CLI/docs, and tests to cover hierarchical builds and attachment reuse.

## Impact
- Affected specs: `config`, `catalog-build`.
- Affected code: config models/path resolution, engine build/attach pipeline, CLI messaging, tests/docs for hierarchical catalogs.
