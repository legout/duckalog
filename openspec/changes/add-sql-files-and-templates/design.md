# Design: SQL File and Template Support for Views

## Goals
- Allow view definitions to source SQL from external files (`sql_file`) as well as inline `sql` fields.
- Provide a simple, explicit SQL template mechanism (`sql_template` + per-view `variables`) for parameterized SQL.
- Keep inline SQL as the default, simplest option; external SQL is additive, not required.
- Ensure consistent behavior for both local and remote configs with clear error handling and logging.

## Non-Goals
- Introducing Jinja2 or any other full template engine in this iteration.
- Implementing conditional configuration or complex multi-pass templating.
- Changing the SQL generation model beyond selecting the correct SQL body for each view.

## Configuration Model

### ViewConfig SQL Sources
Views can specify exactly one of the following SQL sources:
- `sql`: Inline SQL text (current behavior).
- `sql_file`: External SQL file reference for plain SQL.
- `sql_template`: External SQL file reference treated as a template.

Key points:
- `sql_file` and `sql_template` share the same underlying reference shape (path + optional variables + flags).
- Validation enforces `sql` XOR `sql_file` XOR `sql_template` for each view.
- `path` must be a non-empty string; extra fields in the mapping are rejected by Pydantic.

### Template Variables
- `sql_template` includes a `variables: dict[str, Any]` mapping.
- Variables are converted to strings via `str(value)` during substitution.
- The template engine does **not** auto-quote or escape values; SQL authors must write safe patterns (e.g. `'{{start_date}}'::date`).

## Loading Pipeline

### Local Configs (`load_config`)
- `load_config(path, load_sql_files=True, ...)` will:
  1. Read and parse YAML/JSON.
  2. Interpolate `${env:VAR}` placeholders.
  3. Validate into `Config` (including `ViewConfig` validation).
  4. Invoke `_load_sql_files_from_config(config, config_path, sql_file_loader)`.
- `_load_sql_files_from_config` will:
  - Iterate over `config.views`.
  - For each view with `sql_file` or `sql_template`:
    - Resolve the path relative to the config directory (for non-remote paths).
    - Validate the resolved path using existing path-security helpers.
    - Load file content from disk.
    - If `sql_template` (or `sql_file` with template flag, if enabled later):
      - Render the template using the simple placeholder engine.
    - Construct a new `ViewConfig` with `sql` set to the final content and `sql_file`/`sql_template` cleared.

### Remote Configs (`load_config_from_uri`)
- `load_config_from_uri(uri, load_sql_files=True, ...)` will:
  1. Fetch config content via `fetch_remote_content`.
  2. Parse, interpolate env vars, and validate into `Config`.
  3. If `load_sql_files=True`, delegate to `_load_sql_files_from_remote_config`.
- `_load_sql_files_from_remote_config` will:
  - Mirror local behavior but treat SQL paths as:
    - Remote URIs (http/s3/etc.): load content via `fetch_remote_content`; skip local path-security checks.
    - Local/relative paths: resolve relative to a synthetic config directory derived from the URI path and apply the same path-security checks as local configs.

## Template Engine Semantics

### Placeholder Format
- Placeholders use a minimal Mustache-like syntax: `{{variable}}`.
- A simple regex will identify placeholders and their variable names.

### Rendering Rules
- Collect the set of placeholder names from the template content.
- For each view:
  - Look up `variables` from the `sql_template` reference.
  - Verify that every placeholder has a corresponding key in `variables`:
    - If any are missing, raise `SQLFileError` with the missing key name, view name, and SQL path.
  - Replace `{{name}}` with `str(variables["name"])` for each placeholder.
- No evaluation, conditionals, loops, or expressions are supported in this iteration.

## Error Handling and Logging

### Error Types
- IO/path/template issues during SQL file handling will raise `SQLFileError` with context:
  - View name.
  - SQL path (resolved and/or original).
  - Short description of the failure (missing file, disallowed path, missing variable, etc.).
- Local config errors wrap `SQLFileError` as `ConfigError` where appropriate.
- Remote config errors wrap `SQLFileError` as `RemoteConfigError` while preserving the original exception via `raise ... from exc`.

### Logging
- Use existing logging utilities (`log_info`, `log_debug`) for events such as:
  - Starting SQL file load for a view.
  - Number of views using external SQL.
  - Summary of remote SQL fetch operations.
- Avoid logging raw SQL content at INFO level; allow DEBUG logging to include more detail when configured.

## Interaction with SQL Generation

- After `load_config(..., load_sql_files=True)`, all views must either:
  - Have `sql` populated (from inline or loaded content), or
  - Have a valid `source` so that scan-based SQL can be generated.
- `generate_view_sql` remains unchanged in structure:
  - It selects the SQL body from `view.sql` when present.
  - Otherwise, it uses existing source-based rendering.
- This design keeps SQL file/template handling entirely in the config layer, so the SQL generation module does not need to know whether SQL was inline or loaded.

## Backward Compatibility

- Inline `sql` remains fully supported and is unaffected by these changes.
- Existing configs that do not use `sql_file` or `sql_template` behave exactly as before.
- Older or experimental usages of `sql_file`/`sql_template` that currently cause errors will become supported when they conform to the new spec.
- The `load_sql_files` flag preserves a non-IO mode where external SQL is not loaded; callers using this mode must not assume SQL files are available unless they handle them explicitly.

## Open Questions
- Do we want a follow-up change to support a richer template engine (Jinja2) for advanced projects?
- Should we add per-project or per-view options controlling how variables are quoted/escaped, or keep that responsibility on SQL authors?
- Do we need dedicated CLI options to validate SQL file references without performing a full catalog build?
