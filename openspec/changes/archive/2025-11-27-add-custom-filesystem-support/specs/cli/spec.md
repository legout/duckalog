# Add CLI filesystem support to remote config loading

## ADDED Requirements

### Requirement: Add filesystem credential options to CLI commands
The system SHALL add filesystem credential options to CLI commands for building, validating, and generating SQL from remote configuration files. The system MUST support all major fsspec filesystem implementations. The system MUST provide clear error messages for invalid filesystem options.

#### Scenario: S3 with direct credentials
```bash
duckalog build s3://bucket/config.yaml \
  --fs-key AKIAIOSFODNN7EXAMPLE \
  --fs-secret wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY \
  --fs-region us-west-2
```

**Expected Behavior**:
- Creates S3 filesystem with provided credentials
- Loads remote config using custom filesystem
- Validates and processes configuration normally
- Maintains backward compatibility with environment variables

#### Scenario: GitHub with token
```bash
duckalog validate github://user/repo/config.yaml \
  --fs-token ghp_xxxxxxxxxxxxxxxxxxxx
```

**Expected Behavior**:
- Creates GitHub filesystem with provided token
- Loads remote config from GitHub repository
- Handles private repositories with proper authentication
- Provides clear error for invalid tokens

#### Scenario: Azure with connection string
```bash
duckalog generate-sql abfs://account@container/config.yaml \
  --fs-connection-string "DefaultEndpointsProtocol=https;AccountName=account;AccountKey=key"
```

**Expected Behavior**:
- Creates Azure filesystem with connection string
- Loads remote config from Azure Blob Storage
- Supports both account key and SAS token connection strings
- Validates connection string format

#### Scenario: SFTP with SSH key
```bash
duckalog build sftp://user@server/path/config.yaml \
  --fs-host sftp.example.com \
  --fs-key-file ~/.ssh/id_rsa \
  --fs-port 22
```

**Expected Behavior**:
- Creates SFTP filesystem with SSH key authentication
- Loads remote config from SFTP server
- Supports both password and key-based authentication
- Handles custom host and port specifications

#### Scenario: AWS profile
```bash
duckalog build s3://bucket/config.yaml \
  --aws-profile myprofile
```

**Expected Behavior**:
- Uses AWS credentials from configured profile
- Loads remote config using profile authentication
- Supports MFA and temporary credentials from profile
- Falls back to environment variables if profile not found

#### Scenario: Anonymous access
```bash
duckalog build s3://public-bucket/config.yaml \
  --fs-anon true
```

**Expected Behavior**:
- Creates anonymous filesystem for public access
- Loads remote config without authentication
- Useful for public buckets and repositories
- Provides clear error if authentication required

#### Scenario: Error handling
```bash
duckalog build s3://bucket/config.yaml \
  --fs-key invalid_key \
  --fs-secret
```

**Expected Behavior**:
- Validates filesystem credential parameters
- Provides clear error messages for missing required values
- Maintains existing error handling patterns
- Returns appropriate exit codes for CLI errors

#### Scenario: Mixed authentication methods
```bash
# Test combining environment variables with filesystem options
export AWS_DEFAULT_REGION=us-west-2
duckalog build s3://bucket/config.yaml \
  --fs-key AKIAIOSFODNN7EXAMPLE \
  --fs-secret wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

**Expected Behavior**:
- Combines environment variables with CLI filesystem options
- Uses CLI options for explicit credentials, environment for defaults
- Maintains flexible authentication patterns
- Provides clear precedence documentation

#### Scenario: Invalid filesystem options
```bash
duckalog build s3://bucket/config.yaml \
  --fs-protocol invalid_protocol
```

**Expected Behavior**:
- Validates filesystem protocol parameter
- Provides clear error message for unsupported protocols
- Lists supported protocols in error message
- Maintains existing error handling patterns

**Expected Behavior**:
- Creates Azure filesystem with connection string
- Loads remote config from Azure Blob Storage
- Supports both account key and SAS token connection strings
- Validates connection string format

#### Scenario: SFTP with SSH key
```markdown
#### Scenario: SFTP SSH Key Authentication
```bash
duckalog build sftp://user@server/path/config.yaml \
  --fs-host sftp.example.com \
  --fs-key-file ~/.ssh/id_rsa \
  --fs-port 22
```

**Expected Behavior**:
- Creates SFTP filesystem with SSH key authentication
- Loads remote config from SFTP server
- Supports both password and key-based authentication
- Handles custom host and port specifications

#### Scenario: AWS profile
```markdown
#### Scenario: AWS Profile Authentication
```bash
duckalog build s3://bucket/config.yaml \
  --aws-profile myprofile
```

**Expected Behavior**:
- Uses AWS credentials from configured profile
- Loads remote config using profile authentication
- Supports MFA and temporary credentials from profile
- Falls back to environment variables if profile not found

#### Scenario: Anonymous access
```markdown
#### Scenario: Anonymous Public Access
```bash
duckalog build s3://public-bucket/config.yaml \
  --fs-anon true
```

**Expected Behavior**:
- Creates anonymous filesystem for public access
- Loads remote config without authentication
- Useful for public buckets and repositories
- Provides clear error if authentication required

### Error Handling
- **Added**: Validation for filesystem credential parameters
- **Enhanced**: Clear error messages for authentication failures
- **Maintained**: Existing error handling for remote operations
- **Added**: Help text for filesystem options

### Integration Points
- **Enhanced**: Filesystem creation from CLI parameters
- **Maintained**: All existing CLI functionality
- **Added**: Filesystem parameter passing to remote loader
- **Preserved**: Backward compatibility with existing workflows