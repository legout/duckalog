## MODIFIED Requirements

### Requirement: View Metadata Fields
The configuration layer MUST accept optional metadata fields `description` and `tags` on view definitions, and MUST preserve their values in the configuration model without affecting SQL generation.

#### Scenario: View with description
- **GIVEN** a view definition with a `description` string
- **WHEN** the configuration is loaded and validated
- **THEN** the description value is stored on the corresponding `ViewConfig` instance
- **AND** SQL generation for the view is unaffected by the description.

#### Scenario: View with tags
- **GIVEN** a view definition with a `tags` list of strings
- **WHEN** the configuration is loaded and validated
- **THEN** the tags are stored on the corresponding `ViewConfig` instance
- **AND** SQL generation for the view is unaffected by the tags.
