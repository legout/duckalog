# Changelog
## [UNRELEASED] - 0.4.0

### Added
- Major documentation refactor implementing Diátaxis framework
- Complete tutorial system with step-by-step learning paths
- Comprehensive how-to guides for common workflows  
- Enhanced CLI and API reference documentation
- New explanation section: Philosophy, Performance, Limitations, and Comparison guides
- Dashboard basics tutorial with hands-on UI workflow instructions
- Performance tuning and environment management guides
- Migration and troubleshooting documentation
- Updated examples with validated schema compliance

### Changed
- Reorganized documentation following Diátaxis principles (Tutorials, How-to, Reference, Explanation)
- Updated navigation structure for improved discoverability
- Fixed CLI command documentation (version command syntax)
- Corrected example catalog configurations to match schema requirements
- Enhanced code examples and validated all CLI commands

### Deprecated
- Legacy guides section (preserved for backward compatibility)
- Mixed-content documentation patterns

### Fixed
- Fixed missing version field in example catalog files
- Corrected CSV source configuration examples
- Updated documentation build process to eliminate warnings

## [2025-12-03] - 0.3.2

### Added
- Feat: adopt loguru logging abstraction (d6dd68d)

### Changed
- Docs: auto-update changelog.md for version 0.3.1 (323023c)


### Changed
- Docs: auto-update changelog.md for version 0.3.0 (509dcb1)


### Added
- Feat: add comprehensive security regression tests for sql and path protection (a2489da)
- Add comprehensive tests for root-based path security model (8dfe6a3)
- Feat: implement root-based path security boundaries (ecdb4dc)
- Feat: implement sql quoting and secrets safety improvements (34ddd67)
- Feat: implement secrets creation functionality (24bff5c)
- Feat: implement secrets creation functionality (514ec6f)
- Docs: complete add-duckdb-connection-api proposal (299e221)
- Feat: complete openspec change proposals (7016b94)
- Feat: implement duckdb connection api functions (7b410e0)
- Complete add-config-init change proposal tasks (7dcd7fe)

### Fixed
- Fix: eliminate documentation build warnings and improve navigation discoverability (1f5954f)

### Changed
- Update docs for refactored architecture (39a237e)
- Plan documentation update after major refactor (293cbe2)
- Archive completed specification changes to dated folders (16aacf8)
- Refactor: consolidate cli filesystem options across commands (08d69de)
- Docs: mark hierarchical dependency tests as completed (abf0fe2)
- Refactor: simplify engine with catalogbuilder orchestration (c300d43)
- Refactor: extract config into structured package (191f821)
- Refactor: consolidate config layer - merge path_resolution, sql_file_loader, and logging_utils into config.py (277ed3a)
- Update: clarify remote config api contract and responsibilities (9c95820)
- Clarify: standardize python version support at 3.12+ (836de9d)
- Refactor: simplify and standardize exception hierarchy (b78770a)
- Docs: update implement-secrets-creation tasks.md with accurate completion status (f5073d3)
- Docs: mark all path security tasks as completed (919aa27)
- Move code review docs from plan to top level (f952376)
- Docs: update project documentation and agents.md (d206b68)
- Docs: update examples to use modern type annotations (b956586)
- Refactor: modernize python type annotations (45299dc)
- Docs: auto-update changelog.md for version 0.2.4 (55759ce)

## [Unreleased] - Secret Models Refactoring

### Added
- Refactor: Implemented unified `SecretConfig` model as the single canonical configuration interface for all DuckDB secret types
- Refactor: Added comprehensive field coverage for all secret backends (S3, Azure, GCS, HTTP, PostgreSQL, MySQL)
- Refactor: Enhanced validation logic to support multiple credential formats per backend type
- Refactor: Added detailed field mapping documentation between `SecretConfig` and DuckDB `CREATE SECRET` parameters

### Changed
- Refactor: Removed duplicated backend-specific secret classes (`S3SecretConfig`, `AzureSecretConfig`, etc.) from `config.py`
- Refactor: Updated `generate_secret_sql()` to use only fields defined on `SecretConfig` for improved maintainability
- Refactor: Consolidated secret model definitions with `SecretConfig` as the single source of truth
- Refactor: Updated validation rules to support all supported credential combinations per backend type

