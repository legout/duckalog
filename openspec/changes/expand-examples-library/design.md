## Context

Duckalog currently has 3 examples that demonstrate basic functionality but lack comprehensive coverage of real-world use cases. The documentation contains rich examples that aren't executable, and there are significant gaps in business intelligence, production deployment, and advanced feature demonstrations. This change needs to establish standards while creating a comprehensive library of examples that serve both as learning resources and as executable documentation.

### Current State Analysis
- **Examples coverage**: 3 basic examples (SQL files, simple Parquet, semantic layer v2)
- **Documentation examples**: 6 comprehensive guides not in executable format
- **Missing areas**: Business intelligence scenarios, production patterns, advanced integrations
- **User feedback**: Users struggle to find relevant examples for real-world applications

### Constraints
- Examples must be self-contained and runnable without external dependencies
- Data generation scripts must be included for reproducible testing
- Examples should validate automatically as part of CI/CD pipeline
- Need to maintain backward compatibility with existing examples

## Goals / Non-Goals

### Goals
- **Establish standardized example structure** for consistency and maintainability
- **Create comprehensive library** covering major Duckalog use cases and capabilities
- **Provide progressive learning path** from basic to advanced scenarios
- **Ensure examples are executable and testable** as part of development workflow
- **Demonstrate real-world business value** beyond technical capabilities

### Non-Goals
- Create examples for every possible Duckalog feature combination
- Replace existing documentation or tutorials
- Provide production-level data or sensitive business information
- Create examples that require expensive cloud services or complex infrastructure

## Decisions

### 1. Example Organization Structure
**Decision**: Organize examples by domain/use case rather than technical feature
- **Business Intelligence**: customer-analytics, time-series, product-analytics
- **Data Integration**: multi-source, cloud-warehouses, streaming
- **Production & Ops**: cicd-integration, scaling, monitoring
- **Advanced Features**: web-ui, semantic-layer, sql-advanced

**Rationale**: Users think in terms of business problems, not technical features. This organization aligns with how users search for and evaluate tools.

### 2. Standardized Example Template
**Decision**: Each example must include:
- `README.md`: Business context, setup instructions, learning objectives
- `catalog.yaml`: Duckalog configuration (core example)
- `data/generate.py`: Reproducible data generation script
- `validate.py`: Automated validation of example functionality
- `docker-compose.yml` (optional): For complex setups

**Rationale**: Ensures consistency, makes examples self-documenting, and enables automated testing.

### 3. Progressive Complexity Approach
**Decision**: Structure examples with increasing complexity:
- **Level 1**: Single data source, basic queries (existing examples)
- **Level 2**: Multiple sources, simple joins, basic semantic models
- **Level 3**: Complex business logic, advanced semantic features, time-series
- **Level 4**: Production patterns, CI/CD, scaling, monitoring

**Rationale**: Provides clear learning progression and helps users choose appropriate starting points.

### 4. Hybrid Documentation Conversion Strategy
**Decision**: Convert 3-4 high-impact documentation examples to runnable examples:
- Multi-source analytics (high value, commonly requested)
- Environment variables (security focus, best practices)
- DuckDB settings (performance optimization)

**Rationale**: These represent the most valuable scenarios that users want to run directly, while avoiding duplication of effort.

### 5. Validation and Testing Strategy
**Decision**: Include automated validation in each example:
- Syntax validation: `duckalog validate catalog.yaml`
- Data validation: Ensure generated data meets requirements
- Result validation: Verify expected views/tables are created
- Performance validation: Basic performance benchmarks for complex examples

**Rationale**: Ensures examples remain functional as Duckalog evolves and provides confidence for users.

## Risks / Trade-offs

### Risk: Example Maintenance Overhead
**Risk**: Large example library becomes maintenance burden
**Mitigation**:
- Automated validation in CI/CD pipeline
- Standardized structure reduces maintenance complexity
- Focus on high-value, stable use cases
- Clear deprecation policy for outdated examples

### Trade-off: Complexity vs. Accessibility
**Trade-off**: Complex examples demonstrate advanced features but may intimidate new users
**Mitigation**:
- Clear difficulty levels and prerequisites
- Progressive learning path with clear starting points
- Comprehensive README files with setup instructions
- Separate "basic" and "advanced" example categories

### Risk: Data Realism vs. Reproducibility
**Risk**: Realistic data may be complex to generate or reproduce
**Mitigation**:
- Use synthetic but realistic data generation
- Focus on business patterns rather than specific datasets
- Provide clear data schema and generation logic
- Use parameterized generators for different data sizes

### Risk: External Dependencies
**Risk**: Some examples require external services (cloud databases, etc.)
**Mitigation**:
- Use local alternatives where possible (DuckDB, SQLite)
- Provide mock data for external service examples
- Clear documentation of external requirements
- Optional components for external integrations

## Migration Plan

### Phase 1: Foundation (Week 1-2)
1. **Establish Standards**
   - Create example template and structure guidelines
   - Set up automated validation framework
   - Document example contribution guidelines

2. **Convert Key Documentation Examples**
   - Multi-source analytics example
   - Environment variable security example
   - DuckDB performance settings example

### Phase 2: Business Intelligence (Week 3-5)
1. **Customer Analytics Suite**
   - Implement cohort analysis example
   - Add customer lifetime value calculations
   - Create retention metrics example

2. **Time-Series Analytics**
   - Moving averages and trend analysis
   - Growth rate calculations
   - Seasonality analysis patterns

### Phase 3: Production Patterns (Week 6-8)
1. **CI/CD Integration**
   - GitHub Actions workflows
   - Automated testing patterns
   - Multi-environment configurations

2. **Scaling & Performance**
   - Large dataset handling examples
   - Performance optimization techniques
   - Monitoring and observability patterns

### Phase 4: Advanced Features (Week 9-12)
1. **Advanced Integrations**
   - Cloud data warehouse examples
   - Streaming data patterns
   - Advanced SQL feature demonstrations

2. **Web UI & Interactive Examples**
   - Dashboard setup examples
   - Real-time analytics configurations
   - Interactive query patterns

## Open Questions

### Example Scope and Boundaries
- Should examples include industry-specific scenarios (healthcare, finance, retail)?
- How to handle examples that require significant computational resources?
- Should we include "anti-patterns" or "what not to do" examples?

### Community Contribution
- How to structure community contribution process for new examples?
- What quality standards and review process for community submissions?
- Should we maintain separate "official" vs "community" example categories?

### Long-term Maintenance
- What deprecation policy for outdated examples?
- How to handle example updates when DuckDB or Duckalog APIs change?
- Should examples be versioned alongside Duckalog releases?

### Performance and Scale
- What are the resource limits for example execution in CI/CD?
- How to benchmark and document example performance characteristics?
- Should examples include performance optimization guidance?