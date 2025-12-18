## ADDED Requirements
### Requirement: SQL Utilities Module
The system SHALL provide a centralized `sql_utils.py` module containing shared SQL utility functions used across the codebase.

#### Scenario: SQL utilities module created
- **WHEN** code requires SQL quoting or rendering functionality
- **THEN** `from duckalog.sql_utils import quote_ident, quote_literal, render_options` SHALL work
- **AND** these functions SHALL be available as a single source of truth
- **AND** all functions SHALL preserve their exact current behavior and signatures

#### Scenario: Functions imported from shared module
- **WHEN** `sql_generation.py` requires SQL utility functions
- **THEN** it SHALL import `quote_ident`, `quote_literal`, `render_options` from `sql_utils`
- **AND** `engine.py` SHALL import these functions from `sql_utils`
- **AND** `config/validators.py` SHALL import these functions from `sql_utils`
- **AND** all import paths SHALL use the consolidated module

## MODIFIED Requirements
### Requirement: SQL Generation Function Location
The SQL generation module SHALL import shared utilities from the new `sql_utils.py` module instead of containing function definitions.

#### Scenario: SQL generation uses shared utilities
- **WHEN** SQL generation functions are called
- **THEN** `sql_generation.py` SHALL import `quote_ident`, `quote_literal`, `render_options` from `sql_utils`
- **AND** the functions SHALL work identically to current implementation
- **AND** no duplicate implementations SHALL exist in `sql_generation.py`

#### Scenario: Deprecated function removal
- **WHEN** code references the deprecated `_quote_literal` function
- **THEN** it SHALL be removed entirely from the codebase
- **AND** all internal usage SHALL be updated to use `quote_literal` directly
- **AND** the function SHALL no longer be exported from any module

## REMOVED Requirements
### Requirement: Deprecated Function Elimination
**Reason**: The `_quote_literal` function is a deprecated duplicate that creates maintenance burden
**Migration**: Use `quote_literal` directly from the shared `sql_utils` module