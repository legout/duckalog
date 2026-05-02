# Code Context — catalog-studio-form-editor

## Files Retrieved

### Predecessor ExecPlans (chain of dependencies)

1. `.execflow/plans/catalog-studio-editing-safety/execplan.md` (lines 1-300) — The editing safety service that this form editor plan depends on. Defines `src/duckalog/studio/editing.py` with `load_editable_config()`, `validate_config_text()`, `preview_config_diff()`, `save_config_text_safely()`. Key constraints: local-only writes, raw-text preservation (NOT `Config.model_dump()`), `difflib.unified_diff()`, `os.replace()` for atomic save, `shutil.copy2()` for backups, `Config.model_validate()` as canonical structure gate.

2. `.execflow/plans/catalog-studio-expert-editor/execplan.md` (lines 1-200) — The expert YAML/JSON editor that exercises the same safety service with raw textarea text. Key constraint: Expert editor must call the safety service, not inline file-write logic. Defines route names `GET /config/expert`, `POST /config/expert/validate`, `POST /config/expert/preview`, `POST /config/expert/save`. The form editor plan should NOT add the same raw-text routes — it should add structured form routes instead.

3. `.execflow/plans/rebuild-duckalog-ui-starhtml/brainstorm.md` (lines 1-131) — Umbrella product direction. Decision: "Build a new StarHTML-based UI from scratch rather than directly replacing the existing dashboard." Key constraint: "Catalog editing should be form/menu-based for normal users, with an expert mode providing a full-featured YAML or JSON editor."

### Config model — canonical structure source of truth

4. `src/duckalog/config/models.py` (lines 1-700) — `Config`, `ViewConfig`, and all supporting models. The authoritative Pydantic validation gate. All structured form fields derive from this file. Key fields for a first structured editor:

**`Config` top-level fields (line 570+):**
```python
version: int  # positive integer
duckdb: DuckDBConfig  # required
views: list[ViewConfig]  # required
attachments: AttachmentsConfig  # default=AttachmentsConfig
iceberg_catalogs: list[IcebergCatalogConfig]  # default=[]
semantic_models: list[SemanticModelConfig]  # default=[]
imports: Union[list[Union[str, ImportEntry]], SelectiveImports]  # default=[]
env_files: list[str]  # default=[".env"]
loader_settings: LoaderSettings  # default=LoaderSettings
```

**`DuckDBConfig` fields (line 130+):**
```python
database: str  # default=":memory:"
install_extensions: list[str]  # default=[]
load_extensions: list[str]  # default=[]
pragmas: list[str]  # default=[]
settings: Optional[Union[str, list[str]]]  # optional
secrets: list[SecretConfig]  # default=[]
```

**`ViewConfig` fields (line 300+):**
```python
name: str  # required, stripped, non-empty
db_schema: Optional[str]  # optional, stripped
sql: Optional[str]  # optional, mutually exclusive with sql_file/sql_template
sql_file: Optional[SQLFileReference]  # optional, mutually exclusive
sql_template: Optional[SQLFileReference]  # optional, mutually exclusive
source: Optional[EnvSource]  # "parquet"|"delta"|"iceberg"|"duckdb"|"sqlite"|"postgres"
uri: Optional[str]  # required for parquet/delta
database: Optional[str]  # required for duckdb/sqlite/postgres
table: Optional[str]  # required for duckdb/sqlite/postgres
catalog: Optional[str]  # optional for iceberg
options: dict[str, Any]  # default={}
description: Optional[str]  # optional
tags: list[str]  # default=[]
```

**Key validation constraint (line 385+):** `ViewConfig._validate_definition()` — exactly one of `sql`, `sql_file`, or `sql_template` is allowed. If `sql_file` is set, `sql_file.path` must be non-empty.

**`SQLFileReference` fields:**
```python
path: str  # required
variables: Optional[dict[str, Any]]  # default=None
as_template: bool  # default=False
```

