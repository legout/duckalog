# Duckalog — Project Roadmap

## Purpose

Duckalog is a Python library and CLI for building DuckDB catalogs from declarative YAML/JSON configs. It provides config-driven connection management, SQL generation, view creation, secret management, and a web UI dashboard — all aimed at making DuckDB analytics reproducible and configurable.

## Current State

**Version 0.5.0** — Beta status, published on PyPI. Duckalog's core catalog-building feature set is already in place, and current local work is focused more on simplification than on major new capabilities.

- **Stable core**: Config-driven catalog builds, SQL generation, connection management, semantic models, secret handling, and remote-config loading are all implemented and exercised.
- **CLI surface is being simplified**: The codebase is actively moving toward a leaner `duckalog run`-first workflow, with deprecated command paths and redundant wrappers being removed.
- **Config internals are being reduced**: Large deprecated modules such as `src/duckalog/config/loader.py` are being deleted in favor of smaller loading and resolution submodules.
- **Dashboard runtime**: The UI app is built on **Litestar + Datastar**; documentation and examples still need cleanup where they refer to older Starlette terminology.
- **Docs/tests are in catch-up mode**: Example commands, remote-config behavior, and deprecation coverage are being aligned with the slimmer public API.

### Architecture

```
src/duckalog/
├── config/           # Models, loading, validation, interpolation, and resolution helpers
├── dashboard/        # Litestar + Datastar web UI
├── cli.py            # Typer CLI surface
├── engine.py         # Catalog builder
├── connection.py     # Connection management
├── python_api.py     # Public Python API wrappers (currently being simplified)
├── sql_generation.py # SQL generation
├── sql_file_loader.py # SQL file loading
└── sql_utils.py      # SQL utility functions
```

## Key Decisions Made

- **Pydantic v2** for config validation and models
- **Typer** for CLI (not plain Click)
- **Litestar + Datastar** for the dashboard runtime; docs still need cleanup where they mention Starlette
- **OpenSpec** for managing change proposals in the repo
- **Python 3.12+** minimum
- Config supports multiple database attachments: DuckDB, SQLite, PostgreSQL, Iceberg
- Semantic layer provides dimensions, measures, and joins
- Ongoing simplification work is intentionally removing deprecated CLI/config surfaces in favor of a smaller `run`-centric API

## Milestones

### Completed

- [x] Core config system with Pydantic models and YAML/JSON loading
- [x] Engine for building DuckDB catalogs from configs
- [x] SQL generation and file loading
- [x] CLI with config init, validation, and SQL generation
- [x] Web UI dashboard with Datastar
- [x] Config-driven connection management
- [x] Secret management (DuckDB secrets)
- [x] Semantic layer v2 (models, dimensions, measures, joins)
- [x] SQL public API organization and discoverability
- [x] Performance benchmark workflow
- [x] Remote config support (S3, GCS, Azure, SFTP)

### Planned

- [ ] Finish the simplification pass by removing deprecated loader/build/init-env surfaces and consolidating duplicated helper logic
- [ ] Update README, examples, and dashboard docs to match Litestar and the `duckalog run` workflow
- [ ] Stabilize and expand tests around remote config handling, CLI behavior, and deprecation boundaries
- [ ] Explore additional DuckDB features/integrations

## Open Questions

- What features should be prioritized for 1.0 stable release?
