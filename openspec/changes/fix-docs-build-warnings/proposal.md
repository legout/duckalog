# Change: Fix Documentation Build Warnings and Navigation Drift

## Why

Running `mkdocs serve` currently produces multiple warnings:

- Pages in `docs/` (including `SECURITY.md`, path resolution guides, and configuration examples) are not listed in `nav`, violating the existing "Eliminate navigation warnings" requirement and making important docs harder to discover.
- All example pages under `docs/examples/` (DuckDB secrets, DuckDB settings, environment variables, attachments, multi-source analytics, path-resolution examples, simple parquet) are missing from the navigation, despite explicit requirements in the `docs` spec to expose these examples via navigation.
- `docs/examples/duckdb-secrets.md` contains outdated relative links (`architecture.md#secret-management-architecture`, `guides/usage.md#secret-management`) that resolve to non-existent targets under `examples/`, generating link warnings and confusing users.
- mkdocstrings/Griffe emits warnings for missing type annotations in `src/duckalog/python_api.py` and `src/duckalog/config/loader.py`, reducing the quality of generated API docs.

These issues create friction for contributors, hide critical security and path-resolution documentation, and violate the current documentation specification.

## What Changes

- **Clarify docs navigation requirements in specs**
  - Extend the `docs` spec to:
    - Explicitly require navigation entries (or a documented alternative structure) for core guides (User Guide usage, path resolution, security) and for all maintained examples under `docs/examples/`.
    - Require that API reference pages included in the docs site build without mkdocstrings/Griffe warnings for public APIs.
- **Update MkDocs navigation to include missing pages**
  - Update `mkdocs.yml` `nav` to:
    - Add a dedicated **Security** page for `docs/SECURITY.md`.
    - Group path-related documents (overview, guide, best practices, configuration examples, migration guide, examples) under the User Guide section so they are reachable via navigation and align with the flattened top-bar structure.
    - Add explicit entries for all example pages in `docs/examples/`, including DuckDB secrets, DuckDB settings, environment variables, local attachments, multi-source analytics, path-resolution examples, and simple parquet.
    - Add a nested entry under **API Reference** for the Python API page (`docs/reference/api.md`).
- **Fix broken and fragile documentation links**
  - Correct relative links in `docs/examples/duckdb-secrets.md` to point to:
    - `../architecture.md#secret-management-architecture`
    - `../guides/usage.md#secret-management`
  - Audit other cross-page links in the touched docs to ensure they resolve correctly after navigation updates.
- **Eliminate mkdocstrings/Griffe type annotation warnings**
  - Update `src/duckalog/python_api.py` so that:
    - Public functions referenced in the API docs have explicit return type annotations.
    - Any variadic parameters documented in the API reference (for example, `**kwargs`) use acceptable annotation patterns or docstring descriptions that satisfy Griffe/mkdocstrings.
  - Update `src/duckalog/config/loader.py` so that:
    - Public functions exported through `duckalog.config` and used by docs have explicit return type annotations.

## Impact

- **Affected specs**
  - `specs/docs/spec.md`:
    - Extend navigation and quality requirements to cover:
      - Core guides (User Guide, security, path resolution, migration).
      - All maintained examples under `docs/examples/`.
      - API reference pages being free of mkdocstrings/Griffe warnings for public APIs.

- **Affected documentation**
  - `mkdocs.yml` navigation structure for:
    - Security documentation.
    - Path resolution and path management guides.
    - Example pages (secrets, settings, environment vars, attachments, multi-source analytics, simple parquet, path resolution examples).
    - API reference index and Python API page.
  - `docs/examples/duckdb-secrets.md` (relative link corrections).

- **Affected code**
  - `src/duckalog/python_api.py`:
    - Add or refine type annotations for public-facing functions used by the docs.
  - `src/duckalog/config/loader.py`:
    - Add or refine return type annotations for loader functions used in the API docs.

## Non-Goals

- No changes to the public API surface (function names, parameters, or behavior) beyond adding type annotations compatible with existing usage.
- No reorganization or deletion of documentation pages; all currently maintained pages under `docs/` are treated as intentional and will be either included in navigation or explicitly linked from a navigable parent page.