**`SemanticModelConfig` fields (line 540+):**
```python
name: str  # required
base_view: str  # required, must reference existing view
dimensions: list[SemanticDimensionConfig]  # default=[]
measures: list[SemanticMeasureConfig]  # default=[]
joins: list[SemanticJoinConfig]  # default=[]
defaults: Optional[SemanticDefaultsConfig]  # optional
label: Optional[str]  # optional
description: Optional[str]  # optional
tags: list[str]  # default=[]
```

**`SecretConfig` fields (line 30+):**
```python
type: SecretType  # "s3"|"azure"|"gcs"|"http"|"postgres"|"mysql", required
name: Optional[str]  # optional
provider: SecretProvider  # "config"|"credential_chain", default="config"
persistent: bool  # default=False
scope: Optional[str]  # optional
key_id: Optional[str]  # optional
secret: Optional[str]  # optional
region: Optional[str]  # optional
endpoint: Optional[str]  # optional
connection_string: Optional[str]  # optional
tenant_id: Optional[str]  # optional
account_name: Optional[str]  # optional
client_id: Optional[str]  # optional
client_secret: Optional[str]  # optional
service_account_key: Optional[str]  # optional
json_key: Optional[str]  # optional
bearer_token: Optional[str]  # optional
header: Optional[str]  # optional
database: Optional[str]  # optional
host: Optional[str]  # optional
port: Optional[int]  # optional, 1-65535
user: Optional[str]  # optional
password: Optional[str]  # optional
options: dict[str, Any]  # default={}
```

### Config loading API — how to reload and re-validate

5. `src/duckalog/config/api.py` (lines 1-80) — `load_config()` with `load_sql_files: bool = True`. Pass `load_sql_files=False` for reload verification to avoid SQL file inlining side effects.

### StarHTML and Datastar — UI framework and signal patterns

6. `research.md` (lines 1-264) — StarHTML research. Key API patterns:
- Signal definition: `(name := Signal("name", ""))` — walrus syntax, auto-compiles to Datastar JS
- Element attributes: `data_bind`, `data_text`, `data_on_click`, `data_show`, `data_indicator`
- Logical operators: `name & email` → JS `!!$name && !!$email`; `~is_visible` → `!$is_visible`
- Signal operations: `counter.add(1)` → JS `$counter++`; `name.upper()` → `$name.toUpperCase()`
- Routing: `@rt()` decorator, `star_app()`, `serve()`
- **CRITICAL for form editor**: Use `+` for reactive strings (`"Count: " + counter`), NOT f-strings (f-strings are static in reactive contexts)

7. `docs/dashboard/datastar-patterns.md` (lines 1-200) — Datastar signal patterns from existing dashboard. Key patterns:
- Signal initialization: `div(**{"data-signals": json.dumps(signals_dict)})`
- Binding: `input(**{"data-bind": "sql", "data-debounce": "300"})`
- POST with data: `button(**{"data-on-click": "$$post('/api/action', {id: 123})"})`
- SSE patches: `yield SSE.patch_signals({"error": "", "loading": True})`
- Element patches: `yield SSE.patch_elements(html, selector="#results", mode="morph")`
- Debounce: `data-debounce="300"` attribute on bound inputs
- Form validation: read signals, validate, yield errors or proceed

8. `docs/dashboard/components.md` (lines 1-200) — Form component patterns:
- `input(**{"data-bind": bind_to, "data-debounce": "300"})` for text fields
- `textarea(..., **{"data-bind": "sql"})` for SQL input
- `select` with `**{"data-bind": bind_to}`
- `checkbox` with `**{"data-bind": bind_to, "data-checked": f"${bind_to}"}`
- Alert: `div(**{"data-show": f"$showAlert && $alertType === '{type_}'"})`
- Loading spinner: `div(**{"data-show": "$loading"})`
- Buttons with `data-on-click` and `data-indicator`

### Existing config write behavior — what the safety service replaces

9. `src/duckalog/config_init.py` (lines 140-195) — `_write_config_file()` uses `Path.write_text()` with no atomicity, no backup. `_format_as_yaml()` uses `yaml.dump()` which destroys comments. These are the unsafe patterns the safety service replaces.

