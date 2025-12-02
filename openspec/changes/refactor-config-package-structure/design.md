# Design: Config Package Structure

## Goals

- Split the monolithic `config.py` into a structured package without changing external behavior.
- Make responsibilities explicit and files small enough to navigate quickly.

## Proposed layout

```text
src/duckalog/config/
├── __init__.py        # Public API re-exports
├── models.py          # Pydantic model definitions
├── loader.py          # load_config and local file helpers
├── interpolation.py   # ${env:VAR} handling
├── validators.py      # complex validation helpers
└── sql_integration.py # SQL file loader integration
```

Key principles:

- `models.py` must not import from the other modules to avoid cycles; helper modules import models instead.
- The logic that orchestrates reading from disk/remote, interpolation, and validation lives in `loader.py`, using helpers from `interpolation.py`, `validators.py`, and `sql_integration.py`.
- `__init__.py` re-exports the same names that were previously defined in `config.py` to keep the public surface stable.

## Interaction with other changes

- `update-remote-config-api-contract` defines clearer roles for `load_config` and `load_config_from_uri`; this design locates `load_config` in `loader.py` and keeps `load_config_from_uri` accessible via `duckalog.config`.
- `update-path-security-boundaries` and `update-sql-quoting-and-secrets-safety` define behavior, while this change only moves code into clearer containers; their logic remains intact.

