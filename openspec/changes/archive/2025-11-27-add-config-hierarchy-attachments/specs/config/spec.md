## ADDED Requirements
### Requirement: Duckalog config attachments
Duckalog configurations SHALL support attaching other Duckalog configs via `attachments.duckalog[]`, each entry providing an `alias`, a `config_path` to the child config file, an optional `database` override for the child catalog file, and an optional `read_only` flag that defaults to `true`.

#### Scenario: Valid nested config attachment accepted
- **GIVEN** a config with `attachments.duckalog` containing an entry with `alias: ref_data` and `config_path: ./ref/catalog.yaml`
- **AND** the referenced child config defines a `duckdb.database` file path (or the attachment supplies `database`)
- **WHEN** the configuration is loaded and validated
- **THEN** the attachment entry is accepted
- **AND** `read_only` defaults to `true` when omitted.

#### Scenario: Relative paths resolved for nested configs
- **GIVEN** a parent config located at `/projects/main/catalog.yaml`
- **AND** it declares `attachments.duckalog[0].config_path: "../shared/ref.yaml"` and `database: "./data/ref.duckdb"`
- **WHEN** the configuration is loaded
- **THEN** `config_path` resolves to `/projects/shared/ref.yaml`
- **AND** `database` resolves to `/projects/main/data/ref.duckdb`.

#### Scenario: Missing path or in-memory child rejected
- **GIVEN** a `attachments.duckalog` entry missing `alias` or `config_path`, **OR** referencing a child config whose effective database is `:memory:` without a `database` override
- **WHEN** the configuration is validated
- **THEN** validation fails with a clear error describing the missing field or requirement for a durable database path.
