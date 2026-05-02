# Documentation Map

This file tracks each documentation page, its user intent, canonical destination, and migration action during the Zensical documentation refresh.

| Page | Current title | User intent | Canonical destination | Action |
|------|---------------|-------------|-----------------------|--------|
| `docs/SECURITY.md` | Security Documentation | Understand SQL injection protection, path security, auth | `docs/SECURITY.md` | Revise; updated version stamp |
| `docs/_snippets/intro-quickstart.md` | Duckalog | TBD | TBD | TBD |
| `docs/architecture/adr-001-break-monolithic-loader.md` | ADR-001: Break Monolithic loader.py | Record decision to split monolithic loader | `docs/architecture/adr-001-break-monolithic-loader.md` | Keep; ADR preserved unchanged |
| `docs/architecture/adr-002-eliminate-circular-dependencies.md` | ADR-002: Eliminate Circular Dependencies | Record decision to eliminate circular imports | `docs/architecture/adr-002-eliminate-circular-dependencies.md` | Keep; ADR preserved unchanged |
| `docs/architecture/index.md` | Architecture Decision Records (ADRs) | Index of architectural decisions | `docs/architecture/index.md` | Revise; removed broken ADR links |
| `docs/best-practices-path-management.md` | Best Practices: Path Management in Duckalog | Task-focused guidance for managing paths securely and portably | `docs/how-to/path-resolution.md` | Merge content into new how-to page; replace with stub |
| `docs/configuration-path-examples.md` | Configuration Examples: Path Resolution | YAML config examples showing path resolution patterns | `docs/examples/path-resolution-examples.md` | Merge unique examples into canonical examples page; replace with stub |
| `docs/dashboard/architecture.md` | Dashboard Architecture | Understand dashboard tech stack and architecture | `docs/dashboard/architecture.md` | Keep; cross-links updated |
| `docs/dashboard/components.md` | UI Component Usage Guide | Build and customize dashboard UI components | `docs/dashboard/components.md` | Keep |
| `docs/dashboard/datastar-patterns.md` | Datastar Integration Patterns | Use Datastar SSE and signals in the dashboard | `docs/dashboard/datastar-patterns.md` | Keep |
| `docs/dependency-injection-guide.md` | Dependency Injection Guide for Duckalog Configuration Architecture | Extend configuration loading with custom components | `docs/dependency-injection-guide.md` | Revise; fixed directory tree, removed references to deleted modules |
| `docs/documentation-duplication-policy.md` | Documentation Duplication Policy | TBD | TBD | TBD |
| `docs/examples/.env-examples.md` | Example .env files for common Duckalog use cases | TBD | TBD | TBD |
| `docs/examples/config-imports.md` | Config Imports | TBD | TBD | TBD |
| `docs/examples/dependency-injection-examples.md` | Dependency Injection Examples | TBD | TBD | TBD |
| `docs/examples/duckdb-secrets.md` | DuckDB Secrets Example | TBD | TBD | TBD |
| `docs/examples/duckdb-settings.md` | DuckDB Settings Example | TBD | TBD | TBD |
| `docs/examples/environment-vars.md` | Environment Variables and .env Files Example | TBD | TBD | TBD |
| `docs/examples/index.md` | Duckalog Examples | TBD | TBD | TBD |
| `docs/examples/local-attachments.md` | Local Attachments Example | TBD | TBD | TBD |
| `docs/examples/multi-source-analytics.md` | Multi-Source Analytics Example | TBD | TBD | TBD |
| `docs/examples/path-resolution-examples.md` | Path Resolution Examples | Practical examples of path resolution in various scenarios | `docs/examples/path-resolution-examples.md` | Keep as canonical examples page |
| `docs/examples/simple-parquet.md` | Simple Parquet Example | Simple parquet catalog example | `docs/examples/simple-parquet.md` | Keep |
| `docs/explanation/architecture.md` | Duckalog Architecture | Understand system architecture and data flow | `docs/explanation/architecture.md` | Revise; removed references to deleted modules |
| `docs/explanation/comparison.md` | Comparison with Alternatives | Compare Duckalog to dbt, Airflow, Spark, etc. | `docs/explanation/comparison.md` | Keep |
| `docs/explanation/limitations.md` | Limitations and Known Issues | Understand scale limits, known issues, workarounds | `docs/explanation/limitations.md` | Revise; fixed stale API examples |
| `docs/explanation/performance.md` | Performance Characteristics | Optimize queries, storage, and configuration | `docs/explanation/performance.md` | Revise; removed nonexistent CLI command, fixed API examples |
| `docs/explanation/philosophy.md` | Duckalog Philosophy | Understand Duckalog design philosophy and trade-offs | `docs/explanation/philosophy.md` | Keep |
| `docs/guides/index.md` | User Guide | Legacy guides landing page | `docs/guides/index.md` | Retain for now; legacy guide directory to evaluate in later milestone |
| `docs/guides/path-resolution.md` | Path Resolution and Security | Conceptual guide with implementation details and security | `docs/path-resolution.md` | Merge unique content into canonical conceptual page; replace with stub |
| `docs/guides/troubleshooting.md` | Troubleshooting Guide | General troubleshooting for Duckalog | `docs/guides/troubleshooting.md` | Retain for now; evaluate for consolidation in later milestone |
| `docs/guides/ui-dashboard.md` | Duckalog Dashboard | Dashboard usage guide | `docs/guides/ui-dashboard.md` | Retain for now; evaluate for consolidation with `docs/dashboard/` pages in later milestone |
| `docs/guides/usage.md` | User Guide | Comprehensive usage guide covering configuration, CLI, and features | `docs/guides/usage.md` | Retain; large cross-cutting guide to evaluate in later milestone |
| `docs/how-to/path-resolution.md` | How to Manage Paths in Duckalog | Task-focused guide for path management best practices | `docs/how-to/path-resolution.md` | Keep as canonical how-to page (created from best-practices-path-management.md) |
| `docs/how-to/debugging-builds.md` | How to Debug Build Failures | Task guide for debugging catalog build failures | `docs/how-to/debugging-builds.md` | Keep |
| `docs/how-to/environment-management.md` | How to Manage Different Environments | Task guide for managing dev/staging/prod configs | `docs/how-to/environment-management.md` | Keep |
| `docs/how-to/index.md` | How-to Guides | How-to guides landing page | `docs/how-to/index.md` | Keep |
| `docs/how-to/migration.md` | How to Migrate from Manual SQL | General migration from manual SQL to Duckalog | `docs/how-to/migration.md` | Keep |
| `docs/how-to/performance-tuning.md` | How to Tune Performance | Task guide for performance optimization | `docs/how-to/performance-tuning.md` | Keep |
| `docs/how-to/secrets-persistence.md` | Managing Secrets Persistence | Task guide for secrets and persistence | `docs/how-to/secrets-persistence.md` | Keep |
| `docs/index.md` | Duckalog Documentation | Documentation landing page with quickstart and learning paths | `docs/index.md` | Keep; update cross-links if canonical pages move |
| `docs/migration-path-resolution.md` | Migration Guide: Path Resolution | Step-by-step migration from absolute to relative paths | `docs/migration-path-resolution.md` | Keep as canonical migration guide (unique process, checklist, rollback, troubleshooting) |
| `docs/migration-refactor-config-architecture.md` | Migration Guide: Configuration Architecture Refactor | Migration for configuration architecture changes | `docs/migration-refactor-config-architecture.md` | Retain for now; evaluate in later milestone |
| `docs/path-resolution-examples.md` | Path Resolution Examples | Top-level examples showing path resolution patterns | `docs/examples/path-resolution-examples.md` | Merge unique examples into canonical examples page; replace with stub |
| `docs/path-resolution.md` | Path Resolution Guide | Conceptual explanation of path resolution | `docs/path-resolution.md` | Keep as canonical conceptual page; merge guide content into it |
| `docs/reference/api-patterns.md` | API Patterns | Advanced API patterns and customization | `docs/reference/api-patterns.md` | Keep; revised in prior milestone |
| `docs/reference/api.md` | API Reference | Python API reference with mkdocstrings | `docs/reference/api.md` | Keep; revised in prior milestone |
| `docs/reference/cli.md` | CLI Reference | Complete CLI command and option reference | `docs/reference/cli.md` | Keep; revised in prior milestone |
| `docs/reference/config-schema.md` | Configuration Schema Reference | Full configuration schema with field definitions | `docs/reference/config-schema.md` | Keep; revised in prior milestone |
| `docs/reference/index.md` | API Reference | TBD | TBD | TBD |
| `docs/tutorials/dashboard-basics.md` | Dashboard Basics Tutorial | TBD | TBD | TBD |
| `docs/tutorials/getting-started.md` | Getting Started with Duckalog | TBD | TBD | TBD |
| `docs/tutorials/index.md` | Tutorials | TBD | TBD | TBD |
