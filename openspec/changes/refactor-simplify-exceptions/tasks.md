## 1. Spec updates
- [ ] 1.1 Expand `specs/errors-logging/spec.md` to describe the exception hierarchy
- [ ] 1.2 Update other specs (config, catalog-build, remote-config) to reference the standardized exceptions

## 2. Exception hierarchy implementation
- [ ] 2.1 Introduce `DuckalogError` base class and ensure existing exceptions inherit from it
- [ ] 2.2 Add any missing domain-specific exceptions where helpful (for example, path resolution)

## 3. Error handling refactor
- [ ] 3.1 Replace bare `except Exception` patterns with targeted or wrapped exceptions
- [ ] 3.2 Ensure exception chaining (`raise ... from exc`) is used where appropriate
- [ ] 3.3 Remove silent `pass` blocks in error handling except where explicitly justified

## 4. Testing and docs
- [ ] 4.1 Add or update tests to assert that common failure scenarios raise the expected exceptions
- [ ] 4.2 Update user-facing docs to include the new error section and examples of handling common errors

