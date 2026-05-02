# Code Context — catalog-studio-attachments-secrets-editor

## Files Retrieved

### Configuration Models (attachments + secrets)

1. `src/duckalog/config/models.py` (lines 1-350)
   - `SecretConfig` (lines 20-110) — canonical unified secret model
   - `DuckDBAttachment` (lines 197-213)
   - `SQLiteAttachment` (lines 214-227)
   - `PostgresAttachment` (lines 228-253)
   - `DuckalogAttachment` (lines 254-285)
   - `AttachmentsConfig` (lines 287-307)
   - `ViewConfig` (lines 351-450+) — reference for how form editing helpers are structured

2. `src/duckalog/sql_generation.py` (lines 1-300)
   - `generate_secret_sql()` (lines 233-290) — maps `SecretConfig` → `CREATE SECRET` SQL
   - Provider-specific helpers: `_build_s3_params`, `_build_azure_params`, `_build_gcs_params`, `_build_http_params`, `_build_postgres_params`, `_build_mysql_params` (lines 113-230)

3. `src/duckalog/engine.py` (lines 785-1000)
   - `_setup_attachments()` (lines 785-867) — translates attachment models to DuckDB `ATTACH DATABASE` SQL
   - `_create_secrets()` (lines 645-752) — translates `SecretConfig` list to SQL via `generate_secret_sql()`
   - `_apply_catalog_state()` (lines 963-1000) — shared state application helper

4. `src/duckalog/config/validators.py` (lines 1-100)
   - Redaction utilities: `_redact_value()`, `log_info()`, `log_debug()`, `log_warning()`, `log_error()`
   - `SENSITIVE_KEYWORDS = ("password", "secret", "token", "key", "pwd")`
   - Keys matching `SENSITIVE_KEYWORDS` get value `"***REDACTED***"` in logs

5. `tests/test_config.py` (lines 1692-1834)
   - Tests for `DuckalogAttachment` validation (required alias, required config_path, empty-value rejection)

6. `tests/test_engine_hierarchical.py` (lines 481-566)
   - Tests for `DuckalogAttachment` required-field validation

7. `tests/test_sql_generation.py` (lines 218-460)
   - Tests for `generate_secret_sql()` across all providers

8. `tests/test_sql_security.py` (lines 117-240)
   - SQL injection tests for secret values, options type enforcement

9. `tests/test_engine_cli.py` (lines 85-196, 314-345)
   - Attachment integration tests including Postgres attachment setup

10. `tests/test_config_imports.py` (lines 377-630)
    - Duplicate attachment alias detection, import merging for attachments

11. `tests/test_path_resolution.py` (lines 403-550)
    - Attachment path resolution tests

12. `docs/reference/config-schema.md` (lines 353-450)
    - `AttachmentsConfig` and per-attachment field tables

13. `docs/reference/config-schema.md` (lines 108-175)
    - `SecretConfig` field tables by type

14. `docs/SECURITY.md` (lines 1-200)
    - SQL injection protection, secret option type enforcement, redaction, `<REDACTED>` logging

15. `plan/PRD_Spec.md` (lines 410-470, 569-700)
    - `SecretConfig` provider-specific required fields, `AttachmentsConfig` spec, setup functions

16. `.execflow/plans/catalog-studio-view-lifecycle/execplan.md` (lines 1-260)
    - Predecessor plan; shows the pattern this plan must follow

17. `.execflow/plans/catalog-studio-editing-safety/execplan.md` (lines 1-300)
    - Defines the safety service that this plan's UI routes must call

18. `.execflow/plans/catalog-studio-form-editor/execplan.md` (lines 1-200)
    - Defines the structured form editor that this plan extends

## Key Code

### SecretConfig validator (provider-specific required fields)

```python
# src/duckalog/config/models.py:81-110
@model_validator(mode="after")
def _validate_secret_fields(self) -> "SecretConfig":
    if self.type == "s3":
        if self.provider == "config":
            if not self.key_id or not self.secret:
                raise ValueError("S3 config provider requires key_id and secret")
    elif self.type == "azure":
        if self.provider == "config":
            if not self.connection_string
                and not (self.tenant_id and self.account_name)
                and not (self.tenant_id and self.client_id and self.client_secret):
                raise ValueError(...)
    elif self.type == "gcs":
        if self.provider == "config":
            if not (self.service_account_key or self.json_key
                    or (self.key_id and self.secret)):
                raise ValueError(...)
    elif self.type == "http":
        if not self.bearer_token:
            raise ValueError("HTTP secret requires bearer_token")
    elif self.type in {"postgres", "mysql"}:
        if not self.connection_string and not (
            self.host and self.database
            and (self.user or self.key_id)
            and (self.password or self.secret)
        ):
            raise ValueError(...)
    return self
```

### Attachment SQL generation