10. `src/duckalog/config/loading/sql.py` (lines 1-200) — `process_sql_file_references()` replaces `sql_file` with inline `sql`. This is why the form editor must preserve `sql_file` references in the generated YAML — serializing the loaded `Config` would lose them.

### Existing UI patterns for reference

11. `src/duckalog/dashboard/routes/query.py` (lines 1-200) — **`textarea`** with Datastar `data-bind` for SQL input. Line 19: `from htpy import ... textarea`. Line 54: `textarea(id="sql-input", name="sql", rows="6", class_="...font-mono", **{"data-bind": "sql"})`. The expert editor will follow this pattern; the form editor should use StarHTML components.

12. `src/duckalog/config/security/path.py` (lines 1-300) — `validate_path_security()`, `is_within_allowed_roots()`, `is_remote_uri()`. These are reused by the editing safety service for path safety checks.

## Key Code

### Config draft from editing safety service

```python
# From .execflow/plans/catalog-studio-editing-safety/execplan.md
# src/duckalog/studio/editing.py  (to be created by the predecessor plan)

load_editable_config(path)
# -> draft: {path: Path, format: str, text: str, validated_config: Config}

validate_config_text(text, format, base_path)
# -> {ok: bool, errors: list[str], parsed_config: Config | None}

preview_config_diff(original_text, proposed_text, path)
# -> {text: str, stats: {added: int, removed: int, changed: int}}

save_config_text_safely(path, proposed_text)
# -> {ok: bool, backup_path: Path | None, reload_status: str, errors: list[str]}
```

### Form editor flow: Config model → proposed YAML → safety service → save

```python
# Conceptual: form generates proposed text, safety service saves it

from duckalog.studio.editing import (
    load_editable_config,
    validate_config_text,
    preview_config_diff,
    save_config_text_safely,
)

# 1. Load raw text from disk
draft = load_editable_config(config_path)

# 2. Form generates proposed YAML from in-memory Config edits
from duckalog.config.models import Config
proposed_config = Config.model_validate(form_values_dict)
from duckalog.config import serialization  # hypothetical module
proposed_text = serialization.dump_as_yaml(proposed_config, preserve_references=True)

# 3. Validate proposed text (NOT Config object — raw text, to preserve comments/sql_file refs)
validation = validate_config_text(proposed_text, "yaml", base_path=config_path)
if not validation.ok:
    return form_error(validation.errors)

# 4. Preview diff before save
diff = preview_config_diff(draft.text, proposed_text, config_path)

# 5. Save through safety service (backup, atomic write, reload verification)
result = save_config_text_safely(config_path, proposed_text)
```

### ViewConfig mutually exclusive SQL sources

```python
# src/duckalog/config/models.py:ViewConfig._validate_definition()
# CRITICAL: exactly ONE of sql, sql_file, sql_template allowed
has_sql = bool(self.sql and self.sql.strip())
has_sql_file = self.sql_file is not None
has_sql_template = self.sql_template is not None
sql_sources = sum([has_sql, has_sql_file, has_sql_template])
if sql_sources > 1:
    raise ValueError("View cannot have multiple SQL sources...")
```

### StarHTML form signal naming conventions

```python
# From research.md and datastar-patterns.md
# Signal names use snake_case, descriptive, organized by feature

(catalog_edit_name := Signal("catalog_edit_name", ""))
(catalog_edit_description := Signal("catalog_edit_description", ""))
(is_validating := Signal("is_validating", False))
(is_saving := Signal("is_saving", False))
(validation_ok := Signal("validation_ok", False))
(has_preview := Signal("has_preview", False))
(last_saved_at := Signal("last_saved_at", ""))
(error_messages := Signal("error_messages", []))
```

## Architecture

