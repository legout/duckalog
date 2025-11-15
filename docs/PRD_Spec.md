# duckalog – Product Requirements & Technical Specification

## 0. Document Status

- **Version:** 1.0 (conceptual)
- **Scope:** Python library + CLI to build DuckDB catalogs (views) from declarative YAML/JSON configs.
- **Core Features:**
  - Views over S3 Parquet.
  - Credentials via environment variables.
  - Views over Delta Lake and Iceberg tables (with Iceberg catalog support).
  - Attach and use other DuckDB files, SQLite databases, and Postgres databases.
  - Config-driven, reproducible catalog creation.

---

## 1. Product Requirements Document (PRD)

### 1.1. Summary

`duckalog` is a **Python library and CLI** that:

- Reads a **YAML or JSON configuration** describing:
  - DuckDB database file location and session settings.
  - External attachments (other DuckDB files, SQLite DBs, Postgres DBs).
  - Iceberg catalogs.
  - Views over:
    - S3 Parquet datasets.
    - Delta Lake tables.
    - Iceberg tables.
    - Attached DuckDB/SQLite/Postgres tables.
    - Raw SQL queries.
- Optionally resolves **credentials via environment variables**.
- Connects to DuckDB and **creates/updates views** in a `.duckdb` catalog.
- Can **generate a SQL script** with the `CREATE VIEW` statements instead of touching the DB.
- Is **idempotent**: rerunning with the same config yields the same catalog.

This enables teams to treat their DuckDB catalog as code: versioned, reproducible, and portable.

---

### 1.2. Problem Statement

Teams using DuckDB with S3 and various lakehouse / warehouse sources typically need:

- A **repeatable** way to define which datasets are available in DuckDB.
- A **single source of truth** for view definitions.
- A way to **share a DuckDB catalog file** that is consistent across machines/environments.
- A unified way to **mix multiple backends**:
  - S3 Parquet.
  - Delta Lake and Iceberg.
  - Postgres / SQLite / other DuckDB files.
- A way to **avoid hard-coding credentials** in configs.

Current pain points:

- Ad-hoc notebooks or scripts with scattered `CREATE VIEW` SQL.
- Fragile or manual setup for S3, Delta, Iceberg, and Postgres connections.
- Duplication of connection details across different scripts.
- Risk of committing secrets to Git.

---

### 1.3. Goals & Non-Goals

#### 1.3.1. Goals

1. **Config-driven catalog definition**  
   Catalogs are defined in declarative YAML/JSON configs (views, attachments, catalogs, pragmas).

2. **DuckDB + multi-source**  
   Support views built on:
   - S3 Parquet datasets.
   - Delta Lake tables.
   - Iceberg tables (via paths or catalogs).
   - Attached DuckDB, SQLite, and Postgres databases.
   - Arbitrary SQL.

3. **Reproducibility & portability**  
   Catalogs are reproducible across environments given the config and consistent environment variables.

4. **Safe credential handling**  
   Config can refer to environment variables (e.g. `${env:AWS_ACCESS_KEY_ID}`) instead of embedding secrets.

5. **CLI + Python API**  
   Provide:
   - CLI commands for build/validate/generate-sql.
   - Python functions for embedding in pipelines/apps.

6. **Validation & clear errors**  
   Schema validation and meaningful error messages for:
   - Config issues.
   - Missing env variables.
   - Failed DuckDB queries or attachments.

7. **Extensibility**  
   Make it easy to add new source types, catalog types, or attachment types without breaking existing configs.

#### 1.3.2. Non-goals (initial versions)

- No UI or web service; this is a **library + CLI**, not a catalog server.
- No full semantic layer (metrics, relationships, etc.).
- No automatic data ingestion; only **logical views**, not ETL/ELT.
- No advanced permissioning; auth is delegated to underlying systems (S3, Postgres, etc.).

---

### 1.4. Target Users / Personas

1. **Data Engineer**
   - Owns data infrastructure.
   - Wants a single YAML/JSON file to define the DuckDB catalog and all attachments.

2. **Analytics Engineer / BI Developer**
   - Maintains semantic definitions in Git.
   - Wants to define canonical views for analysts using DuckDB.

3. **Power User / Data Scientist**
   - Uses DuckDB locally and wants to quickly connect to S3, Postgres, and lakehouse tables via a simple config.

---

