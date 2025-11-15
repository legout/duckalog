## Why

While the PRD and future README provide essential information, there is no structured documentation site with a quickstart, user guide, and API reference.

A MkDocs site using the Material theme and mkdocstrings will:
- Offer a more discoverable, browsable documentation experience.
- Allow us to render API reference pages directly from docstrings.
- Provide space for task-oriented guides and configuration narratives beyond the README.

## What Changes

- Introduce a `docs` capability spec for the documentation site layout and behavior.
- Add MkDocs configuration:
  - Use `mkdocs-material` for theme.
  - Use `mkdocstrings` (Python handler) for API reference pages.
- Create initial documentation pages:
  - `index.md` with a quickstart (CLI + Python snippets).
  - A user guide (e.g., `guides/usage.md`) covering configuration, attachments, Iceberg, and common workflows.
  - An API reference section wired to mkdocstrings for `duckalog`.
- Add dev dependencies for MkDocs and the plugins (e.g., under a `dev` dependency group).

## Impact

- Gives users a full documentation site suitable for hosting (e.g., GitHub Pages).
- Reuses existing docstrings and README content where possible.
- Provides a clear path for expanding docs as new capabilities land.

