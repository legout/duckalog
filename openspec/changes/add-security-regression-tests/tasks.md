## 1. Spec updates
- [ ] 1.1 Identify the sections in `specs/config/spec.md` and `specs/catalog-build/spec.md` that describe security behavior
- [ ] 1.2 Add a concise “Security Regression Tests” subsection to each spec
- [ ] 1.3 List the key behaviors that MUST be covered by tests (SQL injection attempts, secret options, path traversal)

## 2. SQL security tests
- [ ] 2.1 Add a dedicated test module for SQL security (for example, `tests/test_sql_security.py`)
- [ ] 2.2 Add tests that exercise malicious view names and identifiers and verify the generated SQL remains safe
- [ ] 2.3 Add tests that exercise secret values and options with special characters
- [ ] 2.4 Add tests that verify unsupported secret option types raise `TypeError` with informative messages

## 3. Path security tests
- [ ] 3.1 Add a dedicated test module for path security (or extend existing path tests)
- [ ] 3.2 Add tests for valid relative paths under the config directory
- [ ] 3.3 Add tests for invalid paths that attempt to escape the allowed roots and assert on the raised errors
- [ ] 3.4 Where feasible, add tests simulating Windows-style paths to catch cross-platform issues

## 4. Integration into CI and developer workflow
- [ ] 4.1 Ensure the new tests run as part of the default `pytest` suite
- [ ] 4.2 Document the security regression tests in contributor docs so future changes keep them in mind

