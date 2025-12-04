## ADDED Requirements

### Requirement: Example for SQL Files and Templates
The examples library MUST include at least one runnable example that demonstrates using `sql_file` and `sql_template` in Duckalog catalogs.

#### Scenario: Example structure for external SQL
- **GIVEN** the examples directory
- **WHEN** a user inspects the example for SQL files and templates
- **THEN** they SHALL find an example directory that follows the standardized structure:
  - `README.md` describing the business context and explaining `sql_file` and `sql_template` usage
  - `catalog.yaml` defining at least one inline SQL view, one `sql_file`-based view, and one or more `sql_template`-based views
  - `data/generate.py` that produces deterministic synthetic data for the example
  - `validate.py` that validates the example end-to-end
  - a `sql/` subdirectory containing the SQL and template files referenced from `catalog.yaml`.

#### Scenario: Example demonstrates per-view template variables
- **GIVEN** the example catalog demonstrating SQL templates
- **WHEN** a user opens `catalog.yaml`
- **THEN** they SHALL see one or more views that use `sql_template` with a `variables` mapping
- **AND** the corresponding template file SHALL use `{{variable}}` placeholders consistent with the configuration
- **AND** the `README.md` SHALL explain how these variables are defined and substituted during config loading.

#### Scenario: Example validation covers external SQL behavior
- **GIVEN** the example validation script
- **WHEN** the user runs the example's validation step
- **THEN** the script SHALL:
  - Load the catalog using `load_config(..., load_sql_files=True)`
  - Build or open a DuckDB catalog database
  - Query the views defined via `sql_file` and `sql_template`
  - Assert that the results match the expected behavior described in the README
  - Report clear errors if SQL files or templates are misconfigured.
