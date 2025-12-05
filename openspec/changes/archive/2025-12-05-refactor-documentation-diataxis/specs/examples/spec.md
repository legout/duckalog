## ADDED Requirements

### Requirement: Config Imports Comprehensive Guide
The examples SHALL include a comprehensive guide for config imports feature explaining import resolution, merge behavior, diagnostics, and best practices.

#### Scenario: Import resolution understanding
- **GIVEN** a user wanting to use config imports
- **WHEN** they read the config imports guide
- **THEN** they find detailed explanation of:
  - Import path resolution (relative to config file)
  - Import processing order
  - Remote import support (S3, GCS, Azure, HTTP)
  - Circular dependency detection
- **AND** they see practical examples of each import type
- **SO** they understand how imports are resolved and processed

#### Scenario: Merge behavior documentation
- **GIVEN** a user with conflicting definitions across imported configs
- **WHEN** they consult the config imports guide
- **THEN** they find documentation of merge strategies:
  - How views are merged/overridden
  - How attachments are combined
  - How secrets are merged
  - Conflict resolution rules
- **AND** they see examples of merge outcomes
- **SO** they can predict and control merge behavior

#### Scenario: Diagnostics usage guide
- **GIVEN** a user debugging import issues
- **WHEN** they need to use show-imports diagnostics
- **THEN** they find guide documentation showing:
  - How to use --diagnostics flag
  - How to interpret import graph output
  - How to use --show-merged to preview final config
  - How to export import graph as JSON
- **AND** they see example diagnostic outputs with explanations
- **SO** they can effectively debug import problems

#### Scenario: Config imports best practices
- **GIVEN** a user organizing large configurations
- **WHEN** they look for organizational guidance
- **THEN** they find best practices for config imports:
  - When to use imports vs single file
  - How to organize shared configurations
  - Patterns for environment-specific configs
  - Import depth recommendations
- **AND** they see real-world organizational examples
- **SO** they can organize configurations effectively

### Requirement: Example Metadata and Prerequisites
Each example SHALL include metadata indicating difficulty level, prerequisites, learning objectives, and estimated completion time.

#### Scenario: Example difficulty identification
- **GIVEN** a user browsing examples
- **WHEN** they view any example page
- **THEN** they see a difficulty level indicator (Beginner/Intermediate/Advanced)
- **AND** they see prerequisites listed (e.g., "Complete 'Simple Parquet' example first")
- **AND** they see "What you'll learn" section
- **AND** they see estimated time to complete
- **SO** they can assess if the example is appropriate for their level

#### Scenario: Learning objectives clarity
- **GIVEN** a user selecting an example to work through
- **WHEN** they read the example introduction
- **THEN** they find clear learning objectives stating what skills they'll gain
- **AND** objectives align with the difficulty level
- **AND** objectives specify what they'll be able to do after completion
- **SO** they have clear expectations of outcomes

#### Scenario: Progressive skill indicators
- **GIVEN** a user completing multiple examples
- **WHEN** they track their progress
- **THEN** they can see how examples build on each other
- **AND** they can identify their current skill level
- **AND** they can choose appropriate next examples
- **SO** they can follow a coherent learning path

### Requirement: Example Cross-Referencing
Examples SHALL include cross-references to related examples, relevant how-to guides, and reference documentation to facilitate learning and discovery.

#### Scenario: Related examples discovery
- **GIVEN** a user completing an example
- **WHEN** they finish the example
- **THEN** they see "Related Examples" section suggesting:
  - Prerequisite examples (if not already completed)
  - Next logical examples in learning progression
  - Alternative approaches to similar problems
- **SO** they can continue learning systematically

#### Scenario: Reference documentation links
- **GIVEN** a user working through an example
- **WHEN** they encounter configuration options or commands
- **THEN** they find links to reference documentation for:
  - Configuration schema for options used
  - CLI command reference for commands demonstrated
  - API reference for functions called
- **SO** they can learn more details about specific features

#### Scenario: How-to guide connections
- **GIVEN** a user understanding example concepts
- **WHEN** they want to apply concepts to real problems
- **THEN** they find links to relevant how-to guides:
  - "See how to debug this in production" → troubleshooting guide
  - "Learn to optimize this pattern" → performance tuning guide
  - "Adapt this for multiple environments" → environment management guide
- **SO** they can bridge from learning to practical application