```python
# src/duckalog/engine.py:785-867
def _setup_attachments(conn, config, verbose):
    # DuckDB
    for duckdb_attachment in config.attachments.duckdb:
        clause = " (READ_ONLY)" if duckdb_attachment.read_only else ""
        conn.execute(f"ATTACH DATABASE {quote_literal(duckdb_attachment.path)} "
                    f"AS {quote_ident(duckdb_attachment.alias)}{clause}")

    # SQLite
    for sqlite_attachment in config.attachments.sqlite:
        conn.execute(f"ATTACH DATABASE {quote_literal(sqlite_attachment.path)} "
                    f"AS {quote_ident(sqlite_attachment.alias)} (TYPE SQLITE)")

    # Postgres
    for pg_attachment in config.attachments.postgres:
        clauses = ["TYPE POSTGRES",
                   f"HOST {quote_literal(pg_attachment.host)}",
                   f"PORT {pg_attachment.port}",
                   f"USER {quote_literal(pg_attachment.user)}",
                   f"PASSWORD {quote_literal(pg_attachment.password)}",  # REDACTED in debug log
                   f"DATABASE {quote_literal(pg_attachment.database)}"]
        # sslmode, options, connect_timeout appended
        conn.execute(f"ATTACH DATABASE ... ({clause_sql})")

    # Duckalog child attachments: handled separately in _apply_catalog_state()
```

### Redaction in Postgres attachment

```python
# src/duckalog/engine.py:837-843
log_debug(
    "Postgres attachment details",
    alias=pg_attachment.alias,
    user=pg_attachment.user,
    password="<REDACTED>",  # hard-coded redaction
    options=pg_attachment.options,
)
```

### General redaction helpers

```python
# src/duckalog/config/validators.py:28-79
SENSITIVE_KEYWORDS = ("password", "secret", "token", "key", "pwd")

def _is_sensitive(key: str) -> bool:
    lowered = key.lower()
    return any(kw in lowered for kw in SENSITIVE_KEYWORDS)

def _redact_value(value: Any, key_hint: str = "") -> Any:
    if isinstance(value, dict):
        return {k: _redact_value(v, k) for k, v in value.items()}
    if isinstance(value, str) and _is_sensitive(key_hint):
        return "***REDACTED***"
    return value

def log_info(msg: str, **details: Any) -> None:
    # calls _redact_value on all details before logging
```

### generate_secret_sql — public API

```python
# src/duckalog/sql_generation.py:233-290
def generate_secret_sql(secret: SecretConfig) -> str:
    params = [f"TYPE {secret.type.upper()}"]
    if secret.provider == "credential_chain":
        params.append("PROVIDER credential_chain")
    type_builders = {
        "s3": _build_s3_params,
        "azure": _build_azure_params,
        "gcs": _build_gcs_params,
        "http": _build_http_params,
        "postgres": _build_postgres_params,
        "mysql": _build_mysql_params,
    }
    builder = type_builders.get(secret.type)
    if builder is not None:
        params.extend(builder(secret))
    # options type check (bool/int/float/str only)
    secret_sql = f"CREATE {'PERSISTENT ' if secret.persistent else ''}SECRET {name} (...)"
    if secret.scope:
        secret_sql += f"; SCOPE {quote_literal(secret.scope)}"
    return secret_sql
```

### Config structure

```yaml
# Attachment shape in config YAML
attachments:
  duckdb:
    - alias: ref
      path: ./ref.duckdb
      read_only: true
  sqlite:
    - alias: legacy
      path: ./legacy.db
  postgres:
    - alias: wh
      host: db.example.com
      port: 5432
      database: analytics
      user: readonly
      password: "${env:PG_PASSWORD}"
      sslmode: require
  duckalog:
    - alias: child
      config_path: ./child.yaml
      read_only: true

# Secret shape (nested under duckdb)
duckdb:
  secrets:
    - type: s3
      name: prod_s3
      key_id: "${env:AWS_KEY_ID}"
      secret: "${env:AWS_SECRET}"
      scope: prod/
```

## Architecture

### Config tree (attachments + secrets)

```
Config
├── duckdb: DuckDBConfig
│   └── secrets: list[SecretConfig]        ← secrets live under duckdb
└── attachments: AttachmentsConfig         ← separate top-level section
    ├── duckdb: list[DuckDBAttachment]
    ├── sqlite: list[SQLiteAttachment]
    ├── postgres: list[PostgresAttachment]
    └── duckalog: list[DuckalogAttachment]
```

Key structural difference: secrets are a list under `duckdb.secrets`; attachments are a separate top-level `attachments` dict with four typed sub-lists.

### SQL generation pipeline for attachments

```
AttachmentsConfig → _setup_attachments() → DuckDB ATTACH DATABASE SQL
```