### 1.5. Core Use Cases

#### UC-1: Build a catalog from YAML/JSON

> As a data engineer, I want to define my DuckDB catalog in a config file and build/update it with one command.

```bash
duckalog build catalog.yaml
```

**Expected behavior:**

- Reads `catalog.yaml`.
- Resolves `${env:VAR}` placeholders.
- Connects to `duckdb.database` path.
- Sets up extensions, pragmas, attachments, Iceberg catalogs.
- Creates or replaces all views defined in `views`.
- Exits with a non-zero status if any step fails.

---

#### UC-2: Generate SQL script instead of modifying the DB

> As an analytics engineer, I want a SQL script (`create_views.sql`) from the config so I can apply it manually.

```bash
duckalog generate-sql catalog.yaml --output create_views.sql
```

**Expected behavior:**

- Validates config.
- Generates `CREATE OR REPLACE VIEW ...` statements for all views.
- Optionally includes header comments.
- Does not connect to DuckDB.

---

#### UC-3: Validate config

> As a reviewer, I want to ensure config files are valid before merging.

```bash
duckalog validate catalog.yaml
```

**Expected behavior:**

- Parses and validates structure.
- Resolves env placeholders (failing if any required env var is missing).
- Does not connect to DuckDB (by default).
- Prints a clear success or error message.

---

#### UC-4: Use Python API in pipelines

> As a pipeline developer, I want to call the library from Python and build catalogs programmatically.

```python
from duckdb_catalog import build_catalog

build_catalog("catalog.yaml")
```

---

#### UC-5: Views over S3 Parquet

> As a data engineer, I want simple views mapped to S3 Parquet datasets.

```yaml
views:
  - name: users
    source: parquet
    uri: "s3://my-bucket/data/users/*.parquet"
    options:
      hive_partitioning: true
      union_by_name: true
```

---

#### UC-6: Credentials via env vars

> As an engineer, I want to avoid committing secrets and refer to environment variables.

```yaml
duckdb:
  database: my_catalog.duckdb
  pragmas:
    - "SET s3_region='eu-central-1'"
    - "SET s3_access_key_id='${env:AWS_ACCESS_KEY_ID}'"
    - "SET s3_secret_access_key='${env:AWS_SECRET_ACCESS_KEY}'"
```

---

#### UC-7: Attach DuckDB, SQLite, and Postgres

> As a data engineer, I want to attach existing databases and expose their tables.

```yaml
attachments:
  duckdb:
    - alias: refdata
      path: ./refdata.duckdb
      read_only: true

  sqlite:
    - alias: legacy
      path: ./legacy.db

  postgres:
    - alias: dw
      host: "${env:PG_HOST}"
      port: 5432
      database: dw
      user: "${env:PG_USER}"
      password: "${env:PG_PASSWORD}"
      sslmode: require

views:
  - name: dim_country
    source: duckdb
    database: refdata
    table: public.dim_country

  - name: legacy_users
    source: sqlite
    database: legacy
    table: users

  - name: fact_orders
    source: postgres
    database: dw
    table: public.fact_orders
```

---

#### UC-8: Delta Lake and Iceberg tables

> As a lakehouse user, I want views over Delta Lake and Iceberg tables, with Iceberg catalogs.

```yaml
iceberg_catalogs:
  - name: main_ic
    catalog_type: rest
    uri: "https://iceberg-catalog.internal"
    warehouse: "s3://my-warehouse/"
    options:
      token: "${env:ICEBERG_TOKEN}"

views:
  - name: events_delta
    source: delta
    uri: "s3://my-bucket/delta/events"

  - name: ic_orders
    source: iceberg
    catalog: main_ic
    table: analytics.orders
    options:
      snapshot_id: 123456789
```

---

#### UC-9: Raw SQL views

> As a power user, I want to define arbitrary SQL-based views.

```yaml
views:
  - name: vip_users
    sql: |
      SELECT *
      FROM users
      WHERE is_vip = TRUE
```

---

### 1.6. Functional Requirements

#### FR-1: Config formats

- MUST support:
  - YAML (`.yml`, `.yaml`).
  - JSON (`.json`).
- MUST define a versioned schema (`version` field).
- MUST validate configs before attempting to build.

---

#### FR-2: DuckDB configuration

Config MUST allow:

