# Design: Examples for SQL Files and Templates

## Goals
- Provide a runnable example that demonstrates how to:
  - Use `sql_file` to source SQL from external files.
  - Use `sql_template` with per-view variables defined in `catalog.yaml`.
  - Run end-to-end from data generation to validation.
- Keep the example aligned with the `add-sql-files-and-templates` behavior and the examples specification.

## Example Shape

### Domain
- Use a simple, familiar domain such as **users and orders**:
  - `users` table: basic user attributes.
  - `orders` table: user orders with amounts and regions.
- This allows straightforward queries like "active users" and "regional sales over N days".

### Catalog Structure
- `catalog.yaml` will define views such as:
  - `users`: inline SQL (baseline).
  - `active_users`: uses `sql_file` pointing to `sql/active_users.sql`.
  - `regional_sales_last_30_days` and `regional_sales_last_7_days_na`: use `sql_template` pointing to `sql/regional_sales.sql` with different `variables`.
- The catalog will be loaded with `load_sql_files=True` so that external SQL is inlined before SQL generation.

### Files and Layout
The example directory will follow the examples spec:
- `README.md`: business context, instructions, and explanation of `sql_file`/`sql_template` usage.
- `catalog.yaml`: main Duckalog configuration using inline SQL, `sql_file`, and `sql_template`.
- `data/generate.py`: deterministic generator for `users` and `orders` tables.
- `validate.py`: script that loads the config, builds the catalog, and runs validation queries.
- `sql/active_users.sql`: plain SQL file.
- `sql/regional_sales.sql`: template using `{{variable}}` placeholders.

## Loader Interaction
- The example will explicitly mention that callers should use `load_config(..., load_sql_files=True)` so that:
  - `sql_file` content is read and inlined into `view.sql`.
  - `sql_template` content is rendered using per-view `variables` and inlined into `view.sql`.
- Validation will confirm that the resulting views behave as expected when built and queried.

## Alignment with Specs
- The example is designed to satisfy both:
  - `add-sql-files-and-templates` (behavior of `sql_file`/`sql_template`).
  - `examples` spec (standard directory structure, README contents, validation patterns).

## Open Questions
- Should this example live in an "intermediate" or "advanced features" category in the examples index?
- Do we want a variant that also demonstrates remote configs and remote SQL files, or keep that for a future change?
