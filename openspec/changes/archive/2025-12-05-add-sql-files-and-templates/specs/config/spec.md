## ADDED Requirements

### Requirement: SQL File and Template Sources
View definitions MAY reference external SQL files or SQL templates in addition to inline SQL, but each view MUST declare at most one SQL source.

#### Scenario: View uses sql_file for external SQL
- **GIVEN** a config where a view includes a `sql_file` reference with a non-empty `path`
- **WHEN** `load_config()` is called with `load_sql_files=True`
- **THEN** the loader SHALL resolve the SQL file path relative to the config file directory (for non-remote paths)
- **AND** validate the resolved path using the existing path security rules
- **AND** read the file content and populate `view.sql` with the loaded SQL text
- **AND** clear the `sql_file` reference on the resulting configuration object.

#### Scenario: View uses sql_template with variables
- **GIVEN** a config where a view includes a `sql_template` reference with `path` and a `variables` mapping
- **WHEN** `load_config()` is called with `load_sql_files=True`
- **THEN** the loader SHALL load the template content from the referenced file
- **AND** perform placeholder substitution for `{{variable}}` markers using the provided `variables`
- **AND** raise a configuration or SQL file error if any placeholder has no corresponding variable value
- **AND** populate `view.sql` with the rendered SQL text, clearing the `sql_template` reference.

#### Scenario: Exclusive SQL source per view
- **GIVEN** a config where a view defines more than one SQL source among `sql`, `sql_file`, and `sql_template`
- **WHEN** the configuration is validated
- **THEN** validation SHALL fail with a clear error indicating that only one of `sql`, `sql_file`, or `sql_template` may be specified per view.

#### Scenario: Loading config without processing SQL files
- **GIVEN** a config that uses `sql_file` or `sql_template` on one or more views
- **WHEN** `load_config()` is called with `load_sql_files=False`
- **THEN** the configuration MAY be validated successfully without performing any SQL file IO or template processing
- **AND** the resulting `Config` instance SHALL preserve the `sql_file` and `sql_template` references for callers that wish to handle them explicitly.
