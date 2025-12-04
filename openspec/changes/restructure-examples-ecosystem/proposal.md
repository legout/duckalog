# Proposal: Restructure Examples Ecosystem

## Change ID
restructure-examples-ecosystem

## Summary
Complete refactoring of the examples folder to create a structured, beginner-to-advanced learning path with proper data generation, external service setup (PostgreSQL, S3), and simplified examples.

## Context
The current examples folder has several critical issues:
- Incomplete examples (missing SQL files, external databases)
- Heavy data files (274MB+ in version control)
- No clear learning progression
- Missing setup for external services
- Inconsistent structure across examples

This makes it difficult for users to understand and use duckalog effectively.

## Goals
1. Create a numbered category system (01-getting-started, 02-intermediate, 03-advanced, etc.)
2. Add shared data generators using `faker` library
3. Provide docker-compose setup for PostgreSQL and S3-compatible storage (MinIO)
4. Create simple, working examples for each concept
5. Add missing example types (CSV, Iceberg, Delta Lake)
6. Remove complex/incomplete examples (CI/CD integration)
7. Maintain only runnable, complete examples

## Non-Goals
- Adding new duckalog features
- Modifying core library behavior
- Creating comprehensive documentation beyond examples

## Impact
- Users can learn duckalog incrementally from simple to advanced
- All examples work out of the box with minimal setup
- Repository size reduced by removing pre-built data files
- Clear structure makes it easy to find relevant examples

## Alternatives Considered
1. Keep existing structure and fix incrementally - rejected because problems are too systemic
2. Separate examples into external repo - rejected because examples should be part of main repo
3. Keep CI/CD example - rejected due to complexity and GitHub-specific nature

## Implementation Approach
- Phase 1: Foundation (shared generators, main README)
- Phase 2: Getting Started examples (parquet, CSV, DuckDB, SQLite)
- Phase 3: Intermediate examples (SQL transforms, joins, semantic layer)
- Phase 4: Advanced examples (semantic v2, env vars, performance, Iceberg, Delta Lake)
- Phase 5: External services (PostgreSQL, S3, multi-source)
- Phase 6: Use cases (customer analytics, product analytics, time series)
- Phase 7: Cleanup (remove old structure)

## Open Questions
None at this time.

## Dependencies
None - this is a pure refactoring effort.

## Risks
- Breaking existing user references to old example paths
- Complexity of docker-compose setups for some examples

## Success Criteria
- All examples have working setup.py scripts
- All examples include README.md with clear setup instructions
- No pre-built data files in git (only .gitkeep placeholders)
- Main README provides clear learning path
- Docker-compose examples work with `make up` commands
