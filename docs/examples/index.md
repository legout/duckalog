# Duckalog Examples

Welcome to the Duckalog examples collection! These practical examples demonstrate real-world usage patterns and help you get started with different Duckalog configurations.

## Choosing an Example

Use this guide to find the right example for your use case:

### I'm getting started with Duckalog
→ **Start with**: [Simple Parquet Example](simple-parquet.md)
- Learn the basics of creating DuckDB views over Parquet files
- Perfect for simple analytics without complex joins
- Covers local files and S3 storage

### I need to combine multiple local databases
→ **Use**: [Local Attachments Example](local-attachments.md)
- Attach DuckDB and SQLite databases
- Join data across different local databases
- Learn read-only attachment patterns

### I have data in multiple sources (Parquet + databases + cloud storage)
→ **Follow**: [Multi-Source Analytics Example](multi-source-analytics.md)
- Comprehensive example with S3, PostgreSQL, Iceberg, and local databases
- Real-world analytics workflow
- Complex joins and business logic

### I need to deploy configs across different environments
→ **Read**: [Environment Variables Example](environment-vars.md)
- Secure credential management
- Development, staging, and production configurations
- Docker and Kubernetes deployment patterns

### I want to fine-tune DuckDB performance and behavior
→ **Explore**: [DuckDB Settings Example](duckdb-settings.md)
- Configure session-level settings beyond pragmas
- Optimize threading, memory, and caching
- Control DuckDB features and progress output

### I need to manage credentials for cloud services and databases
→ **Use**: [DuckDB Secrets Example](duckdb-secrets.md)
- Secure credential management for S3, Azure, GCS, and databases
- Support for environment variable interpolation
- Persistent and temporary secrets with scoping
- Integration with attachments and Iceberg catalogs

## Quick Comparison

| Example | Difficulty | Data Sources | Key Learning |
|---------|-----------|--------------|--------------|
| | [Simple Parquet](simple-parquet.md) | 🟢 Beginner | Parquet files | Basic configuration and S3 setup |
| | [Local Attachments](local-attachments.md) | 🟡 Intermediate | DuckDB/SQLite | Database attachments and cross-database joins |
| | [Multi-Source Analytics](multi-source-analytics.md) | 🔴 Advanced | Multiple sources | Complex analytics and business logic |
| | [Environment Variables](environment-vars.md) | 🟡 Intermediate | Any | Security and deployment patterns |
| | [DuckDB Settings](duckdb-settings.md) | 🟡 Intermediate | Any | Performance tuning and session configuration |
| | [DuckDB Secrets](duckdb-secrets.md) | 🟡 Intermediate | Any | Credential management and secure access |

## Prerequisites for All Examples

### Required Software
- **Python 3.9+** with Duckalog installed:
  ```bash
  pip install duckalog
  ```

### Optional but Recommended
- **DuckDB CLI** for interactive querying:
  ```bash
  # Install DuckDB CLI (optional)
  # Visit: https://duckdb.org/docs/installation/
  ```

- **AWS CLI** (for S3 examples):
  ```bash
  pip install awscli
  aws configure
  ```

## Example Categories

### By Data Source

**Parquet Files Only**
- [Simple Parquet](simple-parquet.md) - Perfect starting point
- [Multi-Source Analytics](multi-source-analytics.md) - Includes Parquet with other sources

**Local Databases**
- [Local Attachments](local-attachments.md) - DuckDB and SQLite focus
- [Multi-Source Analytics](multi-source-analytics.md) - Local databases with cloud sources

**Cloud Storage & Data Lakes**
- [Simple Parquet](simple-parquet.md) - S3 configuration
- [Multi-Source Analytics](multi-source-analytics.md) - S3 + Iceberg catalogs
- [Environment Variables](environment-vars.md) - Cloud credential management

**Enterprise/Production**
- [Multi-Source Analytics](multi-source-analytics.md) - Production-ready patterns
- [Environment Variables](environment-vars.md) - Deployment and security

### By Use Case

**Data Analytics**
- [Simple Parquet](simple-parquet.md) - Basic analytics
- [Local Attachments](local-attachments.md) - Cross-database analytics
- [Multi-Source Analytics](multi-source-analytics.md) - Enterprise analytics

**Data Integration**
- [Local Attachments](local-attachments.md) - Local data unification
- [Multi-Source Analytics](multi-source-analytics.md) - Cloud + local integration

**Development & Deployment**
- [Environment Variables](environment-vars.md) - Environment-specific configs
- [Multi-Source Analytics](multi-source-analytics.md) - Production deployment patterns

## Common Patterns Across Examples

All examples demonstrate these important Duckalog concepts:

1. **Configuration Structure** - Consistent YAML patterns
2. **View Composition** - Building complex analytics from simple views
3. **Performance Optimization** - Memory limits, threading, pragmas
4. **Error Handling** - Validation and troubleshooting
5. **Best Practices** - Security, maintainability, scalability

## Getting Started

1. **Choose your example** based on your use case above
2. **Read the prerequisites** in your chosen example
3. **Follow the step-by-step guide** provided in each example
4. **Experiment** with the configurations to match your needs
5. **Combine patterns** from multiple examples as needed

## Next Steps

After working through examples:

- **Read the User Guide** in `../guides/usage.md` for comprehensive documentation
- **Explore the API Reference** in `../reference/api.md` for detailed function documentation
- **Review the PRD** in `../plan/PRD_Spec.md` for deep technical understanding
- **Join the community** for questions and discussions

## Contributing Examples

Have a great Duckalog pattern to share? Consider contributing:

1. Create a new example following the patterns shown here
2. Include clear explanations and real-world scenarios
3. Add troubleshooting sections for common issues
4. Ensure examples work with minimal setup
5. Link from this index page

## Need Help?

- **Configuration Issues**: Check [troubleshooting sections](simple-parquet.md#troubleshooting) in examples
- **API Questions**: See [API Reference](../reference/api.md)
- **General Usage**: Review [User Guide](../guides/usage.md)
- **Technical Details**: Read [PRD Spec](../plan/PRD_Spec.md)

Choose an example above to get started, or explore them in order to build your Duckalog expertise progressively!