```
duckalog studio catalog.yaml
  → duckalog.studio.create_app(config, config_path, ...)
      → StudioContext (state)
      → StarHTML ASGI app
          ├── /catalog  (GET — overview page, disabled editor placeholders)
          ├── /catalog/views  (GET — views list)
          ├── /catalog/views/{name}  (GET — single view detail)
          ├── /catalog/forms/view/{name}  (GET — structured form for a view)
          │   → POST /catalog/forms/view/validate  (validate proposed edits)
          │   → POST /catalog/forms/view/preview  (preview diff)
          │   → POST /catalog/forms/view/save  (save through safety service)
          ├── /catalog/forms/duckdb  (GET — DuckDB settings form)
          ├── /catalog/forms/secret  (GET — secret creation form)
          ├── /catalog/expert  (GET — expert raw YAML/JSON editor, placeholder)
          └── /config/expert  → expert editor (separate plan's route)

src/duckalog/studio/editing.py  (pure Python service, no StarHTML)
  → load_editable_config()      # reads raw text from local file
  → validate_config_text()      # parses + Config.model_validate()
  → preview_config_diff()       # difflib.unified_diff()
  → save_config_text_safely()   # backup + atomic replace + reload

src/duckalog/studio/forms.py  (NEW — form components, StarHTML)
  → view_form_page(view_name, draft, validation=None, diff=None)
  → view_list_page(views, selected=None)
  → duckdb_settings_form(draft, validation=None)
  → signal field definitions

src/duckalog/studio/app.py  (StarHTML routes)
  → /catalog/views/{name}  GET
  → /catalog/forms/view/{name}  GET
  → /catalog/forms/view/validate  POST
  → /catalog/forms/view/preview  POST
  → /catalog/forms/view/save  POST
```

The form editor generates YAML (not raw Datastar edits) from a structured `Config` object, then passes that proposed text to the editing safety service. This is the critical distinction from the expert editor: the expert editor accepts user-written raw text directly; the form editor constructs structured text from model edits. Both flows end at the same safety service.

## Start Here

1. **Read the predecessor ExecPlan** at `.execflow/plans/catalog-studio-editing-safety/execplan.md` to understand the safety service contract before designing any form components.

2. **Open `src/duckalog/config/models.py`** lines 1-700. This is the canonical field reference. Every form field must map to a field on `Config`, `ViewConfig`, `DuckDBConfig`, `SecretConfig`, or related models. Do not invent field names or types that don't exist in these models.

3. **Open `research.md`** lines 1-100 for StarHTML signal naming and reactive string rules. The form editor must follow `counter.add(1)` style signal operations, use snake_case signal names, and use `+` for reactive string concatenation.

4. **Open `docs/dashboard/datastar-patterns.md`** lines 1-200 for Datastar signal/request patterns. The form editor's validation and save routes need to read signals and yield SSE patches.

## Independently Verifiable Milestones

### M1: Views list with link to structured form
- `GET /catalog/views` renders a list of all catalog views with names.
- Each view name is a link to `/catalog/forms/view/{name}`.
- No file writes occur.

**Test**: Write a YAML with 3 views, GET `/catalog/views`, verify all 3 names appear as links.

### M2: View form renders existing values
- `GET /catalog/forms/view/{name}` renders form fields pre-populated from the loaded `Config`.
- Form fields include: `name`, `db_schema`, `description`, `tags`, `source`, `uri`/`database`/`table`/`catalog` (shown conditionally), `sql`/`sql_file`/`sql_template` (exactly one section shown), `options`.
- The form shows the raw file path and format in a header.

**Test**: GET `/catalog/forms/view/demo`, verify `name: demo` pre-fills the name field.

### M3: View form client-side signal state
- Each form field binds to a StarHTML signal via `data-bind`.
- Changing a field updates the corresponding signal.
- StarHTML reactive string expressions use `+` for concatenation, not f-strings.

**Test**: Change the view name field, verify the signal update uses `name + " (modified)"` reactive pattern.

### M4: Validation POST without file write
- `POST /catalog/forms/view/validate` accepts form field values.
- It calls `validate_config_text()` with the reconstructed YAML.
- Returns structured validation errors via SSE patch.
- Does NOT write to disk.