- `duckdb.database` (path, default `:memory:`).
- `duckdb.install_extensions` (list of extensions to install).
- `duckdb.load_extensions` (list of extensions to load).
- `duckdb.pragmas` (list of SQL strings to run after connecting).

---

#### FR-3: Views

Each view:

- MUST have:
  - `name` (unique).
- MUST have exactly one of:
  - `sql` (raw SQL defining the view).
  - `source` + required fields for that source.

Support `source` types:

- `parquet`
- `delta`
- `iceberg`
- `duckdb`
- `sqlite`
- `postgres`

With fields:

- `parquet`:
  - `uri` (required).
  - `options` (optional map).

- `delta`:
  - `uri` (required).
  - `options` (optional map).

- `iceberg`:
  - EITHER:
    - `uri` (path-based).
  - OR:
    - `catalog` (Iceberg catalog name).
    - `table` (fully qualified).
  - `options` (optional map).

- `duckdb` / `sqlite` / `postgres`:
  - `database` (alias from `attachments`).
  - `table` (e.g. `schema.table`).

---

#### FR-4: Attachments

Config MUST support an `attachments` section:

- `attachments.duckdb[]`:
  - `alias`, `path`, optional `read_only`.

- `attachments.sqlite[]`:
  - `alias`, `path`.

- `attachments.postgres[]`:
  - `alias`, `host`, `port`, `database`, `user`, `password`, optional `sslmode`, `options`.

Engine MUST:

- Attach each configured DB before view creation.
- Error clearly if an attachment fails.

---

#### FR-5: Iceberg catalogs

Config MUST support an `iceberg_catalogs` section:

- Each catalog:
  - `name` (unique).
  - `catalog_type` (string, e.g. `rest`, `hive`, `glue`).
  - `uri` (optional; depends on type).
  - `warehouse` (optional).
  - `options` (optional key/value map).

Engine MUST:

- Configure/attach Iceberg catalogs before views that rely on them.
- Error if a view references a non-existent `catalog`.

---

#### FR-6: Environment variable interpolation

- Strings MAY contain `${env:VAR_NAME}` placeholders.
- Library MUST resolve these with `os.environ["VAR_NAME"]`.
- If variable is missing, MUST raise a clear `ConfigError`.
- MUST avoid logging resolved secret values at INFO level.

---

#### FR-7: CLI Commands

Provide a CLI (e.g., `duckalog`) with commands:

- `build <config>`:
  - Options:
    - `--db-path` override.
    - `--dry-run` (print SQL only).
    - `--verbose`.

- `generate-sql <config>`:
  - Options:
    - `--output` (default `-` for stdout).

- `validate <config>`:
  - Validates and prints success or errors.
  - Exit code non-zero on failure.

---

#### FR-8: Python API

At minimum:

- `build_catalog(config_path: str, db_path: Optional[str] = None, dry_run: bool = False, verbose: bool = False) -> None`
- `generate_sql(config_path: str) -> str`
- `validate_config(config_path: str) -> None` (raises on invalid).

---

### 1.7. Non-functional Requirements

- **Language:** Python 3.9+.
- **Dependencies:**
  - `duckdb` Python package.
  - `pyyaml` for YAML.
  - `pydantic` (or equivalent) for validation (recommended).
- **Performance:**
  - Optimized for configs with tens to hundreds of views.
- **Reliability:**
  - Idempotent for given config and environment variables.
  - Clear logging and error messages.
- **Security:**
  - Support env-based credentials.
  - Avoid logging secret values by default.

---

### 1.8. Milestones / Versions

- **v0.1 (MVP):**
  - YAML/JSON configs.
  - Views over Parquet (`source: parquet`).
  - DuckDB config (extensions, pragmas).
  - CLI: `build`, `generate-sql`, `validate`.

- **v0.2:**
  - Env interpolation.
  - Attachments: DuckDB, SQLite, Postgres.
  - Additional sources: `delta`, `duckdb`, `sqlite`, `postgres`.

- **v0.3:**
  - Iceberg catalogs + `source: iceberg`.
  - Better logging & error messages.
  - CI tests.

---

## 2. Technical Specification

### 2.1. High-Level Architecture

Modules:

