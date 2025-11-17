## MODIFIED Requirements

### Requirement: Catalog Config Format

#### Scenario: Optional SQL file references handled safely
- **WHEN** a view or related configuration field includes an optional reference to an external SQL file
- **AND** that reference is absent (`null` / omitted)
- **THEN** the configuration loader or validator SHALL NOT assume the reference is present
- **AND** SHALL avoid accessing attributes such as `.path` on a missing reference
- **AND** SHALL raise a clear configuration error if the reference is required for the chosen source type.

### Requirement: DuckDB Settings Configuration

#### Scenario: Nullable string settings normalized safely
- **WHEN** a configuration field representing a setting or pragma may be `null` or an empty string
- **THEN** the loader or validator SHALL normalize or guard the value before calling string methods (such as `.strip()`)
- **AND** SHALL treat invalid or missing values as configuration errors rather than relying on attribute access on `None`.

