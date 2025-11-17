# Change: Add Syntax Highlighting for YAML and Python Code Cells

## Why

The current documentation uses basic code blocks without syntax highlighting, which creates several issues:

1. **Poor readability**: YAML and Python code without syntax highlighting is harder to read, especially for longer examples
2. **Reduced professionalism**: Documentation without syntax highlighting appears incomplete or outdated
3. **Learning friction**: Users need to mentally parse through plain text, making it harder to identify key syntax elements
4. **Inconsistent experience**: Many modern documentation tools provide syntax highlighting by default
5. **Copy-paste errors**: Without syntax highlighting, it's harder to distinguish between actual code and comments

The existing examples contain substantial YAML and Python code that would benefit significantly from syntax highlighting, making them easier to read, understand, and copy.

## What Changes

- **Enable YAML syntax highlighting** in MkDocs configuration:
  - Configure PyMdown Extensions for YAML syntax highlighting
  - Ensure YAML code blocks in examples render with proper syntax highlighting
  - Handle YAML frontmatter, anchors, and complex nested structures

- **Enable Python syntax highlighting** in MkDocs configuration:
  - Configure Python syntax highlighting for code examples
  - Support for Python docstrings, function definitions, and complex expressions
  - Handle Python code examples in tutorial sections

- **Update MkDocs configuration** (`mkdocs.yml`):
  - Add `pymdownx.highlight` extension for general syntax highlighting
  - Add `pymdownx.superfences` extension for enhanced code block handling
  - Configure language-specific syntax highlighting for YAML and Python

- **Enhance existing code examples**:
  - Ensure all YAML configuration examples use proper language specification
  - Update Python code examples to use Python syntax highlighting
  - Maintain existing functionality while improving visual presentation

## Impact

- **Improved readability**: Users can quickly identify YAML structure and Python syntax elements
- **Better learning experience**: Syntax highlighting helps users understand code patterns and structure
- **Professional appearance**: Documentation looks modern and polished
- **Easier code copying**: Enhanced syntax makes it easier to identify and copy valid code sections
- **Consistent formatting**: All code examples will have consistent, professional formatting
- **No functional changes**: This is purely a visual improvement that doesn't affect Duckalog's behavior

## Technical Details

### MkDocs Configuration Updates

The changes will add these PyMdown Extensions to `mkdocs.yml`:

```yaml
markdown_extensions:
  - pymdownx.highlight:
      anchor_linenums: true
      line_spans: "__span"
      pygments_lang_classes: true
      use_pygments: true
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
  - pymdownx.inlinehilite
  - pymdownx.snippets
```

### Code Block Format

Updated code blocks will use proper language specification:

**YAML Examples:**
```yaml
version: 1

duckdb:
  database: catalog.duckdb
  
views:
  - name: example
    source: parquet
    uri: "s3://bucket/data/*.parquet"
```

**Python Examples:**
```python
from duckalog import build_catalog, load_config

# Load and validate configuration
config = load_config("catalog.yaml")

# Build the catalog
build_catalog("catalog.yaml")
```

### Existing Files to Update

- `mkdocs.yml` - Add PyMdown Extensions configuration
- All example files in `docs/examples/` - Ensure proper language specification
- `docs/index.md` - Update code examples with syntax highlighting
- `docs/guides/usage.md` - Add language specifications to YAML and Python examples

### Backward Compatibility

- All existing functionality remains unchanged
- Code examples continue to work identically
- Only visual presentation is enhanced
- No changes to Duckalog's core behavior or API

## Validation Plan

1. **Configuration validation**: Ensure MkDocs build succeeds with new extensions
2. **Visual verification**: Confirm syntax highlighting renders correctly in the built site
3. **Example testing**: Verify all example configurations are still valid and functional
4. **Cross-reference check**: Ensure all code examples are properly formatted
5. **Responsive testing**: Confirm syntax highlighting works across different screen sizes