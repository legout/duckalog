# Duckalog

[![PyPI version](https://badge.fury.io/py/duckalog.svg)](https://badge.fury.io/py/duckalog)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/duckalog.svg)](https://pypi.org/project/duckalog/)
[![Tests](https://github.com/legout/duckalog/workflows/Tests/badge.svg)](https://github.com/legout/duckalog/actions)

Duckalog is a Python library and CLI for building DuckDB catalogs from
declarative YAML/JSON configuration files. A single config file describes your
DuckDB database, attachments (other DuckDB files, SQLite, Postgres), Iceberg
catalogs, and views over Parquet/Delta/Iceberg or attached tables.

The goal is to make DuckDB catalogs reproducible, versionable, and easy to
apply in local workflows and automated pipelines.

---

## Features

- **Config-driven catalogs** – Define DuckDB views in YAML/JSON instead of
  scattering `CREATE VIEW` statements across scripts.
- **Multiple sources** – Views over S3 Parquet, Delta Lake, Iceberg tables, and
  attached DuckDB/SQLite/Postgres databases.
- **Attachments & catalogs** – Configure attachments and Iceberg catalogs in
  the same config and reuse them across views.
- **Safe credentials** – Use environment variables (e.g. `${env:AWS_ACCESS_KEY_ID}`)
  instead of embedding secrets.
- **CLI + Python API** – Build catalogs from the command line or from Python
  code with the same semantics.

For a full product and technical description, see `docs/PRD_Spec.md`.

---

## Installation

**Requirements:** Python 3.9 or newer

### Install from PyPI

[![PyPI version](https://badge.fury.io/py/duckalog.svg)](https://pypi.org/project/duckalog/) [![Downloads](https://pepy.tech/badge/duckalog)](https://pepy.tech/project/duckalog)

```bash
pip install duckalog
```

This installs the Python package and provides the `duckalog` CLI command.

### Verify Installation

```bash
duckalog --help
duckalog --version
```

### Alternative Installation Methods

**Development installation:**
```bash
git clone https://github.com/legout/duckalog.git
cd duckalog
pip install -e .
```

**Using uv (recommended for development):**
```bash
uv pip install duckalog
```

---

## Quickstart

### 1. Create a minimal config

Create a file `catalog.yaml`:

```yaml
version: 1

duckdb:
  database: catalog.duckdb
  pragmas:
    - "SET memory_limit='1GB'"

views:
  - name: users
    source: parquet
    uri: "s3://my-bucket/data/users/*.parquet"
```

### 2. Build the catalog via CLI

```bash
duckalog build catalog.yaml
```

This will:

- Read `catalog.yaml`.
- Connect to `catalog.duckdb` (creating it if necessary).
- Apply pragmas.
- Create or replace the `users` view.

### 3. Generate SQL instead of touching the DB

```bash
duckalog generate-sql catalog.yaml --output create_views.sql
```

`create_views.sql` will contain `CREATE OR REPLACE VIEW` statements for all
views defined in the config.

### 4. Validate a config

```bash
duckalog validate catalog.yaml
```

This parses and validates the config (including env interpolation), without
connecting to DuckDB.

---

## Python API

The `duckalog` package exposes the same functionality as the CLI with
convenience functions:

```python
from duckalog import build_catalog, generate_sql, validate_config


# Build or update a catalog file in place
build_catalog("catalog.yaml")


# Generate SQL without executing it
sql = generate_sql("catalog.yaml")
print(sql)


# Validate config (raises ConfigError on failure)
validate_config("catalog.yaml")
```

You can also work directly with the Pydantic model:

```python
from duckalog import load_config

config = load_config("catalog.yaml")
for view in config.views:
    print(view.name, view.source)
```

---

## Configuration Overview

At a high level, configs follow this structure:

```yaml
version: 1

duckdb:
  database: catalog.duckdb
  install_extensions: []
  load_extensions: []
  pragmas: []

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

iceberg_catalogs:
  - name: main_ic
    catalog_type: rest
    uri: "https://iceberg-catalog.internal"
    warehouse: "s3://my-warehouse/"
    options:
      token: "${env:ICEBERG_TOKEN}"

views:
  # Parquet view
  - name: users
    source: parquet
    uri: "s3://my-bucket/data/users/*.parquet"

  # Delta view
  - name: events_delta
    source: delta
    uri: "s3://my-bucket/delta/events"

  # Iceberg catalog-based view
  - name: ic_orders
    source: iceberg
    catalog: main_ic
    table: analytics.orders

  # Attached DuckDB view
  - name: ref_countries
    source: duckdb
    database: refdata
    table: reference.countries

  # Raw SQL view
  - name: vip_users
    sql: |
      SELECT *
      FROM users
      WHERE is_vip = TRUE
```

### Environment variable interpolation

Any string value may contain `${env:VAR_NAME}` placeholders. During
`load_config`, these are resolved using `os.environ["VAR_NAME"]`. Missing
variables cause a `ConfigError`.

Examples:

```yaml
duckdb:
  pragmas:
    - "SET s3_access_key_id='${env:AWS_ACCESS_KEY_ID}'"
    - "SET s3_secret_access_key='${env:AWS_SECRET_ACCESS_KEY}'"
```

---

## Contributing

We welcome contributions to duckalog! This section provides guidelines and instructions for contributing to the project.

### Development Setup

**Requirements:** Python 3.9 or newer

#### Using uv (recommended for development)

```bash
# Clone the repository
git clone https://github.com/legout/duckalog.git
cd duckalog

# Install in development mode
uv pip install -e .
```

#### Using pip

```bash
# Clone the repository
git clone https://github.com/legout/duckalog.git
cd duckalog

# Install in development mode
pip install -e .
```

#### Install development dependencies

```bash
# Using uv
uv pip install -e ".[dev]"

# Using pip
pip install -e ".[dev]"
```

### Coding Standards

We follow the conventions documented in [`openspec/project.md`](openspec/project.md):

- **Python Style**: Follow PEP 8 with type hints on public functions and classes
- **Module Structure**: Prefer small, focused modules over large monoliths
- **Configuration**: Use Pydantic models as the single source of truth for config schemas
- **Architecture**: Separate concerns between config, SQL generation, and engine layers
- **Naming**: Use descriptive, domain-aligned names (e.g., `AttachmentConfig`, `ViewConfig`)
- **Testing**: Keep core logic pure and testable; isolate I/O operations

### Testing

We use pytest for testing. The test suite includes both unit and integration tests:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=duckalog

# Run specific test file
pytest tests/test_config.py
```

**Testing Strategy:**
- **Unit tests**: Config parsing, validation, and SQL generation
- **Integration tests**: End-to-end catalog building with temporary DuckDB files
- **Deterministic tests**: Avoid network dependencies unless explicitly required
- **Test-driven development**: Add tests for new behaviors before implementation

### Change Proposal Process

For significant changes, we use OpenSpec to manage proposals and specifications:

1. **Create a change proposal**: Use the OpenSpec CLI to create a new change
   ```bash
   openspec new "your-change-description"
   ```

2. **Define requirements**: Write specs with clear requirements and scenarios in `changes/<id>/specs/`

3. **Plan implementation**: Break down the work into tasks in `changes/<id>/tasks.md`

4. **Validate your proposal**: Ensure it meets project standards
   ```bash
   openspec validate <change-id> --strict
   ```

5. **Implement and test**: Work through the tasks sequentially

See [`openspec/project.md`](openspec/project.md) for detailed project conventions and the OpenSpec workflow.

### Pull Request Guidelines

When submitting pull requests:

1. **Branch naming**: Use small, focused branches with the OpenSpec change-id (e.g., `add-s3-parquet-support`)

2. **Commit messages**: 
   - Keep spec changes (`openspec/`, `docs/`) and implementation changes (`src/`, `tests/`) clear
   - Reference relevant OpenSpec change IDs in PR titles or first commit messages

3. **PR description**: Include a clear description of the change and link to relevant OpenSpec proposals

4. **Testing**: Ensure all tests pass and add new tests for new functionality

5. **Review process**: Be responsive to review feedback and address all comments

We prefer incremental, reviewable PRs over large multi-feature changes.

### Getting Help

- **Project Documentation**: See [`plan/PRD_Spec.md`](plan/PRD_Spec.md) for the full product and technical specification
- **Project Conventions**: Refer to [`openspec/project.md`](openspec/project.md) for detailed development guidelines
- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/legout/duckalog/issues)
- **Discussions**: Join project discussions on [GitHub Discussions](https://github.com/legout/duckalog/discussions)

Thank you for contributing to duckalog! 🚀

---