- `config.py` – loading and env interpolation.
- `model.py` – Pydantic models for config schema.
- `engine.py` – DuckDB connection, attachments, catalogs, view execution.
- `sqlgen.py` – SQL generation from view definitions.
- `cli.py` – CLI entrypoint (arg parsing, command dispatch).
- `errors.py` – custom exception types.
- `logging.py` – logging helpers.

---

### 2.2. Package Layout (Conceptual)

```text
duckdb_catalog/
  __init__.py
  cli.py
  config.py
  model.py
  engine.py
  sqlgen.py
  errors.py
  logging.py
  version.py
tests/
  test_config.py
  test_sqlgen.py
  test_engine.py
  test_env_interpolation.py
```

---

### 2.3. Config Loading & Environment Interpolation

#### 2.3.1. `load_config(path: str) -> Config`

Steps:

1. Read file as text.
2. Depending on extension, parse:
   - YAML via `yaml.safe_load`.
   - JSON via `json.loads`.
3. Run `interpolate_env(raw_dict)` to resolve `${env:VAR}` placeholders.
4. Initialize Pydantic `Config` model.
5. Return `Config`, or raise `ConfigError` on parsing/validation failures.

#### 2.3.2. Env interpolation algorithm

- Pattern: `${env:VAR_NAME}` where `VAR_NAME` is `[A-Z0-9_]+`.
- Recursively descend the parsed structure:
  - Dict → traverse values.
  - List → traverse items.
  - String → apply regex substitution.
- On encountering a placeholder:
  - If `VAR_NAME` is not in `os.environ`, raise `ConfigError`.
  - Otherwise replace the placeholder with the actual value.

---

### 2.4. Data Models (`model.py`)

#### 2.4.1. `DuckDBConfig`

```python
class DuckDBConfig(BaseModel):
    database: Optional[str] = ":memory:"
    install_extensions: List[str] = Field(default_factory=list)
    load_extensions: List[str] = Field(default_factory=list)
    pragmas: List[str] = Field(default_factory=list)
```

---

#### 2.4.2. Attachments

```python
class DuckDBAttachmentConfig(BaseModel):
    alias: str
    path: str
    read_only: bool = True

class SQLiteAttachmentConfig(BaseModel):
    alias: str
    path: str

class PostgresAttachmentConfig(BaseModel):
    alias: str
    host: str
    port: int = 5432
    database: str
    user: str
    password: str
    sslmode: Optional[str] = None
    options: Dict[str, object] = Field(default_factory=dict)

class AttachmentsConfig(BaseModel):
    duckdb: List[DuckDBAttachmentConfig] = Field(default_factory=list)
    sqlite: List[SQLiteAttachmentConfig] = Field(default_factory=list)
    postgres: List[PostgresAttachmentConfig] = Field(default_factory=list)
```

---

#### 2.4.3. Iceberg Catalogs

```python
class IcebergCatalogConfig(BaseModel):
    name: str
    catalog_type: str
    uri: Optional[str] = None
    warehouse: Optional[str] = None
    options: Dict[str, object] = Field(default_factory=dict)
```

---

#### 2.4.4. Views

```python
class ViewConfig(BaseModel):
    name: str

    source: Optional[Literal[
        "parquet",
        "delta",
        "iceberg",
        "duckdb",
        "sqlite",
        "postgres",
    ]] = None

    uri: Optional[str] = None
    options: Dict[str, object] = Field(default_factory=dict)

    database: Optional[str] = None  # attachment alias
    table: Optional[str] = None     # schema.table or table

    catalog: Optional[str] = None   # Iceberg catalog name

    sql: Optional[str] = None

    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

    @root_validator
    def validate_view_definition(cls, values):
        sql = values.get("sql")
        source = values.get("source")
        uri = values.get("uri")
        database = values.get("database")
        table = values.get("table")
        catalog = values.get("catalog")

        if sql:
            # Raw SQL must stand alone
            if any([source, uri, database, table, catalog]):
                raise ValueError("When 'sql' is provided, do not set source/uri/database/table/catalog.")
            return values

        if not source:
            raise ValueError("'source' is required when 'sql' is not provided.")

        if source in ("parquet", "delta"):
            if not uri:
                raise ValueError(f"'uri' is required for source='{source}'")

        if source == "iceberg":
            if uri and (catalog or table):
                raise ValueError("For iceberg, use either 'uri' OR ('catalog' + 'table').")
            if not uri and not (catalog and table):
                raise ValueError("For iceberg, specify 'uri' OR 'catalog'+'table'.")

        if source in ("duckdb", "sqlite", "postgres"):
            if not (database and table):
                raise ValueError(f"'database' and 'table' required for source='{source}'")

        return values
```

