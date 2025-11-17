## Why

The core library (`src/duckalog`) exposes a set of public classes and functions (e.g., `Config`, `ViewConfig`, `load_config`, `build_catalog`, `generate_sql`) that currently have minimal or no structured docstrings.

Without consistent, example-rich docstrings, it is harder for:
- Users to rely on IDE help and `help()` in Python.
- Future tooling (e.g., MkDocs + mkdocstrings) to generate useful API reference documentation.

## What Changes

- Introduce documentation requirements for public Python APIs, focusing on Google-style docstrings.
- Add or improve docstrings for all public objects exported via `duckalog.__all__`, including:
  - High-level summary.
  - Arguments and return types.
  - Raised exceptions (e.g., `ConfigError`, `EngineError`).
  - Small usage examples where helpful.
- Ensure module-level docstrings describe each module’s responsibility (`config`, `engine`, `sql_generation`, `python_api`, `cli`).

## Impact

- Makes the library self-documenting for interactive users and IDEs.
- Provides a solid foundation for generating API reference pages via mkdocstrings.
- Encourages consistent documentation quality as new public APIs are added.

