# Proposal: Extend Config Imports with Remote Sources

## Why
The core `add-config-imports` change focuses on local file imports to keep the initial feature
small and robust. Many teams, however, keep shared configuration in remote locations such as
S3, GCS, or Git-backed HTTP endpoints. Being able to import configuration files from these
locations using the same `imports` mechanism gives Duckalog users a consistent way to:

- Reuse shared base configs across multiple projects or environments.
- Centralize environment- or region-specific defaults in one remote location.
- Avoid manual sync or copy steps when updating common configuration.

## What Changes
This change will extend config imports to support remote URIs:

1. **Remote import support**
   - Allow `imports` entries to reference URIs such as `s3://...`, `gcs://...`, or `https://...`.
   - Reuse the existing remote config loading infrastructure and authentication guidance.

2. **Consistent behavior with local imports**
   - Imported remote configs are merged using the same deep-merge and uniqueness rules defined by
     `add-config-imports`.
   - Circular import detection continues to work when remote and local imports are mixed.

3. **Security and observability**
   - Remote imports follow the same security constraints and error-reporting patterns as existing
     remote config loading.
   - Errors clearly indicate which remote URI failed and in what context.

## Out of Scope
- Changing the core import semantics (merge strategy, uniqueness, etc.).
- Adding advanced import syntax such as selective imports, override flags, or glob patterns.
- Adding new storage backends beyond those already supported by the remote config loader.

## Impact
- **Reuse**: Shared configuration hosted in buckets or repos can be imported directly via `imports`.
- **Consistency**: Local and remote imports share the same logical model, avoiding separate concepts
  for “remote base configs”.
- **Incremental adoption**: Teams already using local imports can gradually move some components to
  remote locations without changing how catalogs are loaded.
