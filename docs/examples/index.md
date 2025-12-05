# Duckalog Examples

Welcome to Duckalog examples collection! These practical examples demonstrate real-world usage patterns and help you get started with different Duckalog configurations.

## Learning Path

Examples are organized by difficulty to help you build Duckalog expertise progressively:

### 🟢 Beginner (Getting Started)
Perfect for users new to Duckalog or data cataloging concepts.

### 🟡 Intermediate (Building Skills)  
For users comfortable with basic concepts and ready for more complex scenarios.

### 🔴 Advanced (Mastery)
For experienced users tackling enterprise-scale data challenges.

## Choosing an Example

Use this guide to find the right example for your use case:

### 🟢 I'm getting started with Duckalog
→ **Start with**: [Simple Parquet Example](simple-parquet.md)
- **What you'll learn**: Basic configuration, Parquet views, S3 setup
- **Prerequisites**: Basic Python, familiar with data files
- **Time to complete**: 15-30 minutes
- Perfect for simple analytics without complex joins

### 🟡 I need to combine multiple local databases
→ **Use**: [Local Attachments Example](local-attachments.md)
- **What you'll learn**: Database attachments, cross-database joins, read-only patterns
- **Prerequisites**: Familiar with basic SQL, local database concepts
- **Time to complete**: 30-45 minutes
- Great for consolidating existing local data sources

### 🔴 I have data in multiple sources (Parquet + databases + cloud storage)
→ **Follow**: [Multi-Source Analytics Example](multi-source-analytics.md)
- **What you'll learn**: Enterprise data integration, complex joins, business logic patterns
- **Prerequisites**: Comfortable with SQL, familiar with cloud storage concepts
- **Time to complete**: 60-90 minutes
- Real-world analytics workflow with production-ready patterns

### 🟢 I need to organize my configuration across multiple files
→ **Use**: [Config Imports Example](config-imports.md)
- **What you'll learn**: Modular configuration, team ownership patterns, environment management
- **Prerequisites**: Basic YAML knowledge, file system concepts
- **Time to complete**: 20-30 minutes
- Essential for team collaboration and project maintainability

### 🟡 I need to deploy configs across different environments
→ **Read**: [Environment Variables Example](environment-vars.md)
- **What you'll learn**: Secure credential management, deployment patterns, environment separation
- **Prerequisites**: Familiar with environment variables, basic deployment concepts
- **Time to complete**: 30-45 minutes
- Critical for production deployments and team workflows

### 🟡 I want to fine-tune DuckDB performance and behavior
→ **Explore**: [DuckDB Settings Example](duckdb-settings.md)
- **What you'll learn**: Performance optimization, memory management, threading configuration
- **Prerequisites**: DuckDB basics, performance concepts
- **Time to complete**: 20-30 minutes
- Essential for production performance tuning

### 🟡 I need to manage credentials for cloud services and databases
→ **Use**: [DuckDB Secrets Example](duckdb-secrets.md)
- **What you'll learn**: Secure credential management, cloud service integration, secret scoping
- **Prerequisites**: Cloud service accounts, security concepts
- **Time to complete**: 25-35 minutes
- Essential for secure cloud data access

## Learning Progression

### Step 1: Start with Basics (🟢 Beginner)
Complete these examples to build foundational skills:

1. **[Simple Parquet](simple-parquet.md)** - Learn core concepts
2. **[Config Imports](config-imports.md)** - Organize your configuration

**Outcome**: You'll understand Duckalog fundamentals and be ready for intermediate scenarios.

### Step 2: Build Intermediate Skills (🟡 Intermediate)
Tackle more complex data management challenges:

3. **[Local Attachments](local-attachments.md)** - Work with multiple databases
4. **[Environment Variables](environment-vars.md)** - Master deployment patterns
5. **[DuckDB Settings](duckdb-settings.md)** - Optimize performance
6. **[DuckDB Secrets](duckdb-secrets.md)** - Secure cloud access

**Outcome**: You'll handle real-world data integration and deployment scenarios.

### Step 3: Advanced Mastery (🔴 Advanced)
Solve enterprise-scale challenges:

7. **[Multi-Source Analytics](multi-source-analytics.md)** - Complete production workflow

**Outcome**: You'll be ready for complex enterprise data projects.

## Quick Reference

| Example | Difficulty | Time | Prerequisites | Key Skills |
|---------|-----------|--------|---------------|-------------|
| [Simple Parquet](simple-parquet.md) | 🟢 Beginner | 15-30 min | Basic Python | Core configuration |
| [Config Imports](config-imports.md) | 🟢 Beginner | 20-30 min | YAML knowledge | Modular organization |
| [Local Attachments](local-attachments.md) | 🟡 Intermediate | 30-45 min | Basic SQL | Database attachments |
| [Environment Variables](environment-vars.md) | 🟡 Intermediate | 30-45 min | Deployment concepts | Secure deployment |
| [DuckDB Settings](duckdb-settings.md) | 🟡 Intermediate | 20-30 min | Performance concepts | Optimization |
| [DuckDB Secrets](duckdb-secrets.md) | 🟡 Intermediate | 25-35 min | Cloud accounts | Credential management |
| [Multi-Source Analytics](multi-source-analytics.md) | 🔴 Advanced | 60-90 min | Complex SQL | Enterprise integration |

## Prerequisites for All Examples

### Required Software
- **Python 3.12+** with Duckalog installed:
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

**Configuration Management**
- [Config Imports](config-imports.md) - Modular configuration patterns
- [Environment Variables](environment-vars.md) - Environment-specific settings

**Development & Deployment**
- [Config Imports](config-imports.md) - Configuration organization and modularity
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

### For Complete Beginners
1. **Start with [Simple Parquet](simple-parquet.md)** to learn core concepts
2. **Add [Config Imports](config-imports.md)** to organize your configuration
3. **Practice** with your own data files

### For Experienced Users
1. **Assess your needs** using the difficulty guide above
2. **Jump to appropriate examples** based on your current skills
3. **Combine patterns** from multiple examples as needed

### Learning Tips
- **Follow the sequence** for progressive skill building
- **Complete each example fully** before moving to the next
- **Experiment** with variations to solidify understanding
- **Apply to your data** to make learning practical

## Next Steps

After working through examples:

- **Read the User Guide** in `../guides/index.md` for comprehensive documentation
- **Explore the API Reference** in `../reference/index.md` for detailed function documentation
- **Review the Architecture** in `../explanation/architecture.md` for high-level design details
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
- **API Questions**: See [API Reference](../reference/index.md)
- **General Usage**: Review [User Guide](../guides/index.md)
- **Technical Details**: Read [Architecture](../explanation/architecture.md)

Choose an example above to get started, or explore them in order to build your Duckalog expertise progressively!