### Breaking Changes
- Refactor: Backend-specific secret models are now internal implementation details only; users must use `SecretConfig`
- Refactor: Some validation errors may change to reflect the stricter canonical model approach
- Refactor: Configuration examples should now use `SecretConfig` field names exclusively

### Deprecated
- Refactor: Direct use of backend-specific secret models from `secret_types.py` is discouraged (use `SecretConfig` instead)

## [Unreleased] - Path Security Hardening

### Added
- Security: Implemented root-based path security model to replace heuristic-based traversal protection
- Security: Added `is_within_allowed_roots()` function for robust cross-platform path validation
- Security: Enhanced path resolution to use `Path.resolve()` and `os.path.commonpath()` for reliable security checks
- Security: Added comprehensive test coverage for path traversal attack prevention across Unix and Windows systems

### Changed
- Security: Replaced `_is_reasonable_parent_traversal()` heuristic checks with definitive root-based validation
- Security: Updated `resolve_relative_path()` to enforce strict root boundaries for all resolved paths
- Security: Modified `validate_path_security()` to use the new root-based security model
- Security: Path security now prevents ALL path traversal attacks regardless of encoding or separator patterns

### Deprecated
- Security: `_is_reasonable_parent_traversal()` function deprecated in favor of `is_within_allowed_roots()`
- Security: Old heuristic-based security approach will be removed in a future version

### Fixed
- Security: Eliminated bypass vectors in path traversal protection (encoding tricks, mixed separators, symlinks)
- Security: Fixed cross-platform inconsistencies in path security validation
- Security: Improved error messages for path security violations to be more descriptive and actionable

### Breaking Changes
- Security: Some paths that previously "worked" by escaping the configuration directory may now be rejected for safety
- Security: More restrictive path validation may affect existing configurations that relied on excessive parent directory traversal

## [Unreleased] - SQL Security Improvements

### Added
- Security: Implemented canonical SQL quoting helpers (`quote_ident`, `quote_literal`) to prevent SQL injection attacks
- Security: Added strict type checking for `SecretConfig.options` (only `bool`, `int`, `float`, `str` allowed)
- Security: Enhanced SQL injection protection for view generation with database/table names
- Security: Hardened secret SQL generation against quote injection and unsafe interpolation

### Changed
- Security: All SQL generation now uses safe quoting helpers instead of ad-hoc string manipulation
- Security: `generate_view_sql` now properly quotes identifiers for `duckdb`, `sqlite`, and `postgres` sources
- Security: Attachment and catalog SQL in `engine.py` now uses proper identifier and literal quoting
- Security: `generate_secret_sql` now enforces strict type validation for option values

### Fixed
- Security: Eliminated SQL injection vectors through configuration-derived database/table names
- Security: Fixed quote escaping in secret generation to prevent SQL injection through secret values
- Security: Removed unsafe string interpolation fallback for unsupported option types

## [2025-11-27] - 0.2.4

### Changed
- Docs: auto-update changelog.md for version 0.2.3 (c34577b)


### Changed
- Docs: auto-update changelog.md for version 0.2.2.1 (b23c35a)
- Docs: auto-update changelog.md for version 0.2.2 (c701f39)


### Changed
- Docs: auto-update changelog.md for version 0.2.2 (c701f39)


### Added
- Add config initialization functionality (f3bf221)

### Changed
- Docs: auto-update changelog.md for version 0.2.1 (1319bc4)


### Added
- Feat: complete semantic ui labels feature and add ci/cd integration examples (4dc5188)


