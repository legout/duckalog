## 1. Spec updates
- [x] 1.1 Identify the sections in `specs/config/spec.md` and `specs/catalog-build/spec.md` that describe security behavior
- [x] 1.2 Add a concise "Security Regression Tests" subsection to each spec
- [x] 1.3 List the key behaviors that MUST be covered by tests (SQL injection attempts, secret options, path traversal)

## 2. SQL security tests
- [x] 2.1 Add a dedicated test module for SQL security (`tests/test_sql_security.py`)
- [x] 2.2 Add tests that exercise malicious view names and identifiers and verify the generated SQL remains safe
- [x] 2.3 Add tests that exercise secret values and options with special characters
- [x] 2.4 Add tests that verify unsupported secret option types raise `TypeError` with informative messages

## 3. Path security tests
- [x] 3.1 Add a dedicated test module for path security (`tests/test_path_security.py`)
- [x] 3.2 Add tests for valid relative paths under the config directory
- [x] 3.3 Add tests for invalid paths that attempt to escape the allowed roots and assert on the raised errors
- [x] 3.4 Where feasible, add tests simulating Windows-style paths to catch cross-platform issues

## 4. Integration into CI and developer workflow
- [x] 4.1 Ensure the new tests run as part of the default `pytest` suite
- [x] 4.2 Document the security regression tests in contributor docs so future changes keep them in mind

## Implementation Summary

**Completed Features:**
- Added comprehensive Security Regression Tests sections to both `specs/config/spec.md` and `specs/catalog-build/spec.md`
- Created `tests/test_sql_security.py` with 18 security tests covering:
  - SQL injection prevention for view identifiers and database/table names
  - Secret SQL injection prevention and type enforcement
  - Canonical quoting helper security validation
  - Dry-run SQL security parity testing
- Created `tests/test_path_security.py` with 21 security tests covering:
  - Path traversal protection (classic and advanced attack patterns)
  - Root-based path validation and boundary enforcement
  - Symlink security and cross-platform path handling
  - Error reporting and security boundary enforcement
- All tests pass and integrate seamlessly with existing pytest suite
- Documentation includes clear guidance on security test requirements for future contributors

