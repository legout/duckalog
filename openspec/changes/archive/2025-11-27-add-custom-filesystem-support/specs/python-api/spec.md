# Add custom filesystem support to remote config loading

## ADDED Requirements

### Requirement: Add filesystem parameter to load_config_from_uri
The system SHALL add filesystem parameter to load_config_from_uri function to enable custom filesystem authentication. The system MUST support all existing fsspec filesystem implementations without breaking changes. The system MUST enable passing pre-configured fsspec filesystem objects for custom authentication.

#### Scenario: Direct credential injection
```python
import fsspec
from duckalog import load_config_from_uri

# Create filesystem with direct credentials
fs = fsspec.filesystem("s3", 
    key="AKIAIOSFODNN7EXAMPLE",
    secret="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    client_kwargs={"region_name": "us-west-2"}
)

# Load config using custom filesystem
config = load_config_from_uri("s3://my-bucket/config.yaml", filesystem=fs)
```

#### Scenario: GitHub token authentication
```python
import fsspec
from duckalog import load_config_from_uri

# GitHub filesystem with token
fs = fsspec.filesystem("github", token="ghp_xxxxxxxxxxxxxxxxxxxx")

# Load config from GitHub
config = load_config_from_uri("github://user/repo/config.yaml", filesystem=fs)
```

#### Scenario: Azure connection string
```python
import fsspec
from duckalog import load_config_from_uri

# Azure with connection string
connection_string = "DefaultEndpointsProtocol=https;AccountName=account;AccountKey=key;EndpointSuffix=core.windows.net"
fs = fsspec.filesystem("abfs", connection_string=connection_string)

config = load_config_from_uri("abfs://account@container/config.yaml", filesystem=fs)
```

### Requirement: Add filesystem parameter to fetch_remote_content
The system SHALL add filesystem parameter to fetch_remote_content function to support custom filesystem for content fetching. The system MUST use provided filesystem when available, fallback to default creation. The system MUST maintain backward compatibility with existing environment variable authentication.

#### Scenario: Custom filesystem with direct credentials
```python
import fsspec
from duckalog.remote_config import fetch_remote_content

# Create custom S3 filesystem
fs = fsspec.filesystem("s3", 
    key="AKIAIOSFODNN7EXAMPLE",
    secret="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
)

# Fetch content using custom filesystem
content = fetch_remote_content("s3://bucket/config.yaml", filesystem=fs)
```

#### Scenario: Fallback to default creation
```python
# When filesystem=None, should use default behavior
content = fetch_remote_content("s3://bucket/config.yaml")
```

### Requirement: Add filesystem parameter to _load_sql_files_from_remote_config
The system SHALL add filesystem parameter support to _load_sql_files_from_remote_config function for SQL file loading. The system MUST pass filesystem parameter to SQL file loading operations. The system MUST enable SQL file references to use custom authentication.

#### Scenario: Remote config with remote SQL files
```python
# Remote config references remote SQL file with custom filesystem
config = load_config_from_uri("s3://bucket/config.yaml", filesystem=fs)
# SQL file references in config should also use the same filesystem
```

### Requirement: Add filesystem validation and error handling
The system SHALL add filesystem validation and error handling to ensure robust operation with custom filesystems. The system MUST provide clear error messages for filesystem authentication failures. The system MUST validate custom filesystem objects appropriately.

#### Scenario: Invalid filesystem object
```python
# Should handle invalid filesystem gracefully
try:
    content = fetch_remote_content("s3://bucket/config.yaml", filesystem="invalid")
except RemoteConfigError as e:
    assert "Invalid filesystem" in str(e)
```

#### Scenario: Authentication failures
```python
# Should provide clear error messages for auth failures
try:
    content = fetch_remote_content("s3://bucket/config.yaml", filesystem=fs)
except RemoteConfigError as e:
    # Should include helpful auth guidance
    assert "Authentication" in str(e) or "credential" in str(e).lower()
```

### Requirement: Update _fetch_fsspec_content to use provided filesystem
The system SHALL update _fetch_fsspec_content function to use provided filesystem when available. The system MUST use provided filesystem object directly when passed. The system MUST handle filesystem-specific errors appropriately.

#### Scenario: Custom filesystem vs default creation
```python
# When filesystem is provided, should use it directly
with provided_fs.open("s3://bucket/config.yaml", "r") as f:
    content = f.read()
    
# When filesystem=None, should create default
with fsspec.open("s3://bucket/config.yaml", "r") as f:
    content = f.read()
```

## MODIFIED Requirements

### Requirement: Update main load_config function
The system SHALL update main load_config function to accept and pass through filesystem parameter. The system MUST maintain backward compatibility with existing environment variable authentication. The system MUST pass filesystem parameter to remote loader when provided.

#### Scenario: Local config unchanged
```python
# Local config (unchanged)
config = load_config("local_config.yaml")
```

#### Scenario: Remote config with custom filesystem
```python
# Remote config with custom filesystem
import fsspec
fs = fsspec.filesystem("s3", key="key", secret="secret")
config = load_config("s3://bucket/config.yaml", filesystem=fs)
```

#### Scenario: Backward compatibility maintained
```python
# Backward compatibility maintained
config = load_config("s3://bucket/config.yaml")  # Uses environment variables
```

### Remote Detection Logic
- **Enhanced**: Remote URI detection with filesystem parameter support
- **Maintained**: All existing local file loading behavior
- **Added**: Seamless delegation to remote loader with filesystem parameter

### Documentation Updates
- **Updated**: Docstrings with filesystem parameter examples
- **Added**: Type hints for filesystem parameter
- **Enhanced**: Usage examples showing custom filesystem scenarios
- **SHALL**: Document filesystem parameter in all relevant functions