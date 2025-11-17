# Duckalog Architecture

Duckalog is a Python library and CLI for building DuckDB catalogs from declarative YAML/JSON configuration files. This document provides a comprehensive architectural overview of the system, its components, and how they work together to transform configuration files into functional DuckDB catalogs.

## System Overview

Duckalog follows a **config-driven, idempotent architecture** that transforms declarative configuration into functional DuckDB catalogs. The system is designed around separation of concerns, with clear boundaries between configuration loading, validation, SQL generation, and catalog execution.

### Core Philosophy

- **Configuration as Code**: Catalogs are defined in version-controllable YAML/JSON files
- **Idempotent Operations**: Running the same config produces the same catalog every time
- **Multi-Source Integration**: Unified interface for S3 Parquet, Delta Lake, Iceberg, and relational databases
- **Environment-Driven**: Credentials and connection details sourced from environment variables
- **Separation of Concerns**: Clear boundaries between configuration, validation, generation, and execution

### High-Level System Architecture

```mermaid
graph TB
    subgraph "External Systems"
        S3[S3 Object Storage<br/>Parquet Files]
        DELTA[Delta Lake<br/>Tables]
        ICEBERG[Iceberg<br/>Catalog/Tables]
        DUCKDB_EXT[External DuckDB<br/>Files]
        SQLITE[SQLite<br/>Databases]
        POSTGRES[PostgreSQL<br/>Databases]
    end
    
    subgraph "Duckalog System"
        CLI[CLI Interface<br/>Commands & Validation]
        CONFIG[Config Loading<br/>YAML/JSON + Environment]
        MODEL[Pydantic Models<br/>Validation & Types]
        SQLGEN[SQL Generation<br/>CREATE VIEW Statements]
        ENGINE[DuckDB Engine<br/>Execution & Connections]
    end
    
    subgraph "Output"
        CATALOG[(DuckDB Catalog<br/>Views & Attachments)]
    end
    
    CLI --> CONFIG
    CONFIG --> MODEL
    MODEL --> SQLGEN
    SQLGEN --> ENGINE
    ENGINE --> CATALOG
    
    ENGINE -.->|S3 Parquet Access| S3
    ENGINE -.->|Delta Tables| DELTA
    ENGINE -.->|Iceberg Integration| ICEBERG
    ENGINE -.->|DuckDB Attachments| DUCKDB_EXT
    ENGINE -.->|SQLite Connections| SQLITE
    ENGINE -.->|PostgreSQL Access| POSTGRES
```

## Core Architecture Components

The system consists of five primary modules that work together to process configurations and create DuckDB catalogs:

```mermaid
graph TB
    subgraph "Duckalog Core Components"
        CLI[CLI Module<br/>Command parsing & dispatch]
        CONFIG[Config Module<br/>Loading & env interpolation]
        MODEL[Model Module<br/>Pydantic validation]
        SQLGEN[SQL Generation<br/>CREATE VIEW statements]
        ENGINE[Engine Module<br/>DuckDB execution]
        
        CLI -.->|typer commands| CONFIG
        CONFIG -.->|validated dict| MODEL
        MODEL -.->|typed objects| SQLGEN
        SQLGEN -.->|SQL strings| ENGINE
        ENGINE -.->|executed SQL| DB[(DuckDB Catalog)]
    end
    
    subgraph "Detailed Component Interactions"
        direction LR
        CONFIG_A[File I/O]
        CONFIG_B[Env Interpolation]
        CONFIG_C[Error Handling]
        
        MODEL_A[Schema Validation]
        MODEL_B[Type Conversion]
        MODEL_C[Business Rules]
        
        SQLGEN_A[Source Detection]
        SQLGEN_B[Template Selection]
        SQLGEN_C[Statement Building]
        
        ENGINE_A[Connection Mgmt]
        ENGINE_B[Attachment Setup]
        ENGINE_C[View Creation]
        ENGINE_D[Transaction Control]
    end
```

### 1. Configuration Module (`config.py`)

**Responsibilities:**
- Load YAML/JSON configuration files
- Perform environment variable interpolation
- Parse and prepare raw configuration data
- Handle file I/O and error management

