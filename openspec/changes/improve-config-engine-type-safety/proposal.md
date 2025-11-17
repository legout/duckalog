# Improve Config and Engine Type Safety

## Why

Running mypy on the project (`uv run mypy src/duckalog`) currently surfaces several type issues in the core configuration and engine modules that indicate gaps between the intended models and their actual usage:

- `duckalog.config`:
  - Optional fields (for example, `SQLFileReference | None` and `str | None`) are accessed without checking for `None` (e.g., calling `.path` or `.strip()` on a union), which is both a type error and a potential runtime risk if the validation path changes.
  - `SQLFileLoader` is referenced as `duckalog.config.SQLFileLoader` in type positions, which mypy treats as an invalid type alias pattern.
- `duckalog.engine`:
  - Variables declared as `DuckDBAttachment` are assigned `SQLiteAttachment` and `PostgresAttachment` instances, then treated as if they all had the same attributes (`host`, `database`, `user`, `password`, `options`, etc.).
  - This mismatch shows that our model types for attachments and the engine logic are not aligned and can lead to subtle bugs if attachment shapes change.

These issues don’t appear as immediate runtime failures, but they weaken our type guarantees in the most critical parts of the system: config parsing/validation and engine attachment setup.

## What Changes

- **Config module safety**:
  - Update `duckalog.config` to treat nullable fields more defensively:
    - Check `SQLFileReference | None` before accessing `.path` and raise a clear configuration error when the reference is missing.
    - Normalize or guard `str | None` values before calling string methods like `.strip()`.
  - Replace invalid type references such as `duckalog.config.SQLFileLoader` with valid type annotations:
    - Use the imported `SQLFileLoader` type directly or a string forward reference `"SQLFileLoader"` where necessary.
- **Engine attachment types**:
  - Refine the types used in `duckalog.engine` so that:
    - Attachment variables accurately represent the actual attachment models they can hold (for example, a union of `DuckDBAttachment`, `SQLiteAttachment`, and `PostgresAttachment`, or a common protocol/base type with the required attributes).
    - Accesses to attachment attributes (`host`, `port`, `database`, `user`, `password`, `sslmode`, `options`, etc.) are safe and match the declared models.
  - Ensure the engine’s attachment setup logic respects the shapes defined in the config models and the `config` spec.
- **Spec alignment**:
  - Extend the `config` spec to explicitly require safe handling of optional SQL file references and nullable strings.
  - Extend the `catalog-build` spec to clarify that engine attachment setup must respect the attachment model shapes defined in `config` and avoid relying on attributes that may not exist for a given attachment type.

## Impact

- **Improved reliability**: The engine and config layers will better match their Pydantic model definitions, making it harder to accidentally ship code that dereferences missing fields.
- **Cleaner type-checking**: Mypy will be able to verify more of the core logic, giving earlier feedback when models and usages diverge.
- **Spec clarity**: The `config` and `catalog-build` specs will capture these safety expectations so future changes maintain the same level of defensive behavior.

## Out of Scope

- Changing the public configuration schema beyond what is required to clarify and enforce optional fields.
- Altering the runtime structure of attachments beyond aligning types with existing Pydantic models.
- Modifying CLI or logging behavior (these will be handled separately if needed).

