# Change: Add S3 Options Field Secrets Example

## Why
Users frequently encounter validation errors when trying to use S3-specific parameters like \`use_ssl\` and \`url_style\` in DuckDB secrets configuration because these parameters are not shown in any S3 examples. The current documentation only shows \`options\` usage for HTTP secrets, leading users to believe it's HTTP-specific. Adding a clear S3 example with options will prevent user confusion and reduce support requests.

## What Changes
- **Add S3 options example**: Create a practical S3 secret configuration showing \`use_ssl\`, \`url_style\`, and other common parameters
- **Update S3 documentation**: Add \`options\` field to the S3 Secret Fields table
- **Include environment variable integration**: Show how to use options with environment variables in S3 context

## Impact
- **Affected specs**: examples (enhanced capability)
- **Affected documentation**: \`docs/examples/duckdb-secrets.md\`
- **User Experience**: Prevents validation errors for common S3 configurations
- **Breaking Changes**: None - this is purely documentation enhancement
