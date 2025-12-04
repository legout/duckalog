# Proposal: Add Examples for SQL Files and Templates

## Why
The new `add-sql-files-and-templates` change introduces first-class support for `sql_file` and
`sql_template` in view definitions, but the examples library does not yet provide clear,
end-to-end examples that show how to:

- Organize catalogs that use external SQL files.
- Define SQL templates with per-view variables inside `catalog.yaml`.
- Run a full example from data generation through validation with these features.

Without curated examples, users must infer usage from specs or internal tests, which makes
adoption harder and increases the chance of misconfiguration.

## What Changes
This change will:

1. **Add a focused example for SQL files and templates**
   - Create or update an example under `examples/` that demonstrates:
     - A catalog with a mix of inline `sql`, `sql_file`, and `sql_template` views.
     - External `.sql` files for reusable queries.
     - Template variables defined per view in the YAML.
   - Include data generation and validation scripts to provide a complete, runnable flow.

2. **Align example documentation with the examples spec**
   - Ensure the example follows the standardized structure (README, catalog.yaml, data generation,
     validation) and clearly calls out the new SQL-file/template capabilities.
   - Describe how `load_config(..., load_sql_files=True)` interacts with the example.

3. **Integrate the example into learning paths**
   - Reference this example from the main docs/examples index as the canonical place to learn
     about external SQL files and templates in Duckalog.

## Out of Scope
- Changes to the core config or SQL generation behavior (covered by `add-sql-files-and-templates`).
- Additional example domains beyond the minimum needed to demonstrate `sql_file` and `sql_template`.
- Benchmarking or performance-focused examples.

## Impact
- **Onboarding**: New users can quickly see how to structure catalogs that use external SQL and
  templates without reading internal specs.
- **Discoverability**: The examples index can point directly to a concrete, runnable demo of
  `sql_file`/`sql_template` usage.
- **Quality**: Automated validation for the example helps prevent regressions in SQL-file handling
  and keeps docs aligned with actual behavior.
