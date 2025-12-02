# Change: Improve Secrets Options Documentation

## Why
The documentation for DuckDB secrets configuration currently omits critical information about the `options` field, which is essential for many real-world use cases. Users encountered `ValidationError` when trying to use S3-specific parameters like `use_ssl` and `url_style` because these fields are not documented as available through the `options` field. The current documentation only shows `options` usage for HTTP secrets, leading users to believe it's HTTP-specific.

## What Changes
- **Enhance S3 secrets documentation**: Add `options` field to S3 Secret Fields table with explanation
- **Update all secret type tables**: Ensure `options` field is documented for all secret types (S3, Azure, GCS, Database, HTTP)
- **Add S3 examples with options**: Include practical examples showing `use_ssl`, `url_style`, and other common S3 parameters
- **Add general options explanatory section**: Clarify that `options` field works for all secret types
- **Update documentation structure**: Ensure consistent presentation across all secret type documentation

## Impact
- **Affected specs**: docs (enhanced capability), examples (enhanced capability)
- **Affected documentation**: `docs/examples/duckdb-secrets.md`
- **User Experience**: Prevents confusion and validation errors for users with advanced secret requirements
- **Breaking Changes**: None - this is purely documentation enhancement