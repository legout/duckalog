## 1. Decision and documentation
- [ ] 1.1 Confirm the minimum supported Python version (3.12+)
- [ ] 1.2 Update `openspec/project.md` Tech Stack section to match
- [ ] 1.3 Update `specs/package-metadata/spec.md` with supported versions and rationale
- [ ] 1.4 Update `specs/docs/spec.md` and README to mention Python 3.12+ explicitly

## 2. Packaging and CI
- [ ] 2.1 Update `pyproject.toml` `requires-python` and classifiers
- [ ] 2.2 Update CI workflows to run tests on the supported versions
- [ ] 2.3 Verify release tooling (if any) uses the updated metadata

## 3. Contributor guidance
- [ ] 3.1 Ensure contribution guidelines reference the modern typing conventions
- [ ] 3.2 Remove or update any docs that suggest 3.9–3.11 compatibility

