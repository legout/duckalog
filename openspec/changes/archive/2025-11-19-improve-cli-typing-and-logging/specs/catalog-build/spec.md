## MODIFIED Requirements

### Requirement: CLI Build Command

#### Scenario: Type-checker friendly CLI definitions
- **WHEN** the CLI build, generate-sql, and validate commands are defined in `duckalog.cli`
- **THEN** their function signatures SHOULD use framework-recommended patterns (for example, Typer’s `Annotated[...]` with `Argument(...)` and `Option(...)`)
- **AND** parameter types and defaults SHOULD be compatible from the perspective of static type checkers
- **AND** these typing improvements MUST NOT change the external CLI behavior observed by users.

