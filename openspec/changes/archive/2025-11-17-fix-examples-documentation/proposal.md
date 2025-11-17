# Change: Fix Examples Documentation Structure

## Why

The current `update-docs-examples` implementation added a multi-source configuration example as a raw YAML file and linked it directly in the MkDocs navigation. This creates a poor user experience because:

1. **Raw YAML rendering**: YAML files don't render nicely in MkDocs - users see raw YAML syntax without proper documentation formatting
2. **Lack of context**: The YAML file contains inline comments, but there's no structured explanation of what's happening or why
3. **Poor discoverability**: Users have to parse through raw configuration to understand what's possible
4. **Missed learning opportunity**: An example this comprehensive deserves a guided walkthrough with explanations, not just raw code

## What Changes

- **Convert `docs/examples/multi-source-config.yaml` to `docs/examples/multi-source-examples.md`**: Transform the raw YAML into a structured Markdown document that includes:
  - Introduction explaining the scenario
  - Full YAML configuration with annotated sections explaining each part
  - Step-by-step walkthrough of how to use the example
  - Explanation of key concepts demonstrated in the config
  
- **Create additional focused examples**: Add at least 2-3 more practical example documents:
  - Simple Parquet-only example (`simple-parquet.md`)
  - Local DuckDB attachments example (`local-attachments.md`)
  - Environment-specific configuration guide (`environment-vars.md`)

- **Update MkDocs navigation**: Change the navigation from linking raw YAML files to linking the new Markdown documentation pages

- **Add index for examples**: Create `docs/examples/index.md` to serve as a directory page explaining what examples are available and when to use each one

## Impact

- **Better user experience**: Users can read through examples as proper documentation with explanations, not just raw YAML
- **Improved learning**: Each example becomes a tutorial that teaches concepts while demonstrating practical usage
- **Enhanced discoverability**: Examples directory helps users find relevant patterns for their use case
- **Maintained functionality**: All existing examples are preserved but now rendered as readable documentation

## Technical Details

The new structure will be:

```
docs/examples/
├── index.md                    # Directory page with overview
├── multi-source-analytics.md   # Main comprehensive example (converted from YAML)
├── simple-parquet.md           # Minimal Parquet-only example
├── local-attachments.md        # Local DuckDB/SQLite example
└── environment-vars.md         # Environment variable patterns
```

Each example document will follow this pattern:
1. Introduction and use case
2. Prerequisites
3. Full annotated configuration
4. Step-by-step usage instructions
5. Key concepts demonstrated
6. Variations and customizations
```

</file_content>