### Added
- **Remote Catalog Export**: Export built DuckDB catalogs directly to cloud storage using fsspec
  - **Cloud Storage Support**: S3, GCS, Azure Blob Storage, Azure Data Lake, SFTP destinations
  - **Extended CLI**: `--db-path` parameter now accepts remote URIs (s3://, gs://, gcs://, abfs://, adl://, sftp://)
  - **Python API**: `build_catalog(config, db_path="s3://bucket/catalog.duckdb", filesystem=custom_fs)`
  - **Temp File Strategy**: Builds locally then streams upload to minimize memory usage
  - **Authentication**: Reuses existing filesystem authentication patterns with provider-specific options
  - **Error Handling**: Clear error messages for missing dependencies and authentication failures
  - **Testing Infrastructure**: Comprehensive test coverage for remote export scenarios
- **Custom Filesystem Authentication**: Enhanced remote configuration loading with flexible filesystem parameter support
  - **Python API**: `load_config(uri, filesystem=custom_fs)` for programmatic credential management
  - **CLI Support**: Added `--fs-*` options for all commands (build, validate, generate-sql)
  - **Multi-Cloud Support**: S3, GCS, Azure, SFTP, GitHub with custom authentication
  - **Backward Compatibility**: Existing environment variable authentication preserved
  - **Testing Infrastructure**: Comprehensive test suite for filesystem scenarios
  - **Documentation**: Updated README with detailed filesystem usage examples

### Changed
- **Security**: Bundle Datastar JavaScript locally (v1.0.0-RC.6) instead of loading from external CDN
- **Offline support**: Dashboard now works without external network dependencies
- **Supply chain security**: Pinned Datastar bundle eliminates remote dependency risks
- **Static file serving**: Added Starlette static mount for bundled assets at `/static/datastar.js`

### Added
- **Semantic Layer UI**: Interactive dashboard for browsing semantic models with business-friendly labels
- **Model Details View**: Expandable panels showing dimensions and measures with expressions and descriptions
- **Semantic Model APIs**: New endpoints `/api/semantic-models` and `/api/semantic-models/{name}` for programmatic access
- **Business Metadata Display**: Shows labels, descriptions, and types for semantic dimensions and measures
- **Integrated Testing**: Comprehensive test suite for semantic model UI functionality

## [2025-11-17] - 0.1.2

### Changed
- Docs: auto-update changelog.md for version 0.1.1 (e8e1ab1)


### Changed
- Docs: auto-update changelog.md for version 0.1.0.1 (ad25b43)
- Finish ci lint formatting, logging, and config type safety improvements (224f0d3)


### Changed
- Finish ci lint formatting, logging, and config type safety improvements (224f0d3)

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Enhanced package metadata and project links in pyproject.toml
- Comprehensive badge integration for quality indicators
- OpenSpec-driven change management process
- Automated PyPI publishing workflow with security scanning
- Architecture documentation for improved developer onboarding

### Changed
- Improved documentation structure and navigation
- Enhanced CI/CD pipeline with comprehensive testing
- Professional project presentation on PyPI

### Fixed
- Workflow dependency issues in GitHub Actions
- Cross-platform compatibility improvements in test suite
- Documentation build validation and link checking

## [0.1.0] - 2025-11-17

### Added
- Initial release of Duckalog - Python library and CLI for building DuckDB catalogs
- **Core Functionality**:
  - Configuration-driven catalog creation from YAML/JSON files
  - Support for multiple data sources (S3 Parquet, Delta Lake, Iceberg)
  - Database attachments (DuckDB, SQLite, PostgreSQL)
  - Environment variable interpolation for credentials
  - Idempotent catalog building operations

- **CLI Commands**:
  - `duckalog build` - Build or update DuckDB catalog from configuration
  - `duckalog validate` - Validate configuration files
  - `duckalog generate-sql` - Generate SQL without executing

- **Python API**:
  - `load_config()` - Load and validate configuration files
  - `build_catalog()` - Build catalog from configuration
  - `generate_sql()` - Generate SQL statements
  - `validate_config()` - Validate configuration without execution

- **Data Source Support**:
  - S3 Parquet file views with hive partitioning support
  - Delta Lake table integration
  - Iceberg table and catalog support
  - Attached database views (DuckDB, SQLite, PostgreSQL)
  - Raw SQL query views

- **Configuration Features**:
  - Environment variable interpolation (`${env:VAR_NAME}`)
  - Comprehensive validation using Pydantic models
  - Multiple configuration format support (YAML, JSON)
  - Extensible configuration schema

- **Documentation**:
  - Comprehensive user guide and API documentation
  - Architecture documentation with system overview
  - Quick start guide with realistic examples
  - Configuration examples and use cases

- **Development Infrastructure**:
  - Comprehensive test suite with multi-platform support
  - Automated CI/CD pipeline with security scanning
  - Code quality enforcement (Black, isort, ruff, mypy)
  - Security analysis with Bandit and dependency scanning

- **Package Distribution**:
  - PyPI-ready package with proper metadata
  - Automated publishing workflow for releases
  - Multi-Python version compatibility (3.12+)
  - Professional package presentation with badges

### Technical Implementation
- **Architecture**: Separation of concerns with distinct modules (config, model, engine, sqlgen, cli)
- **Build System**: setuptools with modern Python packaging standards
- **Testing**: pytest with coverage reporting and parallel execution
- **Quality Assurance**: Automated linting, formatting, and type checking
- **Security**: Comprehensive security scanning and vulnerability management
- **Documentation**: MkDocs with Material theme and API reference generation

### Supported Python Versions
- Python 3.12+
- Tested on Ubuntu, Windows, and macOS

### Known Limitations
- Requires DuckDB 0.8.0 or later
- Some advanced Iceberg features may require additional extensions
- Large dataset processing may require memory tuning

### Performance Characteristics
- Configuration validation: < 1 second for typical configs
- Catalog building: Depends on underlying data sources
- Memory usage: Optimized for development and moderate production use
- Scalability: Suitable for development teams and small to medium analytics workflows

---

## Version History

### [0.1.0] - 2025-11-17
**Initial Public Release**

This release establishes Duckalog as a production-ready tool for building DuckDB catalogs from declarative configuration files. Key achievements:

- **OpenSpec Implementation**: Complete change management system for sustainable development
- **Professional Package**: PyPI publication with comprehensive metadata and links
- **Quality Infrastructure**: Multi-stage CI/CD pipeline with security scanning
- **Developer Experience**: Architecture documentation and contributing guidelines
- **Community Ready**: Issue templates, security policy, and contribution process

### Future Releases

#### Planned Features (0.2.0)
- **Enhanced Source Types**: Additional data source integrations
- **Performance Improvements**: Optimized catalog building for large datasets
- **Advanced Configuration**: Template system and conditional configuration
- **Monitoring Integration**: Metrics and observability for production use
- **Extended Documentation**: Tutorial series and advanced usage patterns

#### Roadmap Items
- **Plugin System**: Dynamic loading of custom source types
- **Distributed Processing**: Support for very large datasets
- **Web Interface**: Optional web-based configuration and monitoring
- **Cloud Integration**: Native cloud storage and database integrations
- **Enterprise Features**: Advanced security, audit logging, and compliance

---

## Contributing

We welcome contributions to Duckalog! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on how to contribute to the project.

### Development Process
- All changes follow the OpenSpec process for change management
- Comprehensive testing required for all contributions
- Code quality standards enforced through automated tools
- Security review for any changes affecting data handling

### Getting Help
- **Issues**: [GitHub Issues](https://github.com/legout/duckalog/issues) for bugs and feature requests
- **Discussions**: [GitHub Discussions](https://github.com/legout/duckalog/discussions) for questions and community support
- **Documentation**: [Project Documentation](https://legout.github.io/duckalog/) for detailed guides and API reference

---

## Support and Maintenance

### Release Support
- **Current Version (0.1.x)**: Actively maintained with security updates
- **Previous Versions**: Security updates only
- **End of Life**: Notice provided 6 months before support ends

### Communication
- **Security Issues**: See [SECURITY.md](SECURITY.md) for responsible disclosure
- **General Support**: GitHub Issues and Discussions
- **Community**: Welcome to join our growing community of DuckDB and data engineering practitioners

---

*This changelog is automatically generated and maintained. For the most current information, please refer to the [project repository](https://github.com/legout/duckalog).*
