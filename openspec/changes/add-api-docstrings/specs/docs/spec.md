## MODIFIED Requirements

### Requirement: Public API Docstrings
Publicly documented Python APIs MUST include structured docstrings suitable for automated reference generation.

#### Scenario: Docstrings present for exported symbols
- **GIVEN** the list of names exported from `duckalog.__all__`
- **WHEN** inspecting their `.__doc__` in Python
- **THEN** each has a non-empty docstring describing its purpose and key parameters.

#### Scenario: Google-style structure
- **GIVEN** a function like `build_catalog` or `generate_sql`
- **WHEN** viewing its docstring
- **THEN** it is written in a Google-style format with sections such as `Args:`, `Returns:`, and `Raises:` as appropriate.

#### Scenario: Docstring examples are accurate
- **GIVEN** example code blocks in docstrings (e.g., for `load_config` or `build_catalog`)
- **WHEN** a user runs those examples with minimal setup
- **THEN** they execute successfully and match the described behavior.

