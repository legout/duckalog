## 1. Spec updates
- [ ] 1.1 Review `specs/catalog-build/spec.md` for existing SQL generation requirements
- [ ] 1.2 Review `specs/config/spec.md` for existing secret and options requirements
- [ ] 1.3 Add or update requirements describing canonical `quote_ident` / `quote_literal` helpers
- [ ] 1.4 Specify allowed types and behavior for `SecretConfig.options` values

## 2. Quoting helper consolidation
- [ ] 2.1 Decide where the canonical quoting helpers live (e.g. `sql_generation` or a small `sql_utils` module)
- [ ] 2.2 Implement `quote_literal` with clear escaping semantics
- [ ] 2.3 Ensure `normalize_path_for_sql` composes with the canonical quoting helpers
- [ ] 2.4 Remove or deprecate any ad-hoc quoting helpers that diverge from the canonical behavior

## 3. Apply safe quoting to SQL generation
- [ ] 3.1 Update `generate_view_sql` to quote database and table identifiers for `duckdb` / `sqlite` / `postgres` sources
- [ ] 3.2 Update any attachment or catalog SQL in `engine.py` to use `quote_ident` for aliases and identifiers
- [ ] 3.3 Refactor `generate_secret_sql` to use `quote_literal` for all string values
- [ ] 3.4 Enforce the allowed option types in `generate_secret_sql` and raise `TypeError` for unsupported types

## 4. Testing and verification
- [ ] 4.1 Add unit tests for `quote_ident` and `quote_literal` (including embedded quotes)
- [ ] 4.2 Add tests for `generate_view_sql` that attempt SQL injection via database/table names
- [ ] 4.3 Add tests for `generate_secret_sql` covering edge cases in secrets and options (quotes, backslashes, unusual characters)
- [ ] 4.4 Run the full test suite and update any expectations around dry-run SQL output for secrets

## 5. Documentation and release notes
- [ ] 5.1 Update docs to describe the strengthened SQL quoting and secret handling guarantees
- [ ] 5.2 Add a changelog entry noting stricter option-type enforcement and improved injection protection

