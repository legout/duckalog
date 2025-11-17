# Tasks: Fix Examples Documentation Structure

## 1. Convert and enhance the multi-source example

- [x] 1.1 Create `docs/examples/multi-source-analytics.md` from the existing YAML config
- [x] 1.2 Add introduction section explaining the business scenario
- [x] 1.3 Add prerequisites and requirements section
- [x] 1.4 Convert the YAML to code blocks with annotated explanations for each section
- [x] 1.5 Add step-by-step usage walkthrough with commands
- [x] 1.6 Add "key concepts demonstrated" section highlighting what users can learn
- [x] 1.7 Add troubleshooting tips specific to this example
- [x] 1.8 Delete the old `docs/examples/multi-source-config.yaml` file

## 2. Create additional focused example documentation

- [x] 2.1 Create `docs/examples/simple-parquet.md`:
  - Minimal Parquet-only configuration
  - Explains basics of S3 configuration
  - Simple single-view and multi-view examples
  
- [x] 2.2 Create `docs/examples/local-attachments.md`:
  - Local DuckDB and SQLite attachment patterns
  - Explains when to use read_only attachments
  - Examples of cross-referencing attached tables
  
- [x] 2.3 Create `docs/examples/environment-vars.md`:
  - Environment variable patterns and best practices
  - Security considerations
  - Examples of environment-specific configurations
  - How to manage credentials safely

## 3. Create examples directory page

- [x] 3.1 Create `docs/examples/index.md`:
  - Overview of all available examples
  - When to use each example (decision tree)
  - Prerequisites for running examples
  - Links to each specific example

## 4. Update documentation site configuration

- [x] 4.1 Update `mkdocs.yml` navigation to replace raw YAML links with Markdown pages
- [x] 4.2 Update cross-references in `docs/guides/usage.md` to point to new example pages
- [x] 4.3 Ensure `mkdocs build` succeeds with new structure
- [x] 4.4 Verify all examples render correctly in the documentation site

## 5. Validation and cleanup

- [x] 5.1 Review all example files for consistency in style and formatting
- [x] 5.2 Ensure all code blocks have proper syntax highlighting
- [x] 5.3 Verify all external links and cross-references work correctly
- [x] 5.4 Test that the examples are discoverable from the main documentation