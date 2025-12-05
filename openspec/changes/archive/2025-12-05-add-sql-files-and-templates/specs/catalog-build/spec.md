## ADDED Requirements

### Requirement: External SQL Sources in Catalog Builds
Catalog builds MUST treat SQL loaded from external files or templates as equivalent to inline SQL, once configuration loading has inlined the SQL content.

#### Scenario: Catalog build with sql_file-based views
- **GIVEN** a config where one or more views declare `sql_file` references
- **AND** the config is loaded with `load_sql_files=True` so that SQL from those files is inlined into `view.sql`
- **WHEN** a catalog build is executed via the CLI or Python API
- **THEN** the generated `CREATE OR REPLACE VIEW` statements for those views SHALL use the inlined SQL body
- **AND** the resulting DuckDB catalog SHALL behave as if the same SQL had been provided inline in the original config.

#### Scenario: Catalog build with sql_template-based views
- **GIVEN** a config where one or more views declare `sql_template` references with `variables`
- **AND** the config is loaded with `load_sql_files=True` so that templates are rendered and inlined into `view.sql`
- **WHEN** a catalog build is executed via the CLI or Python API
- **THEN** the generated `CREATE OR REPLACE VIEW` statements for those views SHALL use the rendered SQL bodies
- **AND** the resulting DuckDB catalog SHALL behave as if the rendered SQL had been specified inline in the original config.
