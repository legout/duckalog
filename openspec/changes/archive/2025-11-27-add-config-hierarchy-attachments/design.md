## Context
Users want to compose catalogs from smaller Duckalog configs or existing DuckDB files by declaring them as attachments. Today attachments only cover DuckDB/SQLite/Postgres connection parameters; there is no way to tell Duckalog to first build another config and then attach its resulting catalog.

## Goals / Non-Goals
- Goals: allow a parent config to reference another Duckalog config, build it automatically, and attach the resulting DuckDB database with a chosen alias; keep behavior deterministic and safe.
- Non-Goals: introduce caching beyond single-run reuse, change view SQL generation semantics, or add new authentication backends.

## Decisions
- Config shape: add `attachments.duckalog[]` entries with `alias`, `config_path`, optional `database` override, and `read_only` (default true) to mirror DuckDB attachment safety.
- Path resolution: resolve `config_path` and `database` override relative to the parent config file, reusing existing attachment path resolution utilities.
- Build order: before creating attachments on the parent connection, build each referenced child config (recursively) so the child's `duckdb.database` exists; attach that path using the provided alias.
- Database target: if a child config's `duckdb.database` is `:memory:`, require a `database` override on the attachment; otherwise raise a validation/build error.
- Cycle safety: track resolved config paths during recursion; if the same config is encountered in the current stack, raise a cycle error. If the same config is referenced multiple times without forming a cycle, build once and reuse the resulting path for all aliases.
- Dry-run: `generate_sql` remains scoped to a single config. For `build_catalog(..., dry_run=True)`, validate and stage child configs but skip physical builds/attachments.

## Risks / Trade-offs
- Recursion adds complexity to logging and error surfacing; mitigate with clear messages that name the attachment alias and config path.
- Large dependency graphs could increase build time; reuse-within-run reduces redundant builds but no persistent cache is planned.
- Misconfigured overrides (`database` pointing to same path as parent) could create self-attaches; rely on cycle detection plus DuckDB errors rather than blocking these outright.

## Open Questions
- Should we expose a CLI flag to force rebuild of attached configs even if their output files exist? (Default is always rebuild within current run.)
- Should `generate_sql` optionally emit SQL for child configs? Current plan is to leave it unchanged.
