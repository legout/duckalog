--8<-- "_snippets/intro-quickstart.md"

# Duckalog Documentation

Welcome to the Duckalog documentation! This comprehensive guide will help you master Duckalog's features and patterns.

## Getting Started

The documentation is organized for different learning styles and needs:

- **[Tutorials](tutorials/index.md)** - Step-by-step hands-on learning for beginners
- **[How-to Guides](how-to/index.md)** - Practical solutions for specific problems
- **[Reference](reference/index.md)** - Technical API documentation and configuration schema
- **[Understanding](explanation/philosophy.md)** - Background context and architectural concepts
- **[Examples](examples/index.md)** - Real-world configuration examples and patterns

## Key Features Overview

### ✅ Multi-Source Data Integration
- **S3 Parquet/Delta/Iceberg**: Direct querying of cloud data lakes
- **Database Attachments**: Connect DuckDB, SQLite, PostgreSQL databases
- **Semantic Layer**: Business-friendly dimensions and measures
- **Path Resolution**: Automatic path handling with security validation

### ✅ Developer Experience  
- **Config-Driven**: Declarative YAML/JSON configurations
- **Idempotent**: Same config always produces the same catalog
- **CLI + Python API**: Use from command line or in code
- **Remote Configs**: Load configurations from S3, GCS, Azure, GitHub

### ✅ Production Ready
- **Security**: Environment variable credentials, no secrets in configs
- **Performance**: Optimized for large-scale analytics workloads
- **Monitoring**: Comprehensive logging and error handling
- **Web UI**: Interactive dashboard for catalog management

### ✅ Enterprise Features
- **Semantic Models**: Business-friendly metadata layer
- **Secret Management**: Canonical credential configuration
- **Audit Trail**: Config-driven change tracking
- **Multi-Cloud**: Support for AWS, GCP, Azure storage systems

## Popular Examples

- 📊 **[Multi-Source Analytics](examples/multi-source-analytics.md)**: Combine Parquet, DuckDB, and PostgreSQL data
- 🔒 **[Environment Variables Security](examples/environment-vars.md)**: Secure credential management patterns  
- ⚡ **[DuckDB Performance Settings](examples/duckdb-settings.md)**: Optimize memory, threads, and storage
- 🏷️ **[Semantic Layer v2](examples/config-imports.md)**: Business-friendly semantic models with dimensions and measures

## Quick Reference

```bash
# Installation
pip install duckalog           # Core package
pip install duckalog[ui]       # With web dashboard
pip install duckalog[remote]   # With remote configuration support

# Core CLI commands
duckalog init                  # Create starter configuration
duckalog run catalog.yaml    # Build DuckDB catalog
duckalog validate catalog.yaml # Check configuration syntax
duckalog ui catalog.yaml       # Launch web dashboard

# Remote configuration examples
duckalog run s3://bucket/config.yaml          # S3 configuration
duckalog run github://user/repo/config.yaml   # GitHub repository
duckalog run gs://bucket/config.yaml          # Google Cloud Storage
```

```python
# Python API basics
from duckalog import build_catalog, generate_sql, validate_config

# Start with a template
from duckalog.config_init import create_config_template
config = create_config_template(format="yaml", output_path="my_config.yaml")

# Build and validate
build_catalog("my_config.yaml")
validate_config("my_config.yaml")
sql = generate_sql("my_config.yaml")
```

## Next Steps

- **🆕 New to Duckalog?** Start with the [Getting Started Tutorial](tutorials/getting-started.md)
- **🎯 Have a specific problem?** Browse the [How-to Guides](how-to/index.md)  
- **📚 Need technical details?** Check the [Reference documentation](reference/index.md)
- **🏗️ Want to understand the design?** Read the [Architecture overview](explanation/architecture.md)
- **💡 Need ideas?** Explore the [Examples](examples/index.md) collection
