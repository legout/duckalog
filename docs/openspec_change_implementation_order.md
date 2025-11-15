Rationale and suggested order:

  1. add-config-schema – everything else (build, SQL, Python API, metadata) depends on the config models and env interpolation.
  2. add-sql-generation – needs ViewConfig and Config from the schema.
  3. add-catalog-build-cli – depends on config + SQL generation to actually build catalogs and wire the CLI.
  4. add-error-and-logging – wraps config/engine behavior with stable error types and logging.
  5. add-view-metadata – small extension of the schema once the basics work.
  6. add-python-api – thin wrappers on top of config + sqlgen + build.
  7. add-testing-strategy – enforce/extend tests as you implement each of the above (partly in parallel).