**Test**: POST malformed YAML fragment to validate, expect error panel, no backup file created.

### M5: Preview diff from form edits
- `POST /catalog/forms/view/preview` generates proposed YAML from form values, calls `preview_config_diff()`, returns unified diff.
- Diff shows original raw text vs proposed form-generated text.

**Test**: Change `description` from "demo" to "demo updated", POST to preview, verify diff shows both lines.

### M6: Save through safety service with backup
- `POST /catalog/forms/view/save` requires validation first.
- Calls `save_config_text_safely()` which creates backup, atomic save, reload verification.
- Saved file contains the form-generated YAML (exact proposed text, not a regeneration).

**Test**: POST valid form save, verify backup file exists, saved file text matches proposed, reloaded config validates.

### M7: sql_file reference preserved
- Form shows `sql_file` section when `sql_file` is set (mutually exclusive with `sql`).
- Saving the form-generated YAML preserves `sql_file: {path: "foo.sql"}` literally.
- After save, reload shows `sql_file` still present, not converted to inline `sql`.

**Test**: Write config with `sql_file: {path: "foo.sql"}`, save via form, verify saved text contains literal `sql_file:`.

### M8: DuckDB settings structured form
- `GET /catalog/forms/duckdb` renders DuckDB settings form from `config.duckdb`.
- Fields: `database`, `install_extensions`, `load_extensions`, `pragmas`, `settings`.
- POST to validate, preview, and save follows the same safety-service pattern.

**Test**: Change database path, POST save, verify backup created, reloaded config has new path.

### M9: Remote path rejection
- Attempting to edit a remote config (e.g., `s3://bucket/catalog.yaml`) via a form returns a read-only error.
- The safety service's `is_remote_uri()` check is the enforcement point.

**Test**: Call `load_editable_config("s3://bucket/catalog.yaml")` → expect error result, no write.

### M10: Full regression
- `tests/test_studio.py` (foundation) passes.
- `tests/test_studio_editing.py` (editing safety) passes.
- `tests/test_dashboard.py` (old UI) passes.
- `starhtml-check` on changed `app.py`, `components.py`, and new form modules.

## Open Questions

1. **YAML serialization for form output**: The form generates proposed YAML from a `Config` object. Should it use `yaml.dump()` (loses comments, normalizes formatting) or a comment-preserving round-trip library? The editing safety plan deliberately deferred round-trip YAML. This plan should use the simplest serialization that produces valid YAML and let the safety service save that text as-is.

2. **What fields for the first form editor**: `ViewConfig` has ~15 fields; `DuckDBConfig` has ~7 fields. Should the first form editor cover all fields or just a minimal subset (name, source type, SQL source, description)? A minimal first cut reduces scope and risk.

3. **How to generate YAML from form values**: After the user edits form fields, the form must reconstruct a `Config` object and dump it as YAML. This requires a serialization step that is the inverse of `load_config()`. Is there an existing serialization helper, or does this plan need to create one? The `Config.model_dump()` route loses comment/formatting but is the simplest approach for a first cut.

4. **Mutually exclusive SQL source UI**: `sql`, `sql_file`, and `sql_template` are mutually exclusive. The form UI must show exactly one section at a time based on which field is populated. Does StarHTML support conditional rendering of form sections via signals?

5. **Adding/removing views**: Should the first form editor support adding new views or only editing existing ones? Adding views requires reconstructing the full config's `views` list and generating YAML for all views, not just one.

6. **StarHTML signal persistence**: If the user navigates away and back to the form, does signal state persist? The form editor should reload from the disk config on each page load, not from client-side state.

7. **stale-save protection**: Should the form editor include a checksum/staleness check (like the expert editor plan specifies)? If the file changed on disk since the editor loaded, should saves be rejected?

8. **What comes after View + DuckDB forms**: Semantic models, attachments, secrets, iceberg catalogs, and imports are all future form targets. Should this plan define a reusable form generation pattern that applies to all config sections, or focus only on views and DuckDB settings?