**Key Features:**
- Supports both YAML and JSON formats
- Environment variable substitution using `${env:VAR_NAME}` pattern
- Recursive traversal of configuration structures
- Comprehensive error handling with descriptive messages

**Example Flow:**
```mermaid
sequenceDiagram
    participant CLI
    participant Config
    participant File
    participant Env
    
    CLI->>Config: load_config("catalog.yaml")
    Config->>File: Read file content
    File-->>Config: Raw YAML content
    Config->>Config: Parse YAML/JSON
    Config->>Config: interpolate_env(raw_dict)
    Config->>Env: Get ${env:VAR} values
    Env-->>Config: Real values
    Config-->>CLI: Validated Config object
```

### 2. Model Module (`model.py`)

**Responsibilities:**
- Define Pydantic models for configuration schema
- Provide data validation and type checking
- Ensure configuration consistency
- Support extensibility for new configuration types

**Core Models:**
- `DuckDBConfig`: Database file and session settings
- `AttachmentConfig`: External database connections (DuckDB, SQLite, Postgres)
- `IcebergCatalogConfig`: Iceberg catalog connections
- `ViewConfig`: Individual view definitions and source specifications
- `Config`: Root configuration aggregating all components

**Validation Flow:**
```mermaid
flowchart LR
    A[Raw Config Dict] --> B[Pydantic Validation]
    B --> C{Valid?}
    C -->|Yes| D[Typed Config Object]
    C -->|No| E[ConfigError]
    D --> F[Schema Validation]
    F --> G[Business Rule Validation]
    G --> H[Validated Config]
```

### 3. SQL Generation Module (`sqlgen.py`)

**Responsibilities:**
- Transform typed configuration objects into SQL statements
- Generate `CREATE VIEW` statements for different source types
- Handle SQL escaping and identifier quoting
- Support complex view definitions with joins and aggregations

**Source Types Supported:**
- **Parquet**: S3-based Parquet file views
- **Delta Lake**: Delta table references
- **Iceberg**: Iceberg table and catalog views
- **Database**: Attached DuckDB/SQLite/Postgres tables
- **SQL**: Raw SQL query views

**SQL Generation Process:**
```mermaid
graph TD
    A[ViewConfig] --> B{Source Type Detection}
    B -->|parquet| C[Generate Parquet CREATE VIEW]
    B -->|delta| D[Generate Delta CREATE VIEW]
    B -->|iceberg| E[Generate Iceberg CREATE VIEW]
    B -->|duckdb/sqlite/postgres| F[Generate DB CREATE VIEW]
    B -->|sql| G[Validate & Pass Through SQL]
    
    C --> H[Add Options & Settings]
    D --> H
    E --> H
    F --> H
    G --> H
    H --> I[Complete SQL Statement]
    
    subgraph "Source-Specific Logic"
        J[URI Processing]
        K[Authentication Config]
        L[Table Reference Resolution]
        M[Option Normalization]
    end
    
    C -.-> J
    D -.-> J
    E -.-> L
    F -.-> L
```

### 4. Engine Module (`engine.py`)

**Responsibilities:**
- Manage DuckDB connections and sessions
- Set up external attachments and catalogs
- Execute generated SQL statements
- Handle transaction management and error recovery

**Key Operations:**
- **Connection Management**: Open and maintain DuckDB connections
- **Attachment Setup**: Configure DuckDB, SQLite, and Postgres connections
- **Catalog Configuration**: Set up Iceberg catalogs with proper authentication
- **View Execution**: Apply generated SQL to create views in the catalog
- **Session Management**: Configure pragmas and session settings

**Engine Workflow:**
```mermaid
sequenceDiagram
    participant Config
    participant Engine
    participant DuckDB
    participant External
    
    Config->>Engine: execute(config)
    Engine->>DuckDB: Open connection
    Engine->>DuckDB: Apply pragmas
    Engine->>DuckDB: Install extensions
    Config->>Engine: Process attachments
    Engine->>DuckDB: ATTACH external DBs
    Config->>Engine: Process catalogs
    Engine->>DuckDB: CREATE iceberg catalogs
    Config->>Engine: Process views
    loop For each view
        Engine->>SQLGEN: generate_sql(view)
        SQLGEN-->>Engine: SQL statement
        Engine->>DuckDB: Execute SQL
        DuckDB-->>Engine: Success/Error
    end
    Engine-->>Config: Complete catalog
```

