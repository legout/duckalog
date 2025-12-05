# Change: Update API Docstrings for MkDocStrings‑Only Reference

## Why

The long‑term goal is to make the **API reference in `docs/reference/api.md` fully powered by mkdocstrings**, not hand‑written summaries. Today:

- Some public APIs have incomplete or missing docstrings.
- Docstring style is not fully consistent.
- The API reference mixes curated prose with partially generated content.

To use **mkdocstrings exclusively** for API docs, we need:

1. **Comprehensive, high‑quality docstrings** across the public surface (functions, classes, methods).
2. Docstrings that follow the configured style (**Google style** in `mkdocs.yml`) and are suitable for direct rendering.
3. **Examples in docstrings where useful**, especially for key user‑facing entry points (config loading, catalog building, connection helpers, SQL file loading).

This change prepares the codebase so `docs/reference/api.md` can be entirely mkdocstrings‑based.

## What Changes

### 1. Define API Documentation Scope and Style

- Establish a clear definition of the **public API** to document:
  - Top‑level `duckalog` functions: `load_config`, `build_catalog`, `validate_config`, `generate_sql`, etc.
  - Connection helpers: `connect_to_catalog`, `connect_to_catalog_cm`, `connect_and_build_catalog`.
  - Key configuration models and exceptions that are part of the public surface.
  - Selected helper modules that are intentionally exported and supported.
- Confirm and document that:
  - **Google‑style docstrings** are the standard (matches existing mkdocstrings config).
  - Docstrings should include, where appropriate:
    - Brief summary line.
    - Args/Parameters section.
    - Returns section.
    - Raises section.
    - Short, runnable example for user‑facing entry points.

### 2. Audit Existing Docstrings

- Create an inventory of:
  - Public modules (`duckalog.__init__`, `duckalog.config`, `duckalog.engine`, `duckalog.dashboard`, etc.).
  - Public functions/classes/methods exported from those modules.
- For each symbol, record whether:
  - A docstring exists.
  - It follows Google style and is clear enough to render as documentation.
  - It needs an example to clarify usage.
- Capture the audit in a lightweight format (table or checklist) under `openspec/changes/update-api-docstrings-for-mkdocstrings/specs/documentation/api-docstrings.md`.

### 3. Improve and Complete Docstrings

- For all public APIs identified in the audit:
  - Add or update docstrings to:
    - Be accurate and up to date.
    - Follow Google‑style sections.
    - Reference relevant concepts (config imports, SQL files, remote configs, dashboard) with links where appropriate.
  - Add **short examples** for:
    - Loading configs and building catalogs.
    - Using connection helpers.
    - Common SQL‑file/template scenarios.
- Ensure examples are:
  - Minimal and focused (no long scripts).
  - Realistic enough to be copy‑pasted.
  - Kept in sync with tutorials and examples where possible.

### 4. Make API Reference MkDocStrings‑Only

- Simplify `docs/reference/api.md` to depend entirely on mkdocstrings, for example:

  ```markdown
  # API Reference

  This reference is generated from the Duckalog Python API using mkdocstrings.

  ::: duckalog
  ```

  or by using a small number of `::: duckalog.specific_module` blocks for better structure.
- Remove or drastically reduce hand‑written per‑function descriptions that duplicate docstrings.
- Ensure mkdocstrings configuration in `mkdocs.yml` remains compatible (already set to `docstring_style: google`).

### 5. Validation

- Build the docs (`mkdocs build`) and verify:
  - All public APIs appear with clear, structured docstrings.
  - Examples render correctly and remain readable.
- Optionally run a lightweight static check (or grep‑style audit) to ensure no obvious public symbols are missing docstrings.

## Impact

- **Users** get up‑to‑date, complete API documentation directly from the code.
- **Maintainers** only need to update docstrings when APIs change; docs stay in sync automatically.
- **Doc quality** improves via examples and consistent formatting.

## Non‑Goals

- No changes to runtime behavior or function signatures.
- No changes to the Diátaxis structure itself (handled by separate documentation refinement changes).
- No introduction of doctest enforcement or CI checks for examples (can be a future change).

