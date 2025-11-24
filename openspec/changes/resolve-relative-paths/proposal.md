# Relative Path Resolution

## Problem Statement

Currently, when users specify relative paths in Duckalog catalog YAML files for data source URIs (e.g., Parquet files), these paths are passed directly to DuckDB without resolution to absolute paths. DuckDB requires absolute paths for local file access, leading to runtime errors or incorrect data access when catalogs are built from different working directories.

## Proposed Solution

Implement automatic resolution of relative paths to absolute paths during catalog configuration processing. Relative paths should be resolved relative to the configuration file's directory, ensuring consistent behavior regardless of where Duckalog is executed from.

## Scope

**In Scope:**
- Relative path resolution for Parquet, Delta, and other file-based data sources
- Path validation for security (prevent directory traversal attacks)
- Maintaining backward compatibility with existing absolute paths
- Cross-platform path handling (Windows, macOS, Linux)
- Integration with existing configuration validation pipeline

**Out of Scope:**
- Cloud storage URIs (s3://, gs://, etc.) - these should remain unchanged
- Database connection strings - these use different protocols
- HTTP/HTTPS URLs - these are already absolute

## Success Criteria

1. Relative paths in YAML configs are automatically resolved to absolute paths
2. Absolute paths continue to work unchanged (backward compatibility)
3. Security validation prevents directory traversal attacks
4. Cross-platform compatibility is maintained
5. Configuration validation catches invalid paths early
6. All existing tests continue to pass

## Implementation Approach

1. Add path resolution utility functions
2. Integrate resolution into configuration validation
3. Add security validation for resolved paths
4. Update SQL generation to use resolved paths
5. Add comprehensive test coverage
6. Update documentation with examples

## Risks and Mitigations

**Risk:** Breaking existing configurations that rely on relative paths
**Mitigation:** Maintain backward compatibility and provide clear migration path

**Risk:** Security vulnerabilities from path traversal
**Mitigation:** Implement strict validation and sandboxing

**Risk:** Cross-platform path handling complexity
**Mitigation:** Use Python's pathlib for robust cross-platform support