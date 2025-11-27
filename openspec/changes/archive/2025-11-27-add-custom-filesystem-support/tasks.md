## 1. Scope & design
- [x] 1.1 Complete `remote_config.py` filesystem parameter implementation
- [x] 1.2 Update `_load_sql_files_from_remote_config()` to use custom filesystem
- [x] 1.3 Add filesystem validation and comprehensive error handling
- [x] 1.4 Update all docstrings with filesystem examples

## 2. Main integration
- [x] 2.1 Update `config.py` to pass filesystem parameter to remote loader
- [x] 2.2 Add filesystem parameter to main `load_config()` signature
- [x] 2.3 Ensure backward compatibility with existing environment variable auth
- [x] 2.4 Add filesystem parameter type hints and validation

## 3. CLI integration
- [x] 3.1 Add filesystem credential options to CLI commands
- [x] 3.2 Implement filesystem creation from CLI parameters
- [x] 3.3 Add validation for CLI filesystem options
- [x] 3.4 Update CLI help text and examples
- [x] 3.5 Support backend-specific CLI options

## 4. Testing & documentation
- [x] 4.1 Create `tests/test_custom_filesystem.py` with comprehensive scenarios
- [x] 4.2 Create `tests/test_cli_filesystem.py` for CLI filesystem options
- [x] 4.3 Update existing tests to cover filesystem parameter
- [x] 4.4 Update README.md with filesystem parameter documentation
- [x] 4.5 Add examples to `examples/` directory
- [x] 4.6 Update CHANGELOG.md with new feature