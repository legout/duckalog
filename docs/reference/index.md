# API Reference

This section provides comprehensive API documentation for the Duckalog library, generated from the source code using mkdocstrings.

## Core API

::: duckalog

## Configuration Models

### Config
The main configuration class that represents a Duckalog configuration file.

### View
Represents a view definition in the catalog.

### DuckDBConfig
Configuration for the DuckDB database instance.

### Attachment
Configuration for database attachments.

### IcebergCatalog
Configuration for Iceberg catalog connections.

## Utility Functions

### load_config
Load a Duckalog configuration from a file path.

### build_catalog
Build a DuckDB catalog from a configuration file.

### validate_config
Validate a Duckalog configuration without building.

### generate_sql
Generate SQL statements from a configuration file.

## Command Line Interface

### duckalog build
Build a DuckDB catalog from a configuration file.

### duckalog validate
Validate a configuration file.

### duckalog generate-sql
Generate SQL statements from a configuration file.

## Error Handling

### ConfigError
Raised when there's an error in the configuration file.

### CatalogError
Raised when there's an error building the catalog.

## Advanced Usage

For detailed examples and advanced usage patterns, see the [User Guide](../guides/index.md) and [Examples](../examples/index.md).