---

#### 2.4.5. Root Config

```python
class Config(BaseModel):
    version: int
    duckdb: DuckDBConfig
    views: List[ViewConfig]
    attachments: AttachmentsConfig = AttachmentsConfig()
    iceberg_catalogs: List[IcebergCatalogConfig] = Field(default_factory=list)

    @root_validator
    def ensure_unique_view_names(cls, values):
        names = [v.name for v in values.get("views", [])]
        if len(names) != len(set(names)):
            raise ValueError("View names must be unique within a config.")
        return values
```

---

### 2.5. Engine Behavior (`engine.py`)

#### 2.5.1. Open Connection

```python
def open_connection(duckdb_config: DuckDBConfig, override_db_path: Optional[str] = None):
    db_path = override_db_path or duckdb_config.database
    try:
        conn = duckdb.connect(db_path)
    except Exception as e:
        raise EngineError(f"Failed to open DuckDB at {db_path}: {e}") from e

    for ext in duckdb_config.install_extensions:
        conn.execute(f"INSTALL {ext};")

    for ext in duckdb_config.load_extensions:
        conn.execute(f"LOAD {ext};")

    for pragma in duckdb_config.pragmas:
        conn.execute(pragma)

    return conn
```

---

#### 2.5.2. Set up attachments

Conceptual logic:

```python
def setup_attachments(conn, attachments: AttachmentsConfig):
    # DuckDB
    for a in attachments.duckdb:
        readonly_clause = " (READ_ONLY)" if a.read_only else ""
        conn.execute(f"ATTACH '{a.path}' AS {a.alias}{readonly_clause};")

    # SQLite
    for a in attachments.sqlite:
        # Actual syntax may rely on sqlite_scanner extension
        # Example (may vary by DuckDB version):
        conn.execute(f"ATTACH '{a.path}' AS {a.alias} (TYPE SQLITE);")

    # Postgres
    for a in attachments.postgres:
        parts = [
            f"HOST '{a.host}'",
            f"PORT {a.port}",
            f"USER '{a.user}'",
            f"PASSWORD '{a.password}'",
            f"DATABASE '{a.database}'",
        ]
        if a.sslmode:
            parts.append(f"SSLMODE '{a.sslmode}'")
        for k, v in a.options.items():
            parts.append(f"{k.upper()} '{v}'")
        options_sql = ", ".join(parts)
        conn.execute(f"ATTACH '' AS {a.alias} (TYPE POSTGRES, {options_sql});")
```

> Note: actual attach syntax may differ; implementation must adapt to DuckDB’s current API while keeping this intent.

---

#### 2.5.3. Set up Iceberg catalogs

Conceptual:

```python
def setup_iceberg_catalogs(conn, catalogs: List[IcebergCatalogConfig]):
    for cat in catalogs:
        # Real API might be e.g. CALL iceberg_attach('name', 'type', 'uri', 'warehouse', options_json)
        # Here we define the intent:
        options_pairs = []
        if cat.uri:
            options_pairs.append(("uri", cat.uri))
        if cat.warehouse:
            options_pairs.append(("warehouse", cat.warehouse))
        for k, v in cat.options.items():
            options_pairs.append((k, v))
        # Implementation to call the appropriate DuckDB function or pragma.
```

---

### 2.6. SQL Generation (`sqlgen.py`)

#### 2.6.1. Utility

```python
def quote_ident(name: str) -> str:
    return f'"{name}"'

def render_options(opts: Dict[str, object]) -> str:
    parts = []
    for k, v in opts.items():
        if isinstance(v, str):
            val = f"'{v}'"
        elif isinstance(v, bool):
            val = "TRUE" if v else "FALSE"
        else:
            val = str(v)
        parts.append(f"{k}={val}")
    return ", ".join(parts)
```

---

#### 2.6.2. `generate_view_sql(view: ViewConfig) -> str`

Conceptual:

