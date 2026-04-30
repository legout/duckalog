# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records (ADRs) for the Duckalog configuration system refactoring.

## ADRs

- [ADR-001: Break Monolithic loader.py](adr-001-break-monolithic-loader.md) - Decision to split the 1,670-line monolithic loader into focused modules
- [ADR-002: Eliminate Circular Dependencies](adr-002-eliminate-circular-dependencies.md) - Resolution of circular import issues between config and remote_config modules

## About ADRs

ADRs are documents that capture an important architectural decision made along with its context and consequences. They are intended to be:

- **Succinct**: Easy to read and understand
- **Specific**: Focus on one decision per document
- **Current**: Reflect the current state of the system
- **Verifiable**: Link to relevant code or documentation

## Contributing

When making significant architectural changes:

1. Create a new ADR following the established format
2. Include the decision, context, and consequences
3. Update this index to reference the new ADR
4. Link related ADRs in the "See also" section

For more information about ADRs, see [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) by Michael Nygard.