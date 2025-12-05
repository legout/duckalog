# Proposal: Add SQL File and Template Support for Views

## Why
Current Duckalog behavior effectively forces all view definitions to use inline SQL (`sql`).
Although the configuration models and specs mention `sql_file` and template-based SQL, the
current implementation rejects any `sql_file` or `sql_template` usage in local configs and
leaves remote SQL loading in a partially implemented and inconsistent state.

This creates several pain points:
- Large or shared SQL cannot be cleanly managed in separate `.sql` files.
- SQL reuse across multiple views requires copy-pasting inline SQL.
- Template-based SQL with per-view variables (e.g. time windows, filters) is not usable
  in a supported way.

Users want to:
- Reference external SQL files from catalog YAML.
- Define SQL templates with placeholders and provide variables per view in the catalog
  entry itself.
- Keep inline SQL as the simplest option, while enabling more advanced patterns for
  complex projects.

## What Changes
This change will:

1. **Reintroduce and formalize SQL file support**
   - Support `sql_file` on views as a first-class way to source SQL from external files.
   - Integrate SQL file loading into the config pipeline for both local and remote configs.
   - Enforce path security and allowed-root validation for local SQL file paths.

2. **Add supported SQL template behavior**
   - Support `sql_template` on views as a way to load SQL templates with `{{variable}}`
     placeholders.
   - Allow each view to specify a `variables` mapping used for placeholder substitution.
   - Define clear semantics for missing variables and value substitution.

3. **Clarify loader and engine behavior**
   - When `load_config(..., load_sql_files=True)` is used, SQL files/templates are loaded
     and inlined into `view.sql` prior to SQL generation.
   - When `load_sql_files=False` is used, config validation may still succeed but no file
     IO or substitution occurs; callers that need executable SQL must handle this explicitly.

4. **Define error and logging expectations**
   - Use `SQLFileError` for file/path/template issues, with clear messages that include
     the view name and SQL path.
   - Log high-level events (e.g. "loading SQL file for view X") via the existing logging
     utilities.

## Out of Scope
- Introducing a full-featured templating engine like Jinja2 in this iteration.
- Adding new CLI flags or environment settings for alternate template dialects.
- Changing the SQL generation model beyond making it source SQL from inline/loaded content.
- Implementing conditional configuration or per-environment config overlays.

## Impact
- **Developer Experience**: Users can keep catalog YAML focused on configuration while
  editing SQL in dedicated `.sql` files with proper editor tooling.
- **Reusability**: Shared SQL (reports, common CTEs) can live in one file and be
  referenced by multiple views.
- **Flexibility**: Simple placeholder-based SQL templates allow per-view customization
  (date ranges, regions, feature flags) without copying whole queries.
- **Backward Compatibility**: Inline `sql` remains the simplest, fully supported option,
  and configs that do not use `sql_file`/`sql_template` remain unaffected.
