## Why

The repository's `README.md` is currently empty, which makes it hard for new users to understand what Duckalog is, how it relates to the PRD, and how to get started with the CLI and Python API.

A comprehensive README should serve as the single entry point for:
- Understanding the problem Duckalog solves and its core features.
- Installing the package and its dependencies.
- Running common CLI commands (`duckalog build`, `generate-sql`, `validate`).
- Calling the Python API (`build_catalog`, `generate_sql`, `validate_config`).
- Linking out to the PRD and future docs.

## What Changes

- Introduce a `docs` capability spec focused on user-facing documentation starting with the top-level `README.md`.
- Define the required sections for the README:
  - Project overview and core features (aligned with `docs/PRD_Spec.md`).
  - Installation and basic requirements.
  - Quickstart examples for CLI and Python usage.
  - Configuration overview with a minimal example config.
  - Links to PRD/OpenSpec documentation and future MkDocs site.
- Draft and populate `README.md` with concise but comprehensive content following those sections.

## Impact

- Gives users a clear, GitHub-friendly starting point without needing to open the PRD.
- Aligns documentation with the implemented behavior and OpenSpec capabilities.
- Provides a foundation the future MkDocs site can reuse and link back to.