### 5. CLI Module (`cli.py`)

**Responsibilities:**
- Provide command-line interface for users
- Parse command-line arguments and options
- Dispatch to appropriate library functions
- Handle user input validation and error reporting

**Available Commands:**
- `build`: Create or update a DuckDB catalog from configuration
- `generate-sql`: Generate SQL statements without executing them
- `validate`: Validate configuration files for syntax and schema correctness

## Data Flow Architecture

The complete data flow from configuration file to functional catalog follows this pipeline:

```mermaid
flowchart TD
    A[YAML/JSON Config File] --> B[Config Loading]
    B --> C[Environment Interpolation]
    C --> D[Pydantic Validation]
    D --> E[Business Rule Validation]
    E --> F[SQL Generation]
    F --> G[Catalog Building]
    G --> H[(DuckDB Catalog)]
    
    subgraph "Validation Stages"
        C --> C1[Syntax Check]
        C1 --> C2[Schema Validation]
        C2 --> C3[Reference Validation]
    end
    
    subgraph "SQL Generation"
        F --> F1[Source Type Detection]
        F1 --> F2[Template Selection]
        F2 --> F3[Statement Building]
        F3 --> F4[Option Processing]
    end
    
    subgraph "Catalog Building"
        G --> G1[Connection Setup]
        G1 --> G2[Attachment Configuration]
        G2 --> G3[Catalog Setup]
        G3 --> G4[View Creation]
    end
```

## Complete Data Flow Architecture

Here's the complete end-to-end data flow from configuration file to functional DuckDB catalog:

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant Config
    participant Model
    participant SQLGen
    participant Engine
    participant DuckDB
    participant External
    
    User->>CLI: duckalog build config.yaml
    CLI->>Config: load_config()
    Config->>External: Read file
    Config->>External: Environment variables
    Config->>Model: Raw config dict
    
    par Parallel Processing
        Model->>Model: Schema validation
        Model->>Model: Type conversion
        Model->>Model: Business rule validation
    end
    
    Model->>SQLGen: Validated ViewConfig list
    
    par For Each View
        SQLGen->>SQLGen: Detect source type
        SQLGen->>SQLGen: Generate SQL statement
        SQLGen->>SQLGen: Apply source-specific options
        SQLGen->>Engine: SQL string
    end
    
    Engine->>DuckDB: Open connection
    Engine->>DuckDB: Apply pragmas
    Engine->>External: Setup attachments (if any)
    Engine->>External: Setup catalogs (if any)
    
    par For Each Generated SQL
        Engine->>DuckDB: Execute CREATE VIEW
        DuckDB-->>Engine: Success/Error
    end
    
    Engine-->>Model: Completion status
    Model-->>CLI: Success/Error
    CLI-->>User: Operation complete
