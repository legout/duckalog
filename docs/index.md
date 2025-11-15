# Duckalog Documentation

Welcome to the Duckalog documentation. Duckalog is a Python library and CLI
for building DuckDB catalogs from declarative YAML/JSON configuration files.

Use these docs to:

- Understand the core concepts behind Duckalog configs.
- Get started with the CLI and Python API.
- Find API reference information generated from the source code.

## Quickstart

### Install

```bash
pip install duckalog
```

### Minimal config

Create a file named `catalog.yaml`:

```yaml
version: 1

duckdb:
  database: catalog.duckdb

views:
  - name: users
    source: parquet
    uri: "s3://my-bucket/data/users/*.parquet"
```

### Build the catalog

```bash
duckalog build catalog.yaml
```

### Generate SQL only

```bash
duckalog generate-sql catalog.yaml --output create_views.sql
```

### Validate the config

```bash
duckalog validate catalog.yaml
```

### Use from Python

```python
from duckalog import build_catalog, generate_sql, validate_config

build_catalog("catalog.yaml")
sql = generate_sql("catalog.yaml")
validate_config("catalog.yaml")
```

For a deeper product and technical description, see the PRD in
`docs/PRD_Spec.md`.

