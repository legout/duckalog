# Change: Add custom filesystem support to remote config loading

## Why

The current remote configuration implementation only supports authentication via environment variables, which limits flexibility for:
- Programmatic credential management in Python code
- Testing scenarios with custom authentication
- CI/CD pipelines with injected credentials
- Complex authentication setups (temporary credentials, custom endpoints)
- Multi-cloud scenarios where different auth methods are needed

Users want to pass pre-configured fsspec filesystem objects directly to `load_config()` and CLI commands, enabling more flexible authentication patterns without relying solely on environment variables.

## What Changes

### Core API Enhancements
- Add `filesystem` parameter to `load_config_from_uri()` and `fetch_remote_content()` functions
- Update `_fetch_fsspec_content()` to use provided filesystem when available
- Modify `_load_sql_files_from_remote_config()` to support custom filesystems for SQL file references
- Update main `load_config()` function to accept and pass through filesystem parameter

### CLI Enhancements  
- Add filesystem credential options to all CLI commands (`build`, `generate-sql`, `validate`)
- Implement filesystem creation from CLI parameters
- Add `--fs-*` options for different authentication methods
- Support backend-specific CLI options for common use cases

### Testing & Documentation
- Create comprehensive test suite for custom filesystem functionality
- Update documentation with filesystem parameter examples
- Add CLI filesystem options to help text and examples

## Impact

- **Affected capability**: remote config loading (enhanced)
- **Affected code**: `remote_config.py`, `config.py`, `cli.py`
- **Backward compatibility**: Fully maintained - existing environment variable authentication unchanged
- **Security**: Improved - enables secure credential injection without environment variables

## Design Decisions

### API Design
```python
# Primary API - supports custom filesystem
def load_config_from_uri(
    uri: str,
    load_sql_files: bool = True,
    sql_file_loader: Optional[Any] = None,
    resolve_paths: bool = False,
    timeout: int = 30,
    filesystem: Optional[fsspec.AbstractFileSystem] = None,  # NEW
) -> Config:
```

### CLI Design
```bash
# Generic filesystem options
--fs-protocol s3|gcs|abfs|sftp|github
--fs-key value
--fs-secret value  
--fs-token value
--fs-anon true|false
--fs-timeout seconds

# Backend-specific options
--aws-profile name
--gcs-credentials-file path
--azure-connection-string string
--sftp-host host
--sftp-port port
--sftp-key-file path
```

### Usage Examples

#### Python API with Custom Filesystem
```python
import fsspec
from duckalog import load_config

# S3 with direct credentials
fs = fsspec.filesystem("s3", 
    key="AKIAIOSFODNN7EXAMPLE", 
    secret="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    client_kwargs={'region_name': 'us-west-2'}
)
config = load_config("s3://my-bucket/config.yaml", filesystem=fs)

# GitHub with personal access token
fs = fsspec.filesystem("github", token="ghp_xxxxxxxxxxxxxxxxxxxx")
config = load_config("github://user/repo/config.yaml", filesystem=fs)

# Azure with connection string
fs = fsspec.filesystem("abfs", 
    connection_string="DefaultEndpointsProtocol=https;AccountName=account;AccountKey=key;EndpointSuffix=core.windows.net"
)
config = load_config("abfs://account@container/config.yaml", filesystem=fs)

# SFTP with SSH key
fs = fsspec.filesystem("sftp", 
    host="sftp.example.com",
    username="user",
    private_key="~/.ssh/id_rsa"
)
config = load_config("sftp://user@sftp.example.com/path/config.yaml", filesystem=fs)
```

#### CLI with Filesystem Options
```bash
# S3 with direct credentials
duckalog build s3://bucket/config.yaml \
  --fs-key AKIAIOSFODNN7EXAMPLE \
  --fs-secret wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY \
  --fs-region us-west-2

# GitHub with token
duckalog validate github://user/repo/config.yaml \
  --fs-token ghp_xxxxxxxxxxxxxxxxxxxx

# Azure with connection string
duckalog generate-sql abfs://account@container/config.yaml \
  --fs-connection-string "DefaultEndpointsProtocol=https;AccountName=account;AccountKey=key"

# SFTP with SSH key file
duckalog build sftp://user@server/path/config.yaml \
  --fs-host sftp.example.com \
  --fs-key-file ~/.ssh/id_rsa \
  --fs-port 22

# Using AWS profile (alternative to direct credentials)
duckalog build s3://bucket/config.yaml \
  --aws-profile myprofile

# Anonymous access (public buckets)
duckalog build s3://public-bucket/config.yaml \
  --fs-anon true
```

## Implementation Tasks

### Phase 1: Core API Completion
- [ ] 1.1 Complete `remote_config.py` filesystem parameter implementation
- [ ] 1.2 Update `_load_sql_files_from_remote_config()` to use custom filesystem
- [ ] 1.3 Add filesystem validation and comprehensive error handling
- [ ] 1.4 Update all docstrings with filesystem examples

### Phase 2: Main Integration
- [ ] 2.1 Update `config.py` to pass filesystem parameter to remote loader
- [ ] 2.2 Add filesystem parameter to main `load_config()` signature
- [ ] 2.3 Ensure backward compatibility with existing environment variable auth
- [ ] 2.4 Add filesystem parameter type hints and validation

### Phase 3: CLI Integration
- [ ] 3.1 Add filesystem credential options to CLI commands
- [ ] 3.2 Implement filesystem creation from CLI parameters
- [ ] 3.3 Add validation for CLI filesystem options
- [ ] 3.4 Update CLI help text and examples
- [ ] 3.5 Support backend-specific CLI options

### Phase 4: Testing & Documentation
- [ ] 4.1 Create `tests/test_custom_filesystem.py` with comprehensive scenarios
- [ ] 4.2 Create `tests/test_cli_filesystem.py` for CLI filesystem options
- [ ] 4.3 Update existing tests to cover filesystem parameter
- [ ] 4.4 Update README.md with filesystem parameter documentation
- [ ] 4.5 Add examples to `examples/` directory
- [ ] 4.6 Update CHANGELOG.md with new feature

## Security Considerations

### Credential Exposure
- ⚠️ **CLI credentials visible in process list** - document this limitation
- ✅ **Environment variables remain most secure** for production use
- ✅ **Custom filesystems enable secure credential injection** in code
- ✅ **No credentials embedded in URIs** - maintain security principle

### Best Practices Documentation
- Recommend environment variables for production
- Document custom filesystems for development/testing
- Provide examples for secure credential management
- Warn about CLI credential visibility

## Backward Compatibility

- ✅ **Fully backward compatible** - all existing functionality preserved
- ✅ **Environment variable authentication unchanged** - continues to work as before
- ✅ **Default behavior identical** - when filesystem=None, uses current implementation
- ✅ **CLI commands unchanged** - filesystem options are optional additions

## Open Questions

1. Should we add filesystem caching to avoid recreating filesystems for multiple operations?
2. Do we need to support filesystem configuration files for complex setups?
3. Should we add filesystem validation helpers for common misconfigurations?
4. Do we need to support filesystem factories for dynamic credential loading?

## Success Criteria

- [ ] Python API accepts filesystem parameter and uses it correctly
- [ ] CLI supports filesystem credential options for all major backends
- [ ] All existing functionality continues to work unchanged
- [ ] Comprehensive test coverage for filesystem scenarios
- [ ] Documentation updated with clear examples
- [ ] Security implications documented and warnings provided