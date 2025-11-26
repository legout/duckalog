# Duckalog

[![PyPI version](https://badge.fury.io/py/duckalog.svg)](https://badge.fury.io/py/duckalog)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/duckalog.svg)](https://pypi.org/project/duckalog/)
[![Tests](https://github.com/legout/duckalog/workflows/Tests/badge.svg)](https://github.com/legout/duckalog/actions)
[![codecov](https://codecov.io/gh/legout/duckalog/branch/main/graph/badge.svg)](https://codecov.io/gh/legout/duckalog)
[![Security](https://github.com/legout/duckalog/workflows/Security/badge.svg)](https://github.com/legout/duckalog/actions/workflows/security.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/badge/lint-ruff-blue.svg)](https://github.com/charliermarsh/ruff)

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
  same config and reuse them across views.
- **Semantic layer** – Define business-friendly dimensions and measures on top of existing views for BI and analytics.
- **Safe credentials** – Use environment variables (e.g. `${env:AWS_ACCESS_KEY_ID}`)
  instead of embedding secrets.
- **CLI + Python API** – Build catalogs from command line or from Python
  code with the same semantics.
- **Web UI** – Interactive dashboard for catalog management, query execution, and data export (requires `duckalog[ui]`).

For a full product and technical description, see `docs/PRD_Spec.md`.

**Ready to try examples?** See the [`examples/`](examples/) directory for hands-on learning:

- 📊 **Multi-Source Analytics**: Combine Parquet, DuckDB, and PostgreSQL data
- 🔒 **Environment Variables Security**: Secure credential management patterns
- ⚡ **DuckDB Performance Settings**: Optimize memory, threads, and storage
- 🏷️ **Semantic Layer v2**: Business-friendly semantic models with dimensions and measures

---

## Installation

**Requirements:** Python 3.9 or newer

### Install from PyPI

[![PyPI version](https://badge.fury.io/py/duckalog.svg)](https://pypi.org/project/duckalog/) [![Downloads](https://pepy.tech/badge/duckalog)](https://pepy.tech/project/duckalog)

```bash
pip install duckalog
```

This installs the Python package and provides the `duckalog` CLI command.

### Install with UI support

For the web UI dashboard, install with optional UI dependencies:

```bash
pip install duckalog[ui]
```

#### **UI Dependencies**

The `duckalog[ui]` extra includes these core dependencies:

- **Starlette** (`starlette>=0.27.0`): ASGI web framework
- **Datastar Python SDK** (`datastar-python>=0.1.0`): Reactive web framework
- **Uvicorn** (`uvicorn[standard]>=0.20.0`): ASGI server
- **Background task support**: Built-in Starlette background tasks
- **CORS middleware**: Security-focused web access control

#### **Datastar Runtime Requirements**

The web UI uses **Datastar** for reactive, real-time updates:

- **No legacy fallback**: The UI exclusively uses Datastar patterns
- **Reactive data binding**: Automatic UI updates when data changes
- **Server-Sent Events**: Real-time communication for background tasks
- **Modern web patterns**: Built-in security and performance optimizations
- **Bundled assets**: Datastar v1.0.0-RC.6 is served locally for offline operation
- **Supply chain security**: No external CDN dependencies for the UI

The bundled Datastar JavaScript is served from `/static/datastar.js` and works offline without external network access.

#### **Optional Enhanced YAML Support**

For better YAML formatting preservation, install optional dependency:

```bash
pip install duckalog[ui,yaml]
# or
pip install ruamel.yaml>=0.17.0
```

This provides:
- **Comment preservation** in YAML configs
- **Formatting maintenance** during updates
- **Advanced YAML features** like anchors and aliases

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

This parses and validates config (including env interpolation), without
connecting to DuckDB.

### 5. Explore Examples

```bash
# Try multi-source analytics
cd examples/data-integration/multi-source-analytics
python data/generate.py
duckalog build catalog.yaml

# Try environment variables security
cd examples/production-operations/environment-variables-security
python generate-test-data.py
python validate-configs.py dev

# Try DuckDB performance tuning
cd examples/production-operations/duckdb-performance-settings
python generate-datasets.py --size small
duckalog build catalog-limited.yaml
```

### 6. Start the web UI

```bash
duckalog ui catalog.yaml
```

This starts a secure, reactive web-based dashboard at http://127.0.0.1:8000 with:

#### **Core Features**
- **View Management**: Create, edit, and delete catalog views
- **Query Execution**: Run SQL queries with real-time results
- **Data Export**: Export data as CSV, Excel, or Parquet
- **Schema Inspection**: View table and view schemas
- **Catalog Rebuild**: Rebuild catalog with updated configuration
- **Semantic Layer Explorer**: Browse semantic models with business-friendly labels
- **Model Details**: View dimensions and measures with expressions and descriptions

#### **Security Features**
- **Read-Only SQL Enforcement**: Only allows SELECT queries, blocks DDL/DML
- **Authentication**: Admin token protection for mutating operations (production mode)
- **CORS Protection**: Restricted to localhost origins by default
- **Background Task Processing**: Non-blocking database operations
- **Configuration Security**: Atomic, format-preserving config updates

#### **Technical Implementation**
- **Reactive UI**: Built with Datastar for real-time updates
- **Background Processing**: All database operations run in background threads
- **Format Preservation**: Maintains YAML/JSON formatting when updating configs
- **Error Handling**: Comprehensive security-focused error messages

#### **Production Deployment**
```bash
# Set admin token for production security
export DUCKALOG_ADMIN_TOKEN="your-secure-random-token"
duckalog ui catalog.yaml --host 0.0.0.0 --port 8000
```

**Dependencies**: Requires `duckalog[ui]` installation for Datastar and Starlette dependencies.

**Security**: See [docs/SECURITY.md](docs/SECURITY.md) for comprehensive security documentation.

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

semantic_models:
  # Business-friendly semantic model on top of existing view
  - name: sales_analytics
    base_view: sales_data
    label: "Sales Analytics"
    description: "Business metrics for sales analysis"
    tags: ["sales", "revenue"]
    dimensions:
      - name: order_date
        expression: "created_at::date"
        label: "Order Date"
        type: "date"
      - name: customer_region
        expression: "UPPER(customer_region)"
        label: "Customer Region"
        type: "string"
    measures:
      - name: total_revenue
        expression: "SUM(amount)"
        label: "Total Revenue"
        type: "number"
      - name: order_count
        expression: "COUNT(*)"
        label: "Order Count"
        type: "number"
```

### Semantic Models (v1)

Semantic models provide business-friendly metadata on top of existing views. **v1 is metadata-only** - no new DuckDB views are created, and no automatic query generation is performed.

**Key limitations in v1:**
- No joins between semantic models
- No automatic query generation 
- No time dimension handling
- Single base view per model

**Use semantic models to:**
- Define business-friendly names for technical columns
- Document dimensions and measures for BI tools
- Provide structured metadata for future UI features

### Semantic Models (v2)

Semantic layer v2 extends v1 with **joins, time dimensions, and defaults** while maintaining full backward compatibility.

**New v2 features:**
- **Joins**: Optional joins to other views (typically dimension tables)
- **Time dimensions**: Enhanced time dimensions with supported time grains
- **Defaults**: Default time dimension, primary measure, and default filters

```yaml
semantic_models:
  - name: sales_analytics
    base_view: sales_data
    label: "Sales Analytics"

    # v2: Joins to dimension views
    joins:
      - to_view: customers
        type: left
        on_condition: "sales.customer_id = customers.id"
      - to_view: products
        type: left
        on_condition: "sales.product_id = products.id"

    dimensions:
      # v2: Time dimension with time grains
      - name: order_date
        expression: "created_at"
        type: "time"
        time_grains: ["year", "quarter", "month", "day"]
        label: "Order Date"

      - name: customer_region
        expression: "customers.region"
        type: "string"
        label: "Customer Region"

    measures:
      - name: total_revenue
        expression: "SUM(sales.amount)"
        label: "Total Revenue"
        type: "number"

    # v2: Default configuration
    defaults:
      time_dimension: order_date
      primary_measure: total_revenue
      default_filters:
        - dimension: customer_region
          operator: "="
          value: "NORTH AMERICA"
```

**Backward Compatibility:**
- All existing v1 semantic models continue to work unchanged
- New v2 fields are optional and additive
- No breaking changes to existing validation rules

See the [`examples/semantic_layer_v2`](examples/semantic_layer_v2/) directory for a complete example demonstrating all v2 features.

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

### Path Resolution

Duckalog automatically resolves relative paths to absolute paths, ensuring consistent behavior regardless of where Duckalog is executed from.

#### **Automatic Path Resolution**
- **Relative Paths**: Paths like `"data/file.parquet"` are automatically resolved relative to the configuration file's directory
- **Absolute Paths**: Already absolute paths (e.g., `"/absolute/path/file.parquet"` or `"C:\path\file.parquet"`) are preserved unchanged
- **Remote URIs**: Cloud storage URIs (`s3://`, `gs://`, `http://`) and database connections are not modified
- **Cross-Platform**: Works consistently on Windows, macOS, and Linux

#### **Security Features**
- **Directory Traversal Protection**: Prevents malicious path patterns (e.g., `"../../../etc/passwd"`)
- **Sandboxing**: Resolved paths are restricted to stay within reasonable bounds from the config directory
- **Validation**: Path resolution is validated to ensure security and accessibility

#### **Examples**

```yaml
# Relative paths (recommended)
views:
  - name: users
    source: parquet
    uri: "data/users.parquet"  # Resolved to: /path/to/config/data/users.parquet
    description: "User data relative to config location"

  - name: events
    source: parquet
    uri: "../shared/events.parquet"  # Resolved to: /path/to/../shared/events.parquet
    description: "Shared data from parent directory"

# Absolute paths (still supported)
views:
  - name: fixed_data
    source: parquet
    uri: "/absolute/path/data.parquet"  # Used as-is
    description: "Absolute path preserved unchanged"

# Remote URIs (not modified)
views:
  - name: s3_data
    source: parquet
    uri: "s3://my-bucket/data/file.parquet"  # Used as-is
    description: "S3 paths unchanged"
```

#### **Benefits**
- **Reproducible Builds**: Catalogs work consistently across different working directories
- **Flexible Project Structure**: Organize data files relative to configuration location
- **Portability**: Move configuration and data together without path updates
- **Safety**: Security validation prevents path traversal attacks

### Configuration Format Preservation

Duckalog automatically preserves your configuration file format when making updates through the web UI:

#### **YAML Format Preservation**
- Maintains comments and formatting
- Preserves indentation and structure
- Uses `ruamel.yaml` when available for best results
- Falls back to standard `pyyaml` if needed

#### **JSON Format Preservation**
- Maintains pretty-printed structure
- Preserves field ordering
- Uses 2-space indentation for readability

#### **Automatic Format Detection**
- **File Extension**: `.yaml`, `.yml`, `.json`
- **Content Analysis**: Analyzes file structure if extension is ambiguous
- **Smart Detection**: JSON detected by `{`/`[` starts, YAML otherwise

#### **Atomic Operations**
All configuration updates use atomic file operations:
1. Write to temporary file with new format
2. Validate the temporary file
3. Atomically replace original file
4. Clean up temporary files on failure
5. Reload configuration into memory

#### **In-Memory Configuration**
- Configuration changes take effect immediately
- No server restart required for updates
- Background tasks use latest configuration
- Failed updates don't affect running operations

---

## Contributing

We welcome contributions to duckalog! This section provides guidelines and instructions for contributing to the project.

### Development Setup

**Requirements:** Python 3.9 or newer

#### Automated Version Management

This project uses automated version tagging to streamline releases. When you update the version in `pyproject.toml` and push to the main branch, the system automatically:

- Extracts the new version from `pyproject.toml`
- Validates semantic versioning format (X.Y.Z)
- Compares with existing tags to prevent duplicates
- Creates a Git tag in format `v{version}` (e.g., `v0.1.0`)
- Triggers the existing `publish.yml` workflow to publish to PyPI

**Simple Release Process:**
```bash
# 1. Update version in pyproject.toml
sed -i 's/version = "0.1.0"/version = "0.1.1"/' pyproject.toml

# 2. Commit and push
git add pyproject.toml
git commit -m "bump: Update version to 0.1.1"
git push origin main

# 3. Automated tagging creates tag and triggers publishing
# Tag v0.1.1 is created automatically
# publish.yml workflow runs and publishes to PyPI
```

For detailed examples and troubleshooting, see:
- [Automated Version Tagging Documentation](docs/automated-version-tagging.md)
- [Version Update Examples](docs/version-update-examples.md)
- [Troubleshooting Guide](docs/troubleshooting-version-tagging.md)

#### Continuous Integration

Duckalog uses a streamlined GitHub Actions setup to keep CI predictable:

- **Tests workflow** runs Ruff + mypy on Python 3.11 and executes pytest on Ubuntu for Python 3.9–3.12. If tests fail, the workflow fails—no auto-generated smoke tests.
- **Security workflow** focuses on a curated set of scans: TruffleHog and GitLeaks for secrets, Safety + pip-audit for dependency issues, and Bandit + Semgrep for code-level checks. Heavy container or supply-chain scans run only when explicitly needed.
- **publish.yml** builds sdist + wheel once on Python 3.11, validates artifacts with `twine check`, smoke-tests the wheel, and then reuses the artifacts for Test PyPI, PyPI, or dry-run scenarios. Release jobs rely on the `Tests` workflow’s status rather than re-running the full test matrix.

For local development, we recommend:

- `uv run ruff check src/ tests/` to run lint checks (CI treats these as required).
- `uv run ruff format src/ tests/` to auto-format code (CI runs `ruff format --check` in advisory mode).
- `uv run mypy src/duckalog` to run type checks.

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
