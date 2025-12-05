# Implementation Tasks: Update API Docstrings for MkDocStrings‑Only Reference

## 1. Define API Scope and Style

- [ ] 1.1 Enumerate the public modules and symbols that should appear in the API reference (e.g. `duckalog.__init__`, `duckalog.config`, `duckalog.engine`, `duckalog.dashboard`).
- [ ] 1.2 Document the official list of public APIs in `openspec/changes/update-api-docstrings-for-mkdocstrings/specs/documentation/api-docstrings.md` (or equivalent spec file).
- [ ] 1.3 Confirm and document that Google‑style docstrings are the standard and outline required sections (summary, Args, Returns, Raises, Examples where applicable).

## 2. Audit Existing Docstrings

- [ ] 2.1 Scan the identified public modules for exported functions, classes, and methods.
- [ ] 2.2 For each public symbol, record whether a docstring exists and whether it follows Google style.
- [ ] 2.3 Mark which symbols need additional examples or clarification.
- [ ] 2.4 Update the spec file with the audit results (e.g. a table of symbol → status).

## 3. Improve and Complete Docstrings

- [ ] 3.1 Add or update docstrings for public functions (e.g. `load_config`, `build_catalog`, `validate_config`, `generate_sql`).
- [ ] 3.2 Add or update docstrings for connection helpers (`connect_to_catalog`, `connect_to_catalog_cm`, `connect_and_build_catalog`) including short usage examples.
- [ ] 3.3 Add or update docstrings for key configuration models and exceptions that form part of the public API.
- [ ] 3.4 Ensure all updated docstrings follow Google‑style conventions and are suitable for direct rendering by mkdocstrings.

## 4. Make API Reference MkDocStrings‑Only

- [ ] 4.1 Simplify `docs/reference/api.md` so that it relies solely on mkdocstrings blocks (e.g. `::: duckalog` or module‑specific sections).
- [ ] 4.2 Remove or minimize any hand‑written per‑API descriptions that duplicate docstring content.
- [ ] 4.3 Verify that the mkdocstrings configuration in `mkdocs.yml` is still correct and aligned with the updated docstrings.

## 5. Validation

- [ ] 5.1 Run `mkdocs build` and ensure the API reference page builds successfully and includes the expected sections.
- [ ] 5.2 Manually review the rendered API reference to confirm readability, section structure, and code examples.
- [ ] 5.3 Optionally run a static check or linter to flag public symbols without docstrings and address any remaining gaps.

