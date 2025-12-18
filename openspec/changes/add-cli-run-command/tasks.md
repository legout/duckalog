## 1. CLI Command Implementation
- [ ] 1.1 Add `run` command to CLI with smart connection logic
- [ ] 1.2 Update `build` command to be explicit full rebuild
- [ ] 1.3 Add `--force-rebuild` flag to `run` command
- [ ] 1.4 Update help text and command descriptions
- [ ] 1.5 Add deprecation warning for `run` vs `build` usage

## 2. Python API Enhancement
- [ ] 2.1 Add `connect_to_catalog()` function to python_api.py
- [ ] 2.2 Add deprecation warning to `build_catalog()` function
- [ ] 2.3 Update example usage in documentation
- [ ] 2.4 Ensure backward compatibility for existing code

## 3. Error Handling and UX
- [ ] 3.1 Add clear error messages for connection failures
- [ ] 3.2 Add progress indicators for session state restoration
- [ ] 3.3 Add verbose logging for `run` command operations
- [ ] 3.4 Add config validation before connection attempts

## 4. Documentation Migration
- [ ] 4.1 Update README.md to use `run` command in examples
- [ ] 4.2 Update quickstart guide with new workflow
- [ ] 4.3 Add migration guide from `build` to `run` command
- [ ] 4.4 Update CLI help and command references