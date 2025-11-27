## ADDED Requirements
### Requirement: Config Initialization API
The system SHALL provide a Python API function `create_config_template()` that generates a basic, valid Duckalog configuration template.

#### Scenario: Generate basic YAML config template
- **WHEN** `create_config_template(format='yaml')` is called
- **THEN** a valid YAML configuration string is returned
- **AND** the config contains required fields: `version`, `duckdb`, `views`
- **AND** the config includes sensible defaults and example content
- **AND** the config can be loaded and validated successfully

#### Scenario: Generate basic JSON config template  
- **WHEN** `create_config_template(format='json')` is called
- **THEN** a valid JSON configuration string is returned
- **AND** the config contains the same structure and content as YAML version
- **AND** the config can be loaded and validated successfully

#### Scenario: Generate config with custom output path
- **WHEN** `create_config_template(format='yaml', output_path='custom_config.yaml')` is called
- **THEN** the configuration is written to the specified file path
- **AND** the file is created with proper permissions
- **AND** the function returns the generated configuration content

#### Scenario: Config template validation
- **WHEN** a generated config template is loaded using `load_config()`
- **THEN** the config loads without errors
- **AND** all required fields are present and properly typed
- **AND** example views can be processed by the SQL generation system

### Requirement: Config Template Content
The generated config template SHALL include educational and practical example content that demonstrates key features.

#### Scenario: Template includes example views
- **WHEN** a config template is generated
- **THEN** it includes at least one example view of each common type
- **AND** comments explain the purpose of each section
- **AND** example content is realistic but clearly marked as examples

#### Scenario: Template includes sensible defaults
- **WHEN** a config template is generated  
- **THEN** default DuckDB settings are provided
- **AND** example pragmas demonstrate common performance configurations
- **AND** database path defaults to a sensible local filename

#### Scenario: Template provides guidance
- **WHEN** a config template is generated
- **THEN** it includes inline comments or metadata explaining key concepts
- **AND** users can understand how to customize the generated template
- **AND** the template serves as both a working example and a learning aid