# Tasks: Add Syntax Highlighting for YAML and Python Code Cells

## 1. Install PyMdown Extensions

- [x] 1.1 Install required PyMdown Extensions packages:
  - `pymdown-extensions` (includes highlight, superfences, inlinehilite, snippets)
  - Verify installation with `pip show pymdown-extensions`
- [x] 1.2 Test that extensions are available in the Python environment
- [x] 1.3 Document version requirements if any specific versions are needed

## 2. Update MkDocs Configuration

- [x] 2.1 Backup current `mkdocs.yml` configuration
- [x] 2.2 Add `pymdownx.highlight` extension with proper configuration:
  ```yaml
  - pymdownx.highlight:
      anchor_linenums: true
      line_spans: "__span"
      use_pygments: true
  ```
- [x] 2.3 Add `pymdownx.superfences` extension for enhanced code handling
- [x] 2.4 Add `pymdownx.inlinehilite` for inline code highlighting
- [x] 2.5 Add `pymdownx.snippets` for code snippet inclusion
- [x] 2.6 Update existing markdown_extensions to include new extensions
- [x] 2.7 Test `mkdocs build` to ensure configuration is valid

## 3. Update Existing Documentation Files

- [x] 3.1 Update `docs/examples/index.md`:
  - Add `yaml` language specification to YAML code blocks
  - Add `python` language specification to Python code examples
  - Verify all code blocks render with proper highlighting

- [x] 3.2 Update `docs/examples/multi-source-analytics.md`:
  - Add `yaml` specification to all configuration examples
  - Add `bash` specification to shell command examples
  - Add `python` specification to Python code examples
  - Ensure complex YAML with comments still renders correctly

- [x] 3.3 Update `docs/examples/simple-parquet.md`:
  - Add `yaml` specification to all configuration examples
  - Add `bash` specification to command line examples
  - Add `python` specification to Python code examples
  - Verify S3-related configuration YAML renders properly

- [x] 3.4 Update `docs/examples/local-attachments.md`:
  - Add `yaml` specification to all configuration examples
  - Add `bash` specification to command examples
  - Add `python` and `sql` specifications to respective code blocks
  - Ensure database-related YAML structures highlight correctly

- [x] 3.5 Update `docs/examples/environment-vars.md`:
  - Add `yaml` specification to configuration examples
  - Add `bash` specification to shell script examples
  - Add `python` specification to Python code examples
  - Add `dockerfile` specification to Docker examples if any

- [x] 3.6 Update `docs/index.md`:
  - Add `yaml` specification to quickstart configuration example
  - Add `python` specification to Python API examples
  - Add `bash` specification to command line examples

- [x] 3.7 Update `docs/guides/usage.md`:
  - Add `yaml` specification to all configuration examples
  - Add `bash` specification to command examples
  - Add `python` specification to any Python code
  - Ensure table structures in YAML examples highlight properly

## 4. Validate Syntax Highlighting

- [x] 4.1 Test that YAML syntax highlighting works correctly:
  - Verify keys, values, and nested structures are highlighted
  - Check that YAML anchors (`&` and `*`) are handled properly
  - Ensure environment variable interpolation (`${env:VAR}`) is visible
  - Confirm string quotes, numbers, and booleans are distinguished

- [x] 4.2 Test that Python syntax highlighting works correctly:
  - Verify keywords, strings, comments, and function names are highlighted
  - Check that docstrings and function definitions are properly styled
  - Ensure imports and module references are highlighted
  - Confirm f-strings and complex expressions are handled

- [x] 4.3 Test mixed language highlighting:
  - Verify shell commands in `bash` blocks are highlighted
  - Check that SQL in `sql` blocks (if any) is properly styled
  - Ensure JSON within YAML is handled correctly

## 5. Test Documentation Build

- [x] 5.1 Run `mkdocs build` and verify it completes without errors
- [x] 5.2 Check that all syntax highlighting CSS is included in the build
- [x] 5.3 Verify that the built site contains properly highlighted code
- [x] 5.4 Test that line numbers work correctly for long code examples
- [x] 5.5 Ensure syntax highlighting works in both light and dark themes

## 6. Cross-Browser and Responsive Testing

- [x] 6.1 Test syntax highlighting in Chrome/Chromium
- [x] 6.2 Test syntax highlighting in Firefox
- [x] 6.3 Test syntax highlighting in Safari (if available)
- [x] 6.4 Verify mobile/tablet responsiveness of highlighted code blocks
- [x] 6.5 Test copy-to-clipboard functionality with syntax highlighting

## 7. Performance and Quality Assurance

- [x] 7.1 Verify that syntax highlighting doesn't significantly increase build time
- [x] 7.2 Check that CSS bundle size is reasonable
- [x] 7.3 Test that highlighted code is accessible (screen readers, high contrast)
- [x] 7.4 Ensure code blocks remain copyable and selectable
- [x] 7.5 Verify that search functionality still works with highlighted code

## 8. Documentation and Communication

- [x] 8.1 Update any documentation about contributing that mentions code formatting
- [x] 8.2 Document the new syntax highlighting requirements for future contributors
- [x] 8.3 Add guidelines about code block language specifications
- [x] 8.4 Test that code examples in PR descriptions will also benefit from highlighting

## 9. Final Validation and Cleanup

- [x] 9.1 Run comprehensive `mkdocs build` test
- [x] 9.2 Validate all example configurations still work correctly
- [x] 9.3 Verify that syntax highlighting enhances readability without distractions
- [x] 9.4 Test edge cases:
  - Very long code blocks
  - Code blocks with special characters
  - Inline code within markdown text
  - Code blocks with Unicode characters
- [x] 9.5 Final visual inspection of all updated documentation pages

## 10. Rollback Plan

- [x] 10.1 Keep backup of original `mkdocs.yml` configuration
- [x] 10.2 Document steps to revert changes if needed
- [x] 10.3 Test rollback process to ensure it works
- [x] 10.4 Verify that rollback doesn't break existing functionality

## Success Criteria

✅ **Configuration**: MkDocs builds successfully with new extensions
✅ **YAML Highlighting**: All YAML examples show proper syntax highlighting
✅ **Python Highlighting**: All Python examples show proper syntax highlighting
✅ **Cross-Reference**: All documentation files updated consistently
✅ **Responsive**: Syntax highlighting works across devices and browsers
✅ **Performance**: No significant impact on build time or site performance
✅ **Accessibility**: Syntax highlighting doesn't interfere with accessibility features

## Estimated Time

- **Installation and Configuration**: 30 minutes
- **File Updates**: 60-90 minutes (depending on number of files)
- **Testing and Validation**: 30-45 minutes
- **Cleanup and Documentation**: 15-30 minutes

**Total**: Approximately 2-3 hours for complete implementation

## Dependencies

- PyMdown Extensions package
- Access to all documentation files
- MkDocs build environment
- Web browser for testing