```

## Design Patterns and Architectural Decisions

### 1. Separation of Concerns

Duckalog strictly separates different responsibilities into distinct modules:

- **Configuration Layer**: File I/O, parsing, environment interpolation
- **Validation Layer**: Schema validation, type checking, business rules
- **Generation Layer**: SQL statement creation, template management
- **Execution Layer**: Database operations, connection management
- **Interface Layer**: CLI commands, user interaction

This separation provides several benefits:
- Easier testing and debugging
- Independent module evolution
- Clear extension points
- Reduced coupling between components

### 2. Config-Driven Design

The entire system revolves around declarative configuration:

**Benefits:**
- **Reproducibility**: Same config always produces same results
- **Version Control**: Configuration files can be tracked in Git
- **Testing**: Easy to create test scenarios with different configs
- **Collaboration**: Non-developers can understand and modify configurations
- **Documentation**: Config files serve as living documentation

**Extensibility:**
New source types can be added by:
1. Extending the `ViewConfig` Pydantic model
2. Adding SQL generation logic for the new source type
3. Implementing engine-side setup if needed
4. Updating documentation and examples

### 3. Idempotent Operations

All catalog building operations are designed to be idempotent:

- **View Replacement**: `CREATE OR REPLACE VIEW` ensures consistent results
- **Attachment Management**: Consistent attachment procedures regardless of current state
- **Schema Evolution**: Config changes are applied predictably
- **Rollback Safety**: Failed operations leave the catalog in a consistent state

### 4. Layered Architecture

The system follows a strict layered approach:

```
┌─────────────────────┐
│   CLI Interface     │  ← User interaction, command parsing
├─────────────────────┤
│   Config Layer      │  ← File I/O, environment handling
├─────────────────────┤
│   Validation Layer  │  ← Schema validation, type checking
├─────────────────────┤
│   Generation Layer  │  ← SQL creation, template management
├─────────────────────┤
│   Execution Layer   │  ← Database operations, connections
├─────────────────────┤
│   External Systems  │  ← DuckDB, S3, databases, catalogs
└─────────────────────┘
```

Each layer depends only on the layer directly below it, ensuring clear dependencies and testability.

### 5. Error Handling and Logging Patterns

**Error Handling Strategy:**
- **Fail Fast**: Validate configuration early to catch issues quickly
- **Descriptive Errors**: Provide actionable error messages with context
- **Graceful Degradation**: Continue processing non-dependent items when possible
- **Error Categorization**: Different exception types for different failure modes

**Logging Approach:**
- **Structured Logging**: Use consistent log formats and levels
- **Security Conscious**: Never log sensitive information (passwords, tokens)
- **Debug Support**: Detailed logging available for troubleshooting
- **User-Friendly**: Important operations logged at appropriate levels

## Configuration Schema Architecture

The configuration schema follows a hierarchical structure:

```mermaid
graph TD
    ROOT[Config Root<br/>version, duckdb, attachments, views] --> DB[DuckDB Config<br/>database, pragmas]
    ROOT --> ATTACH[Attachments Config<br/>duckdb, sqlite, postgres]
    ROOT --> ICEBERG[Iceberg Catalogs<br/>catalog configs]
    ROOT --> VIEWS[Views List<br/>view definitions]
    
    ATTACH --> DUCKDB_ATTACH[DuckDB Attachment<br/>alias, path, read_only]
    ATTACH --> SQLITE_ATTACH[SQLite Attachment<br/>alias, path]
    ATTACH --> POSTGRES_ATTACH[Postgres Attachment<br/>alias, host, port, user, password]
    
    ICEBERG --> IC_CONFIG[Iceberg Catalog Config<br/>name, catalog_type, uri, warehouse]
    
    VIEWS --> PARQUET_VIEW[Parquet View<br/>source: parquet, uri, options]
    VIEWS --> DELTA_VIEW[Delta View<br/>source: delta, uri]
    VIEWS --> ICEBERG_VIEW[Iceberg View<br/>source: iceberg, catalog, table]
    VIEWS --> DB_VIEW[Database View<br/>source: duckdb/sqlite/postgres, database, table]
    VIEWS --> SQL_VIEW[SQL View<br/>source: sql, query]
```

## Component Dependency Graph

Understanding the dependencies between components helps in maintenance and extension:

```mermaid
graph TD
    subgraph "Layer 1: Interface"
        CLI[CLI Module<br/>Commands: build, validate, generate-sql]
    end
    
    subgraph "Layer 2: Configuration"
        CONFIG[Config Module<br/>File loading & env interpolation]
    end
    
    subgraph "Layer 3: Validation"
        MODEL[Model Module<br/>Pydantic validation & types]
    end
    
    subgraph "Layer 4: Generation"
        SQLGEN[SQL Generation<br/>Statement creation]
    end
    
    subgraph "Layer 5: Execution"
        ENGINE[Engine Module<br/>DuckDB operations]
    end
    
    subgraph "External Dependencies"
        DUCKDB[DuckDB Engine]
        YAML[YAML/JSON Parser]
        PYDANTIC[Pydantic Validator]
        TYPER[Typer CLI Framework]
    end
    
    CLI --> CONFIG
    CONFIG --> MODEL
    MODEL --> SQLGEN
    SQLGEN --> ENGINE
    
    CONFIG -.-> YAML
    MODEL -.-> PYDANTIC
    CLI -.-> TYPER
    ENGINE -.-> DUCKDB
