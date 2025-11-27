## ADDED Requirements
### Requirement: CLI Init Command
The CLI SHALL expose an `init` command that creates a new Duckalog configuration file.

#### Scenario: CLI creates YAML config file
- **WHEN** `duckalog init` is executed
- **THEN** a file named `catalog.yaml` is created in the current directory
- **AND** the file contains a valid, basic Duckalog configuration
- **AND** the command prints success message with file location

#### Scenario: CLI creates JSON config file
- **WHEN** `duckalog init --format json` is executed
- **THEN** a file named `catalog.json` is created in the current directory
- **AND** the file contains the same configuration structure as YAML but in JSON format
- **AND** the command prints success message with file location

#### Scenario: CLI creates custom filename
- **WHEN** `duckalog init --output my_config.yaml` is executed
- **THEN** a file named `my_config.yaml` is created with the configuration
- **AND** the command prints success message with the specified filename

#### Scenario: CLI handles file overwrite confirmation
- **WHEN** `duckalog init` is executed in a directory that already contains the target file
- **THEN** the command prompts for confirmation before overwriting
- **AND** with `--force` flag, the command overwrites without prompting
- **AND** with `--skip-existing` flag, the command skips creating the file

#### Scenario: CLI validates generated config
- **WHEN** `duckalog init` creates a configuration file
- **THEN** the generated file is immediately validated
- **AND** if validation fails, an error is displayed and no file is created
- **AND** if validation succeeds, a success message is shown

### Requirement: CLI Init Command Options
The CLI init command SHALL support options for format, output path, and behavior customization.

#### Scenario: Format option support
- **WHEN** `duckalog init --format yaml` is executed
- **THEN** a YAML file is created (default behavior)
- **WHEN** `duckalog init --format json` is executed  
- **THEN** a JSON file is created
- **AND** invalid format values are rejected with an error message

#### Scenario: Output path options
- **WHEN** `duckalog init --output path/to/config.yaml` is executed
- **THEN** the configuration is created at the specified path
- **AND** parent directories are created if they don't exist
- **AND** relative paths are resolved relative to the current working directory

#### Scenario: Interactive mode support
- **WHEN** `duckalog init --interactive` is executed
- **THEN** the command prompts for basic customization options
- **AND** users can specify database name, view names, and other basic settings
- **AND** the generated config reflects the user's input choices