```python
def generate_view_sql(view: ViewConfig) -> str:
    if view.sql:
        body = view.sql.strip()
        return f"CREATE OR REPLACE VIEW {quote_ident(view.name)} AS
{body};"

    src = view.source
    opts = view.options or {}
    opt_sql = render_options(opts)
    opt_clause = f", {opt_sql}" if opt_sql else ""

    if src == "parquet":
        body = f"SELECT * FROM parquet_scan('{view.uri}'{opt_clause})"

    elif src == "delta":
        body = f"SELECT * FROM delta_scan('{view.uri}'{opt_clause})"

    elif src == "iceberg":
        if view.uri:
            body = f"SELECT * FROM iceberg_scan('{view.uri}'{opt_clause})"
        else:
            body = f"SELECT * FROM iceberg_scan('{view.catalog}', '{view.table}'{opt_clause})"

    elif src in ("duckdb", "sqlite", "postgres"):
        body = f"SELECT * FROM {view.database}.{view.table}"

    else:
        raise ValueError(f"Unsupported source type: {src}")

    return f"CREATE OR REPLACE VIEW {quote_ident(view.name)} AS
{body};"
```

---

#### 2.6.3. `generate_all_views_sql(config: Config) -> str`

```python
def generate_all_views_sql(config: Config) -> str:
    lines = [
        "-- Generated by duckalog",
        f"-- Config version: {config.version}",
        ""
    ]
    for view in config.views:
        lines.append(generate_view_sql(view))
        lines.append("")
    return "
".join(lines)
```

---

### 2.7. Build Catalog (`build_catalog`)

```python
def build_catalog(config_path: str,
                  db_path: Optional[str] = None,
                  dry_run: bool = False,
                  verbose: bool = False):
    config = load_config(config_path)

    if dry_run:
        sql = generate_all_views_sql(config)
        print(sql)
        return

    conn = open_connection(config.duckdb, override_db_path=db_path)

    try:
        setup_attachments(conn, config.attachments)
        setup_iceberg_catalogs(conn, config.iceberg_catalogs)

        for v in config.views:
            sql = generate_view_sql(v)
            if verbose:
                print(f"Executing for view {v.name}:
{sql}
")
            conn.execute(sql)
    except Exception as e:
        raise EngineError(f"Failed to apply catalog: {e}") from e
    finally:
        conn.close()
```

---

### 2.8. CLI (`cli.py`)

- Use `argparse` or `click`. Conceptually:

```python
@click.group()
def main():
    ...

@main.command()
@click.argument("config_path")
@click.option("--db-path", default=None)
@click.option("--dry-run", is_flag=True)
@click.option("--verbose", is_flag=True)
def build(config_path, db_path, dry_run, verbose):
    build_catalog(config_path, db_path=db_path, dry_run=dry_run, verbose=verbose)

@main.command("generate-sql")
@click.argument("config_path")
@click.option("--output", "-o", default="-")
def generate_sql_cmd(config_path, output):
    config = load_config(config_path)
    sql = generate_all_views_sql(config)
    if output == "-":
        print(sql)
    else:
        Path(output).write_text(sql)

@main.command()
@click.argument("config_path")
def validate(config_path):
    try:
        load_config(config_path)
        print("Config is valid.")
    except Exception as e:
        click.echo(f"Config is invalid: {e}", err=True)
        raise SystemExit(1)
```

Entry point (in `pyproject.toml`):

```toml
[project.scripts]
duckalog = "duckalog.cli:app"
```

---

### 2.9. Errors & Logging

- `ConfigError`:
  - Invalid file paths.
  - Parse errors.
  - Validation errors.
  - Missing env variables.

- `EngineError`:
  - DuckDB connection failures.
  - Attachment failures.
  - SQL execution failures.

Logging:

- Use Python `logging` module.
- Default INFO level logs high-level operations.
- DEBUG level logs actual SQL (potentially redacted), attachment details (without secrets).

---

### 2.10. Testing Strategy

- **Config tests**:
  - YAML/JSON parsing.
  - Env interpolation behavior.
  - Required/optional fields.
  - Unique view names.

- **SQL generation tests**:
  - Snapshot tests for different sources.
  - Option rendering (booleans, strings, numbers).
  - Edge cases (quoting identifiers).

- **Engine tests (integration)**:
  - Use temporary DuckDB files.
  - Verify that views exist after build.
  - Smoke tests for attachments using simple SQLite/DuckDB files.
  - (Optionally) integration tests with local Postgres (behind a flag).

---

_End of PRD & Technical Spec._
