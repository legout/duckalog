## 1. Config schema and validation
- [x] 1.1 Add a `DuckalogAttachment` model (alias, config_path, optional database override, read_only default true) under `attachments`.
- [x] 1.2 Extend path resolution to handle nested config paths and optional database override relative to the parent config file.
- [x] 1.3 Validate that attached configs point to resolvable files and to a durable database path (nested config `duckdb.database` or override) rather than `:memory:`.

## 2. Engine build + attach behavior
- [x] 2.1 Add recursive build step that loads/builds attached Duckalog configs before creating attachments on the parent connection.
- [x] 2.2 Attach built child catalogs using the configured alias and read_only flag; reuse builds when the same child config is referenced multiple times.
- [x] 2.3 Detect cyclic attachment graphs and surface a clear error before executing any build steps.

## 3. Tooling, docs, and tests
- [x] 3.1 Add config validation and path-resolution tests for `attachments.duckalog`.
- [x] 3.2 Add engine integration tests covering nested builds, reuse, dry-run behavior, and cycle failures.
- [x] 3.3 Update CLI help/docs/examples to demonstrate hierarchical config attachments.
