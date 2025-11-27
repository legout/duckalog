# Add custom filesystem support to remote config loading

This enhancement allows users to pass pre-configured fsspec filesystem objects directly to Duckalog's remote configuration loading, enabling more flexible authentication patterns beyond environment variables.

## Status: **Proposed**

### Files Created
- `openspec/changes/add-custom-filesystem-support/proposal.md` - Detailed design specification
- `openspec/changes/add-custom-filesystem-support/tasks.md` - Implementation task breakdown

### Next Steps
1. Review and approve the proposal
2. Begin implementation with Phase 1 (Core API)
3. Progress through phases as outlined in the proposal

### Related Work
This builds upon the `add-remote-config-loader` implementation (completed) and extends it with enhanced authentication capabilities.

### Benefits
- **Programmatic credential management** - No need to set environment variables
- **Testing scenarios** - Easy to inject test filesystems
- **CI/CD integration** - Credentials can be passed securely
- **Multi-cloud support** - Different auth methods for different backends
- **Backward compatibility** - Existing environment variable auth preserved

### Example Usage (After Implementation)
```python
import fsspec
from duckalog import load_config

# Custom S3 filesystem
fs = fsspec.filesystem("s3", key="key", secret="secret", anon=False)
config = load_config("s3://my-bucket/config.yaml", filesystem=fs)

# CLI with filesystem options
duckalog build s3://bucket/config.yaml --fs-key key --fs-secret secret
```