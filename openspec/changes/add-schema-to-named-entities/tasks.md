## 1. Configuration Model and Validation
- [ ] 1.1 Update config Pydantic models to add optional `schema` on view definitions (and any other relevant named entities as identified in the spec).
- [ ] 1.2 Update config validation to treat `(schema, name)` as the uniqueness key for views and ensure clear errors when duplicates occur.
- [ ] 1.3 Add or update tests to cover configs with and without `schema`, including mixed usage in the same catalog.

## 2. SQL Generation and Catalog Build
- [ ] 2.1 Update SQL generation for `CREATE VIEW` statements to emit schema-qualified identifiers when `schema` is present.
- [ ] 2.2 Ensure catalog build logic correctly respects schema-qualified identifiers without altering behaviour for views with no `schema`.
- [ ] 2.3 Add tests that build a catalog with schema-qualified and unqualified views and validate the resulting DuckDB catalog objects.

## 3. Semantic Layer and References
- [ ] 3.1 Extend semantic-layer models and validation so semantic models can reference schema-qualified base views and joins.
- [ ] 3.2 Add tests verifying that semantic models can safely reference views that include `schema` in their definition.

## 4. CLI, Docs, and Examples
- [ ] 4.1 Update any CLI help, docs, and example configs to demonstrate the `schema` field on views and related entities.
- [ ] 4.2 Add or update tests for `duckalog init` or template generation if they include example views.

## 5. Validation and Cleanup
- [ ] 5.1 Run the full test suite and fix regressions.
- [ ] 5.2 Run `openspec validate add-schema-to-named-entities --strict` and resolve any spec issues.
