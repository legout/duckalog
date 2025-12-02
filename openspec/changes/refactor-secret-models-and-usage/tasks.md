## 1. Spec alignment
- [ ] 1.1 Inventory current secret models in `config.py` and `secret_types.py`
- [ ] 1.2 Review the secrets section in `specs/config/spec.md` and secrets-related docs
- [ ] 1.3 Define `SecretConfig` as the canonical model and list fields per backend type
- [ ] 1.4 Update specs to de-emphasize or remove any mention of backend-specific config models

## 2. Implementation cleanup
- [ ] 2.1 Remove duplicated backend-specific secret classes from `config.py`
- [ ] 2.2 Keep or adjust backend-specific models in `secret_types.py` as internal helpers (if needed)
- [ ] 2.3 Ensure `SecretConfig` covers all fields required by DuckDB for each secret type
- [ ] 2.4 Update `generate_secret_sql` so it only uses fields defined on `SecretConfig`

## 3. Testing
- [ ] 3.1 Add or update tests to validate `SecretConfig` instances for each backend type
- [ ] 3.2 Add tests asserting that `generate_secret_sql` produces the expected DuckDB statements per backend type
- [ ] 3.3 Run full test suite and adjust any tests that referenced removed duplicate classes

## 4. Documentation
- [ ] 4.1 Update secrets documentation to use `SecretConfig` exclusively in examples
- [ ] 4.2 Document per-type field mapping and valid combinations
- [ ] 4.3 Add a note in the changelog about removal of duplicate secret models and clarified behavior

