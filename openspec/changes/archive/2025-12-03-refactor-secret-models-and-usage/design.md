# Design: Canonical SecretConfig Model

## Goals

- Establish `SecretConfig` as the single configuration model for secrets.
- Keep the mapping from configuration to DuckDB `CREATE SECRET` clear and maintainable.
- Avoid duplicated type definitions that can drift or confuse contributors.

## Canonical model shape

`SecretConfig` is a discriminated union keyed by `type`, with optional fields used by specific backends. At a high level:

```python
class SecretConfig(BaseModel):
    name: str
    type: Literal["s3", "azure", "gcs", "http", "postgres", "mysql"]
    persistent: bool = False
    scope: str | None = None

    # Shared / common fields
    key_id: str | None = None
    secret: str | None = None
    connection_string: str | None = None

    # Backend-specific fields (examples)
    region: str | None = None          # s3
    endpoint: str | None = None        # s3
    account_name: str | None = None    # azure
    host: str | None = None            # postgres/mysql
    port: int | None = None
    database: str | None = None
    user: str | None = None
    password: str | None = None

    options: dict[str, bool | int | float | str] | None = None
```

The exact field list will be finalized during spec alignment, but the key properties are:

- One config model covers all secret types.
- Fields are optional and interpreted according to `type`.
- This model matches how `generate_secret_sql` builds DuckDB `CREATE SECRET` statements.

## Backend-specific helpers

Backend-specific models (for example, `S3SecretConfig`) may still be useful:

- For internal ergonomics in the engine or SQL generation layers.
- For mapping higher-level configuration into a `SecretConfig` instance.

However:

- They should live in a single module (for example, `secret_types.py`).
- They should NOT be used directly as configuration models or appear in public docs.
- They should be regarded as implementation details that can change without breaking user configs.

## Mapping to DuckDB CREATE SECRET

The mapping from `SecretConfig` to DuckDB SQL is:

- Driven solely by `SecretConfig`’s fields and `type`.
- Implemented in `generate_secret_sql(secret: SecretConfig)`.
- Covered by tests for each backend type, ensuring:
  - All documented fields produce the expected parameters.
  - Unsupported combinations either behave predictably or fail with clear exceptions.

The design from `update-sql-quoting-and-secrets-safety` (quoting rules, allowed option types) applies here as well.

## Migration considerations

- Any code that currently imports backend-specific secret models from `config.py` should be updated to:
  - Import from `secret_types.py` (if still needed internally), or
  - Use `SecretConfig` directly.
- Tests referencing removed models should be updated to use `SecretConfig` or the internal helper models from their new location.

