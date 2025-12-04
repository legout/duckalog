## 1. Example Design and Scope
- [ ] 1.1 Decide whether to extend an existing example (e.g. intermediate SQL examples) or create a new dedicated example for `sql_file`/`sql_template`.
- [ ] 1.2 Define the minimal business scenario (e.g. users and orders) to keep SQL realistic but simple.

## 2. Example Catalog and SQL Files
- [ ] 2.1 Create or update `catalog.yaml` for the example to include:
  - [ ] Inline SQL view (baseline).
  - [ ] View using `sql_file` with a plain SQL file.
  - [ ] Two or more views using `sql_template` with different `variables` mappings.
- [ ] 2.2 Add corresponding `.sql` files under a `sql/` subdirectory.
  - [ ] Plain SQL file used via `sql_file`.
  - [ ] Template SQL file using `{{variable}}` placeholders consistent with the `add-sql-files-and-templates` spec.

## 3. Data Generation and Validation
- [ ] 3.1 Implement or update `data/generate.py` to produce deterministic synthetic data required by the example views.
- [ ] 3.2 Implement or update `validate.py` to:
  - [ ] Load the catalog with `load_sql_files=True`.
  - [ ] Build a DuckDB catalog and run one or more queries against the views.
  - [ ] Assert that the views defined via `sql_file` and `sql_template` behave as expected.

## 4. Documentation and Indexing
- [ ] 4.1 Write or update `README.md` for the example to:
  - [ ] Explain the business context and what the example demonstrates.
  - [ ] Show how `sql_file` and `sql_template` are defined in `catalog.yaml`.
  - [ ] Provide step-by-step instructions to run data generation, catalog build, and validation.
- [ ] 4.2 Integrate the example into the examples index / docs so it is discoverable as the canonical reference for SQL files and templates.

## 5. Quality Checks
- [ ] 5.1 Run the example end-to-end locally (data generation, build, validation) and fix any issues.
- [ ] 5.2 Run the test suite (or targeted tests) to ensure no regressions.
- [ ] 5.3 Run `openspec validate add-examples-sql-files-and-templates --strict` and resolve any spec issues.