Each attachment type maps to different DuckDB syntax:
- DuckDB: `ATTACH DATABASE '<path>' AS <alias> (READ_ONLY)`
- SQLite: `ATTACH DATABASE '<path>' AS <alias> (TYPE SQLITE)`
- Postgres: `ATTACH DATABASE '<db>' AS <alias> (TYPE POSTGRES, HOST ..., PORT ..., USER ..., PASSWORD ..., DATABASE ...)`
- Duckalog: separate two-phase build (child catalog → ATTACH with resolved path)

### SQL generation pipeline for secrets

```
list[SecretConfig] → _create_secrets() → generate_secret_sql() per secret
```

Secrets are executed before attachments in `_apply_catalog_state()` to ensure credentials are available for remote attachments.

### Redaction/logging layer

```
log_info / log_debug / log_warning / log_error
  → _redact_value(details)   # keys matching SENSITIVE_KEYWORDS → "***REDACTED***"
  → _emit_loguru_logger()
```

Postgres `password` in `_setup_attachments()` uses hard-coded `"<REDACTED>"` string. Other sensitive fields are caught by `_is_sensitive()` keyword matching.

### Form editing pipeline (pattern from predecessor plans)

```
draft (raw text + format)
  → build_proposed_*_text(draft, values)     # parse YAML/JSON dict, modify section, serialize
  → validate_config_text(proposed_text, format, base_path)
  → preview_config_diff(original_text, proposed_text, path)
  → save_config_text_safely(path, proposed_text)   # backup + atomic write + reload verify
```

The safety service (`editing.py`) is the mandatory intermediary for all writes. Helpers are pure Python; only routes call the service + StarHTML.

## Key Observations for This Plan

1. **No `src/duckalog/studio/` package exists yet.** The predecessor plans (editing-safety → expert-editor → form-editor → view-lifecycle) have execplans but haven't been implemented. `studio/` must be created first before this plan can extend it. The prerequisite chain must complete before this plan starts.

2. **Two distinct config sections need forms**: `attachments` (top-level, 4 typed sub-lists) and `duckdb.secrets` (nested under `duckdb`). These are structurally separate in the Config model. Both need add/duplicate/rename/delete helpers, plus edit helpers for existing entries.

3. **Provider-specific required fields in SecretConfig**: The validator at lines 81-110 enforces required-field sets per secret type and provider. Form validation must surface these errors per type before attempting `Config.model_validate()`.

4. **Redaction is a UI concern too**: Password and secret values must not appear in diffs, log output, or UI previews. The `_redact_value()` utility already exists but must be applied in the form editor's preview diff generation — the raw text diff may expose secrets in YAML comments or inline values.

5. **`DuckalogAttachment` requires two-phase build**: The child catalog must be built first to resolve `config_path` → `database_path`, then the ATTACH is issued with the resolved path. This is different from the other three attachment types. The form editor must handle this as a special case.

6. **Secret type affects SQL generation complexity**: S3, Azure, GCS, HTTP, Postgres, MySQL — each has different parameter builders. Form prefill should default based on `type`, which drives which fields are shown.

7. **`sql_file`/`sql_template` inlining risk**: Normal config loading inlines SQL file references. The editing pipeline must use `yaml.safe_load()`/`json.loads()` and serialize the raw dict back, NOT `Config.model_dump()`.

8. **View lifecycle plan is the immediate predecessor**: catalog-studio-view-lifecycle is the plan that actually implements the `studio/` package. This attachments/secrets plan should build on top of it, not parallel to it.

## Start Here

1. **Confirm the predecessor chain is implemented first:**
   ```bash
   ls src/duckalog/studio/  # must contain: editing.py, form_editing.py, view_lifecycle.py
   uv run pytest tests/test_studio_view_lifecycle.py -q  # must pass
   ```
   If `studio/` doesn't exist, this plan cannot proceed — implement the predecessor chain first.

2. **Read the view-lifecycle context** at `.execflow/plans/catalog-studio-view-lifecycle/context.md` for the full pattern this plan should follow.

3. **Read the editing safety service** at `src/duckalog/studio/editing.py` once it exists to understand the exact `validate_config_text()`, `preview_config_diff()`, `save_config_text_safely()` signatures.

4. **Read the `AttachmentsConfig` and `SecretConfig` models** at `src/duckalog/config/models.py:20-307` to understand all fields, validators, and defaults before designing the form fields.

5. **Read the attachment SQL generation** at `src/duckalog/engine.py:785-867` to understand the four ATTACH variants before designing form prefill behavior.

6. **Read the secret SQL generation** at `src/duckalog/sql_generation.py:113-290` to understand provider-specific parameter building before designing secret-type-aware forms.

## Pi-intercom handoff

No `intercom` tool is available. The `studio/` package doesn't exist yet — the predecessor plan (catalog-studio-view-lifecycle) is the first to create it. This plan should not start until the full predecessor chain (editing-safety → expert-editor → form-editor → view-lifecycle) is implemented and tests pass. Once that's confirmed, the studio package provides `editing.py`, `form_editing.py`, and `view_lifecycle.py` as the foundation for this attachments/secrets editor.
