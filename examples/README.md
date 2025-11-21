# Duckalog Examples

This directory contains comprehensive examples demonstrating Duckalog's capabilities across different business domains and difficulty levels.

## Example Structure

Each example follows a standardized structure:

```
examples/[category]/[example-name]/
├── README.md              # Business context, setup, and learning objectives
├── catalog.yaml           # Duckalog configuration
├── data/
│   └── generate.py        # Reproducible data generation script
├── validate.py            # Automated validation script
└── docker-compose.yml     # Optional: Complex setup requirements
```

## Categories

### 📊 Business Intelligence
Real-world analytics scenarios and business metrics:
- **multi-source-analytics**: Multi-source data integration with cross-source joins (Level 2)

### 🔗 Data Integration
Multi-source and cloud data integration patterns:
- **multi-source**: Combining different data sources
- **cloud-warehouses**: BigQuery, Snowflake integration

### 🚀 Production & Operations
Production-ready configurations and operational best practices:
- **environment-variables-security**: Secure credential management and environment isolation (Level 3)
- **duckdb-performance-settings**: Memory, thread, and storage optimization techniques (Level 4)

### 🔧 Advanced Features
Advanced Duckalog capabilities and extensions:
- **cicd-integration**: CI/CD workflows and automation
- **scaling**: Large dataset handling and performance
- **monitoring**: Observability and alerting

### ⚡ Advanced Features
Advanced Duckalog capabilities and integrations:
- **web-ui**: Interactive dashboard configurations
- **semantic-layer**: Business metadata and semantic models
- **sql-advanced**: Window functions, analytics, JSON processing

## Difficulty Levels

- **Level 1** 🟢: Single data source, basic concepts (Beginner friendly)
- **Level 2** 🟡: Multiple sources, simple joins (Intermediate)
- **Level 3** 🟠: Complex logic, advanced features (Advanced)
- **Level 4** 🔴: Production patterns, enterprise scale (Expert)

## Quick Start

1. **Choose an example** based on your use case and skill level
2. **Follow the README** for setup instructions
3. **Generate data** using `python data/generate.py`
4. **Build catalog** with `duckalog build catalog.yaml`
5. **Validate results** with `python validate.py`

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on contributing new examples.