```

### Dependency Rules:
1. **No backward dependencies** - higher layers never depend on lower layers
2. **Clear interfaces** - each layer exposes well-defined interfaces
3. **Minimal coupling** - components only know about their direct dependencies
4. **Testable units** - each layer can be tested independently

## Extension Patterns

### Adding New Source Types

To extend Duckalog with a new data source type:

1. **Model Extension**:
   ```python
   class NewSourceViewConfig(BaseModel):
       name: str
       source: Literal["new_source"]
       uri: str
       options: Dict[str, Any] = Field(default_factory=dict)
   ```

2. **SQL Generation**:
   ```python
   def generate_new_source_sql(view: NewSourceViewConfig) -> str:
       # Generate appropriate CREATE VIEW statement
       return f"CREATE OR REPLACE VIEW {view.name} AS ..."
   ```

3. **Engine Integration** (if needed):
   ```python
   def setup_new_source(engine, view: NewSourceViewConfig):
       # Set up any required connections or configurations
       pass
   ```

### Adding New Attachment Types

Similar extension pattern for database attachments:

1. Extend `AttachmentsConfig` model
2. Add attachment setup logic in engine
3. Update SQL generation if needed
4. Add validation rules

## Performance and Scalability Considerations

### Current Architecture Supports:
- **Large Configuration Files**: Efficient parsing and validation
- **Multiple Views**: Batch processing and optimization
- **Concurrent Operations**: Thread-safe where appropriate
- **Memory Management**: Streaming and chunked processing where needed

### Scaling Patterns:
- **Horizontal Scaling**: Multiple catalogs can be processed independently
- **Vertical Scaling**: DuckDB's in-memory processing for complex queries
- **External Optimization**: Leverage underlying system optimizations (S3, databases)

## Security Architecture

### Security Principles:
- **Zero Secrets in Config**: All sensitive data via environment variables
- **Connection Security**: SSL/TLS support for external connections
- **Access Control**: DuckDB's built-in security features
- **Audit Trail**: Config-driven approach provides built-in change tracking

### Security Measures:
- Environment variable validation
- Secure credential handling
- Connection security options (SSL modes)
- No credential logging or exposure

## Development and Testing Architecture

### Testing Strategy:
- **Unit Tests**: Individual module functionality
- **Integration Tests**: End-to-end catalog building
- **Configuration Tests**: Schema validation and parsing
- **SQL Generation Tests**: Output verification for different source types

### Development Workflow:
1. Configuration-driven development
2. Test-first approach for new features
3. Documentation integration
4. Continuous validation against specifications

## Future Architecture Considerations

### Potential Extensions:
- **Plugin System**: Dynamic loading of new source types
- **Caching Layer**: Configuration and SQL result caching
- **Monitoring Integration**: Metrics and observability
- **Multi-Catalog Management**: Orchestrating multiple catalog deployments

### Architectural Evolution:
The current architecture is designed to accommodate these future needs without major restructuring, thanks to its separation of concerns and extensibility patterns.

## Conclusion

Duckalog's architecture provides a robust, maintainable, and extensible foundation for building DuckDB catalogs from declarative configurations. The separation of concerns, config-driven design, and idempotent operations make it suitable for both development and production use cases, while the clear extension patterns support future growth and adaptation to new data sources and requirements.

## Getting Started with the Architecture

### For New Developers

1. **Start with the system overview** to understand Duckalog's purpose and high-level design
2. **Review the component descriptions** to understand each module's responsibilities
3. **Follow the data flow** to see how configuration becomes a catalog
4. **Examine the design patterns** to understand architectural decisions
5. **Look at extension examples** if you need to add new functionality

### For Contributors

- **Code contributions** should respect the separation of concerns
- **New source types** follow the documented extension patterns
- **Architecture changes** require OpenSpec proposals
- **Documentation updates** should maintain consistency across documents

### For System Integrators

- **API stability** is maintained through well-defined interfaces
- **Configuration evolution** follows semantic versioning principles
- **Extension points** are documented and tested
- **Error handling** provides actionable feedback for troubleshooting

## Related Documentation

- **[Product Requirements](../plan/PRD_Spec.md)**: Detailed product and technical specification
- **[User Guide](guides/usage.md)**: How to use Duckalog in practice
- **[API Reference](reference/api.md)**: Complete API documentation
- **Examples**: See the `examples/` directory for configuration samples