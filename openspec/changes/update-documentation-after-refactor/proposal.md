# Change: Update Documentation After Major Refactors

## Why
Recent changes to the config layer, engine orchestration, secrets handling, path security, and remote configuration APIs have significantly evolved Duckalog's internal architecture while preserving the public API. The existing documentation—especially `docs/architecture.md` and related guides—still describes the pre-refactor module layout (for example, a single `config.py`, a separate `model.py`, and a `sqlgen.py` module) and does not clearly surface new concepts like the `duckalog.config` package structure, the `CatalogBuilder` orchestration class, updated path security boundaries, or the canonical `SecretConfig` model.

This drift makes it harder for developers and users to understand how the system currently works, how to extend it safely, and how to reason about security-sensitive behavior (secrets, filesystem access, remote config).

## What Changes
- Align the architecture documentation with the current implementation:
  - Describe the `duckalog.config` package (models, loader, interpolation, validators, SQL integration) instead of a monolithic `config.py`/`model.py` split.
  - Document the engine's `CatalogBuilder` orchestration and simplified dependency resolution at a conceptual level.
  - Show how SQL generation (`sql_generation`) and the engine interact, including where path resolution and file loading plug in.
- Surface security- and safety-related behaviors in the docs:
  - Explain the updated path security boundaries and how CLI and remote configuration loaders respect them.
  - Clarify the canonical `SecretConfig` model and how it maps to DuckDB `CREATE SECRET` statements.
  - Connect these behaviors back to the architecture and configuration layers so contributors know where to extend or harden them.
- Ensure user-facing guides and reference docs point to the updated architecture and security model:
  - Cross-link relevant sections from usage guides, path-resolution docs, and the dashboard documentation back to the updated architecture overview.
  - Verify that examples (especially secrets and remote/attached catalogs) are consistent with the canonical config and engine behavior.

## Impact
- Affected specs:
  - `specs/documentation/spec.md` – extend the architecture documentation requirements to cover the refactored config package, engine orchestration, and security-oriented behaviors.
- Affected docs:
  - `docs/architecture.md` – primary architecture and component interaction overview.
  - `docs/index.md` – high-level description and links to architecture and security-related docs.
  - `docs/guides/*.md` – especially `usage.md`, `path-resolution.md`, and `ui-dashboard.md` where they describe how the system fits together.
  - `docs/best-practices-path-management.md`, `docs/path-resolution*.md` – ensure they align with the documented path security boundaries and remote config behavior.
  - `docs/examples/*.md` – ensure secrets and remote catalog examples match the canonical configuration and engine behavior.

