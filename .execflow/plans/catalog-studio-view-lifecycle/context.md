# Code Context — catalog-studio-view-lifecycle

## Files Retrieved

### Core config model (canonical schema gate)

1. `src/duckalog/config/models.py` (lines 300-460) — `ViewConfig` fields and constraints.
   Key fields: `name`, `db_schema`, `sql`/`sql_file`/`sql_template` (mutually exclusive), `source` (`EnvSource`), `uri`, `database`, `table`, `catalog`, `options`, `description`, `tags`.
   Critical validator at line 385+: `_validate_definition()` enforces at most one SQL source, and requires either a SQL source or a data source. Source-specific fields are validated per source type.

2. `src/duckalog/config/models.py` (lines 540-700) — `SemanticModelConfig` fields.
   Key fields: `name`, `base_view` (must reference existing view), `dimensions`, `measures`, `joins` (list of `SemanticJoinConfig`), `defaults`.
   `SemanticJoinConfig.to_view` at line 625+ validates non-empty string referencing another view.

3. `src/duckalog/config/models.py` (lines 770-820) — `Config` top-level uniqueness validator.
   At line 920+, `_validate_uniqueness()` checks for duplicate view names `(db_schema, name)`. At line 1019+, it validates semantic model base views and join view references exist. At line 1076+, it validates that `to_view` in joins references existing views.

4. `src/duckalog/config/models.py` (lines 300-350) — `SQLFileReference` fields: `path`, `variables`, `as_template`.

5. `src/duckalog/config/models.py` (lines 130-180) — `DuckDBConfig` fields: `database`, `install_extensions`, `load_extensions`, `pragmas`, `settings`, `secrets`.

### Config loading and SQL file processing

6. `src/duckalog/config/api.py` (lines 1-80) — `load_config()` with `load_sql_files: bool = True`. Pass `False` for editing reload to avoid SQL file inlining side effects. `load_config()` is the canonical reload verification function.

7. `src/duckalog/config/loading/sql.py` (lines 1-160) — `process_sql_file_references()` at line 35+. This is the critical function that **replaces `sql_file`/`sql_template` with inline `sql`**. It does `view.model_copy(update={"sql": sql_content, "sql_file": None})`. This is why generating proposed text must preserve raw `sql_file`/`sql_template` references — serializing a loaded `Config` object would destroy them.

8. `src/duckalog/config/resolution/imports.py` (lines 1-120) — `RequestContext`, `request_cache_scope()`, and import resolution. `_load_config_with_imports()` resolves imports before passing to `Config.model_validate()`.

### Config validation and validation result types

9. `src/duckalog/config/validators.py` (lines 1-100) — `_validate_uniqueness()` for views and semantic models. Also contains `PathResolutionError` and `ConfigError` from `duckalog.errors`.

10. `src/duckalog/errors.py` — `ConfigError`, `DuplicateNameError`, `PathResolutionError` exception types.

### Predecessor ExecPlans

11. `.execflow/plans/catalog-studio-form-editor/execplan.md` (lines 1-300) — The immediate predecessor. Key decisions:
    - Decision: Defer add/delete views in the first form editor.
    - Decision: Generate proposed raw text from the whole root config (not partial writes).
    - Decision: Preserve `sql_file`/`sql_template` references by working from raw draft text.
    - Decision: Do not add a round-trip YAML dependency.
    - Helper function names: `build_proposed_view_config_text(draft, original_name, values)`, `build_proposed_duckdb_config_text(draft, values)`.
    - This plan **defers** add/delete to the next ExecPlan.

12. `.execflow/plans/catalog-studio-editing-safety/execplan.md` (lines 1-300) — The safety service that both form-editor and expert-editor use.
    - Functions: `load_editable_config(path)`, `validate_config_text(text, format, base_path)`, `preview_config_diff(original_text, proposed_text, path)`, `save_config_text_safely(path, proposed_text)`.
    - Constraint: local-only writes, raw-text preservation (NOT `Config.model_dump()`), `difflib.unified_diff()`, atomic save via `os.replace()`, backup via `shutil.copy2()`.

13. `.execflow/plans/catalog-studio-form-editor/context.md` (lines 1-200) — Scout context from form-editor planning. Includes the **independently verifiable milestones M1-M10** and form signal naming conventions.

### Tests for config validation

14. `tests/test_config.py` (lines 870-1070) — Tests for semantic model validation:
    - `test_semantic_models_missing_base_view_rejected` (line 908): asserts `"reference undefined base view"` error.
    - `test_semantic_models_duplicate_names_rejected` (line 887): duplicate semantic model names rejected.
    - `test_semantic_models_v2_join_to_nonexistent_view_rejected` (line 1439): join `to_view` to nonexistent view rejected.
    - `test_semantic_model_with_ambiguous_view_reference` (line 2089): ambiguous view references rejected.
    - `test_semantic_model_with_schema_qualified_base_view` (line 2062): schema-qualified base view resolved correctly.
    - Lines 215-260: duplicate view names across imports rejected.

15. `tests/test_config.py` (lines 87-105) — `test_duplicate_view_names_rejected`: duplicate view names within the same config rejected with message `"Duplicate view name"`.

16. `tests/test_config_imports.py` (lines 215-260) — `test_duplicate_view_names_across_imports`: duplicate names across imported files rejected.

### Config template and YAML serialization

17. `src/duckalog/config_init.py` (lines 140-195) — `_format_as_yaml()` uses `yaml.dump()` (loses comments), `_write_config_file()` uses `Path.write_text()` (no atomicity, no backup). These are the unsafe patterns that the editing safety service replaces. These are the only existing YAML serialization patterns — there is no comment-preserving round-trip serializer.

### Dashboard and SQL generation for reference

18. `src/duckalog/dashboard/routes/views.py` (lines 1-100) — Dashboard views listing page. Shows view names as links to view detail pages. For reference when adding view list navigation in the Studio.

19. `src/duckalog/sql_generation.py` (lines 1-120) — `generate_view_sql(view)` produces `CREATE OR REPLACE VIEW` SQL. `_render_view_body()` handles source-specific SQL generation. For understanding how view definitions are rendered at SQL-build time.

### Config security and path validation

20. `src/duckalog/config/security/path.py` (lines 1-100) — `validate_path_security()`, `is_within_allowed_roots()`, `is_remote_uri()`. Reused by the editing safety service for local-path safety checks.

## Key Code

### ViewConfig field constraints (mutually exclusive SQL sources)

```python
# src/duckalog/config/models.py:ViewConfig._validate_definition() (lines 385-425)
has_sql = bool(self.sql and self.sql.strip())
has_sql_file = self.sql_file is not None
has_sql_template = self.sql_template is not None
sql_sources = sum([has_sql, has_sql_file, has_sql_template])

# Must have either SQL content or a data source
if sql_sources == 0 and not has_source:
    raise ValueError("View must define either SQL content or a data source")

# Cannot have multiple SQL sources
if sql_sources > 1:
    raise ValueError("View cannot have multiple SQL sources...")

# Data source field requirements:
# parquet/delta: uri required
# iceberg: uri XOR (catalog + table)
# duckdb/sqlite/postgres: database AND table required
```

### Config uniqueness validator (view uniqueness, semantic model references)

```python
# src/duckalog/config/models.py:Config._validate_uniqueness() (lines 920-1115)
# 1. Duplicate view names (schema-qualified)
seen: dict[tuple[Optional[str], str], int] = {}
for index, view in enumerate(self.views):
    key = (view.db_schema, view.name)
    if key in seen:  # ERROR: duplicate
    else: seen[key] = index

# 2. Semantic model base_view existence (with ambiguity detection)
def resolve_view_reference(reference: str) -> tuple[Optional[str], str]:
    if "." in reference:
        parts = reference.split(".", 1)
        return (parts[0], parts[1])  # (schema, name)
    return (None, reference)          # (None, name)

# Check exact schema-qualified match first, then name-only (fail if ambiguous)

# 3. Semantic model join to_view existence (same resolution pattern)
for semantic_model in self.semantic_models:
    for join in semantic_model.joins:
        # resolve_view_reference(join.to_view) — must resolve to existing view
```

### SQL file inlining (what destroys sql_file references on normal load)

```python
# src/duckalog/config/loading/sql.py:process_sql_file_references() (lines 35-120)
if view.sql_file is not None:
    sql_content = sql_file_loader.load_sql_file(...)
    updated_view = view.model_copy(
        update={"sql": sql_content, "sql_file": None}  # <-- sql_file is set to None!
    )
    return updated_view, True
```

### Form editor helper contract (from predecessor execplan)

```python
# src/duckalog/studio/form_editing.py  (to be created)
# Pure Python, no StarHTML imports

build_proposed_view_config_text(draft, original_name, values) -> str
# - Takes current raw editable config text
# - Parses it into a plain dict (NOT Config.model_validate() on the whole thing)
# - Modifies only the targeted view section
# - Serializes the proposed root config back to the same format as the original
# - For YAML: yaml.safe_dump(..., sort_keys=False)
# - For JSON: json.dumps(..., indent=2)
# - Calls validate_config_text() to ensure output is valid

build_proposed_duckdb_config_text(draft, values) -> str
# - Same pattern for DuckDB settings section

# Form values dict shape:
values = {
    'name': str,
    'db_schema': str | None,
    'description': str | None,
    'tags': list[str],
    'definition_kind': 'inline_sql' | 'sql_file' | 'sql_template' | 'source',
    'sql': str | None,
    'sql_file_path': str | None,
    'sql_template_path': str | None,
    'source': str | None,  # 'parquet'|'delta'|'iceberg'|'duckdb'|'sqlite'|'postgres'
    'uri': str | None,
    'database': str | None,
    'table': str | None,
    'catalog': str | None,
    'options': dict[str, Any],
}
```

### SemanticModelConfig.base_view and joins.to_view fields

```python
# src/duckalog/config/models.py:SemanticModelConfig (lines 540-570)
class SemanticModelConfig(BaseModel):
    name: str
    base_view: str  # Must reference an existing view in the views section
    joins: list[SemanticJoinConfig] = Field(default_factory=list)
    ...

# src/duckalog/config/models.py:SemanticJoinConfig (lines 615-625)
class SemanticJoinConfig(BaseModel):
    to_view: str  # Must reference an existing view in the views section
    type: str  # 'inner'|'left'|'right'|'full'
    on_condition: str
```

## Architecture

```
catalog-studio-view-lifecycle builds on catalog-studio-form-editor

src/duckalog/studio/form_editing.py  (from predecessor)
  → build_proposed_view_config_text()     # edit existing views
  → build_proposed_duckdb_config_text()

src/duckalog/studio/view_lifecycle.py  (NEW — this plan)
  → build_proposed_add_view_text()         # add new view to config
  → build_proposed_delete_view_text()       # remove view from config
  → build_proposed_duplicate_view_text()   # duplicate view with new name
  → build_proposed_rename_view_text()      # rename view (cross-checks semantic models)

All lifecycle helpers:
  1. Parse current raw config text into dict (preserve sql_file refs)
  2. Modify targeted view(s) in the dict
  3. Check affected references BEFORE generating proposed text
  4. Serialize to YAML/JSON matching original format
  5. Call validate_config_text() from editing safety service
  6. Return proposed raw text string (never Config.model_dump())

src/duckalog/studio/app.py  (StarHTML routes, extended)
  → /catalog/views              GET   (list with add/delete/duplicate buttons)
  → /catalog/views/add          GET   (new view form)
  → /catalog/views/{name}/delete GET   (delete confirmation)
  → /catalog/views/{name}/duplicate GET (duplicate form)
  → /catalog/forms/view/{name}  GET   (existing — edit form, from predecessor)
  → /catalog/forms/view/save    POST  (existing — from predecessor)

Editing safety service (shared):
  → load_editable_config()       (from predecessor)
  → validate_config_text()       (from predecessor)
  → preview_config_diff()        (from predecessor)
  → save_config_text_safely()    (from predecessor)
```

### Dependency chain for view lifecycle operations

```
ADD VIEW:
  1. generate_proposed_add_view_text(draft, view_values) → proposed_text
  2. validate_config_text(proposed_text) → check uniqueness (new name not duplicate)
  3. save_config_text_safely(path, proposed_text)
  Risk: None (new view doesn't break existing references)

DELETE VIEW:
  1. generate_proposed_delete_view_text(draft, view_name) → proposed_text
  2. validate_config_text(proposed_text) → MUST FAIL if semantic model references this view
  3. If validation fails, surface error: "Cannot delete view X: referenced by semantic model Y.base_view and Z.joins[0].to_view"
  4. If validation passes, save_config_text_safely()
  Risk: HIGH — deleting a view breaks semantic model base_view and join to_view references

DUPLICATE VIEW:
  1. validate new name uniqueness (not duplicate)
  2. generate_proposed_duplicate_view_text(draft, source_name, new_name) → proposed_text
  3. validate_config_text(proposed_text)
  4. save_config_text_safely()
  Risk: LOW — duplicates are independent

RENAME VIEW:
  1. validate new name uniqueness
  2. find all semantic models that reference the old name (base_view or join.to_view)
  3. generate_proposed_rename_view_text() with all affected semantic model refs updated
  4. validate_config_text(proposed_text)
  5. save_config_text_safely()
  Risk: MEDIUM — must update semantic model references atomically with the view rename
```

## Start Here

1. **Open `src/duckalog/config/models.py`** lines 920-1115. This is the `_validate_uniqueness()` validator that implements the reference-checking logic. Study the `resolve_view_reference()` helper and the three validation blocks (view uniqueness, base_view existence, join to_view existence). These are the same checks the lifecycle helper must invoke before generating proposed text for delete/rename operations.

2. **Open `src/duckalog/config/loading/sql.py`** lines 35-120. This is the function that inlines SQL files and would destroy `sql_file` references. The lifecycle helper must parse raw YAML/JSON text (via `yaml.safe_load()` or `json.loads()`) and re-emit it without going through `load_config()`, which calls this function.

3. **Open `.execflow/plans/catalog-studio-form-editor/execplan.md`** lines 60-120 (Decision Log and Plan of Work sections). This establishes the core pattern: work from raw draft text, generate proposed raw text from modified dict, call safety service for validation/save.

4. **Open `tests/test_config.py`** lines 908 and 1439. These are the canonical regression tests for view reference validation. The lifecycle helper's pre-flight checks must trigger the same validation errors.

## Independently Verifiable Milestones

### M1: Add view validation — duplicate name rejected
Create a config with a view named "demo". POST to add a view also named "demo". Expect validation error: `"Duplicate view name"`.

**Test**: Write YAML with `views: [{name: demo, sql: "SELECT 1"}]`, attempt to add another `demo`, assert validation rejects.

### M2: Add view validation — sql/sql_file/sql_template mutual exclusivity
Add a view with both `sql` and `sql_file` fields set. Expect validation error: `"View cannot have multiple SQL sources"`.

**Test**: Attempt to add a view with conflicting SQL source fields, assert validation rejects.

### M3: Delete view — semantic model base_view reference blocks deletion
Config has view "source_view" and semantic model with `base_view: source_view`. Attempt to delete "source_view". Expect validation error: `"reference undefined base view: broken_model -> source_view"`.

**Test**: Write config with view + semantic model referencing it, attempt to delete view, assert validation blocks deletion.

### M4: Delete view — semantic model join to_view reference blocks deletion
Config has views "a" and "b", semantic model with `joins: [{to_view: b}]`. Attempt to delete view "b". Expect validation error: `"reference undefined view(s): model.b"`.

**Test**: Write config with view + semantic model with join referencing it, attempt to delete, assert validation blocks.

### M5: Delete view — no semantic model dependency allows deletion
Config has view "solo_view" with no semantic model references. Delete succeeds. Saved file no longer contains `solo_view`.

**Test**: Write config with orphan view, delete it, assert file updated, backup created, reload succeeds.

### M6: Duplicate view — new name uniqueness validated
Config has view "demo". Duplicate with name "demo". Expect validation error: `"Duplicate view name(s) found: demo"`.

**Test**: Write config with view "demo", duplicate as "demo", assert validation rejects.

### M7: Duplicate view — new name uniqueness validated
Config has view "demo". Duplicate with name "new_demo". Expect validation succeeds, saved file contains both views.

**Test**: Write config with view "demo", duplicate as "new_demo", save, assert both views exist in saved file.

### M8: Rename view — semantic model base_view updated atomically
Config has view "old_name" and semantic model with `base_view: old_name`. Rename to "new_name". Saved file has view "new_name" and semantic model's `base_view` updated to "new_name".

**Test**: Write config with view + semantic model, rename view, save, assert view renamed and semantic model base_view updated in same save.

### M9: Rename view — semantic model join to_view updated atomically
Config has view "old_name" and semantic model with join `to_view: old_name`. Rename to "new_name". Saved file has view "new_name" and join `to_view` updated to "new_name".

**Test**: Write config with view + semantic model with join, rename view, save, assert view renamed and join to_view updated in same save.

### M10: Rename view — ambiguous reference causes rejection
Config has views with same name in different schemas (`analytics.v1`, `default.v1`). Semantic model references `v1` unqualified. Rename `analytics.v1` to `v2`. Expect validation error: `"ambiguous base view reference"`.

**Test**: Write config with same-name views in different schemas, semantic model with unqualified reference, rename one, assert validation rejects with ambiguity message.

### M11: Form helper produces proposed text from raw draft
Call `build_proposed_delete_view_text()` on raw draft text containing 3 views, requesting deletion of view 2. Verify proposed text contains views 1 and 3 only, and the helper never calls `load_config()` or `Config.model_dump()`.

**Test**: Write 3-view config to temp file, call helper, assert proposed text has 2 views, `sql_file` references in other views unchanged.

### M12: Form helper preserves sql_file references
Config has view with `sql_file: {path: query.sql}` and another with `sql: "SELECT 1"`. Delete the `sql`-only view. Saved file still contains `sql_file: {path: query.sql}` for the other view.

**Test**: Write config with sql_file view + sql view, delete sql view, assert saved file preserves sql_file reference exactly.

### M13: Backup created on lifecycle save
Add, delete, or rename a view via the form. Verify backup file created with timestamp. Saved file matches proposed text. Reload succeeds.

**Test**: Lifecycle save, assert backup exists, backup contains original text, saved file contains proposed text, reload validates.

### M14: Full regression
- `tests/test_studio_form_editor.py` (predecessor) passes.
- `tests/test_studio_editing.py` (editing safety) passes.
- `tests/test_dashboard.py` (old UI) passes.
- `starhtml-check` on changed `app.py`, `components.py`, and new lifecycle modules.

## Risks

### R1: Deleting a view referenced by semantic models (HIGH)
If a user deletes a view that a semantic model's `base_view` or `joins[].to_view` references, the config becomes invalid. The current `_validate_uniqueness()` in `Config` checks for missing base views and join view references. The lifecycle helper MUST run this same validation before generating proposed delete text, and MUST surface these errors to the user before any save is attempted. The editing safety service's `validate_config_text()` should catch this if the proposed text is validated, but the UX should surface it early.

**Mitigation**: Pre-flight check via `Config.model_validate()` on the proposed delete text. Surface specific error: "Cannot delete view 'X': referenced by semantic model 'Y' (base_view) and 'Z' (join). Update or remove these references first."

### R2: Renaming a view without updating semantic model references (HIGH)
If a user renames view "A" to "B" without updating a semantic model's `base_view: A` or `joins[].to_view: A`, the config becomes invalid post-save. The rename operation must atomically update both the view name and all referring semantic model references.

**Mitigation**: The rename helper must find all semantic models referencing the old name (using `resolve_view_reference()` pattern), include those updates in the proposed text, and validate the complete proposed text before saving.

### R3: SQL file references destroyed by Config.model_dump() (HIGH)
`load_config()` calls `process_sql_file_references()` which replaces `sql_file`/`sql_template` with inline `sql`. A lifecycle helper that calls `load_config()` then tries to save would destroy these references.

**Mitigation**: All lifecycle helpers must work from `yaml.safe_load()` / `json.loads()` on the raw draft text, NOT from `Config.model_dump()` or a loaded `Config` object. Serialization back to YAML must use `yaml.safe_dump(..., sort_keys=False)` or `json.dumps(..., indent=2)`.

### R4: Adding duplicate view names (MEDIUM)
Adding a view with a name matching an existing view (same schema) should be rejected at validation time, not at save time. The `_validate_uniqueness()` in `Config` catches this.

**Mitigation**: `validate_config_text()` on the proposed add text triggers `Config.model_validate()`, which rejects duplicates.

### R5: Ambiguous view references on rename (MEDIUM)
If the config has two views with the same name in different schemas, and a semantic model references the name unqualified, a rename of one of them could create ambiguity or break the semantic model.

**Mitigation**: Detect ambiguous references before rename and surface an error requiring schema-qualified references to be used first.

### R6: No existing studio package yet (MEDIUM)
The `src/duckalog/studio/` package does not exist yet (predecessor plan not implemented). The form editor execplan assumes `src/duckalog/studio/editing.py` and `src/duckalog/studio/form_editing.py` exist, but these have not been created yet.

**Mitigation**: This plan builds on catalog-studio-form-editor which creates the `studio/` package. This plan should only start after form-editor is implemented.

## Open Questions

1. **Add/delete via partial text or full config rebuild?** Should the lifecycle helper operate on the whole config text (consistent with form-editor pattern) or on a targeted diff of just the views list? Full config rebuild is consistent with the predecessor but may normalize unrelated sections.

2. **Should add view be a separate route or a blank form at the same route as edit?** Adding a view could be `GET /catalog/views/add` (new view form) or `GET /catalog/forms/view/new` (blank form with add-mode flag). The predecessor execplan's Decision Log says "Defer adding new views and deleting views in this first form editor," so this plan must decide the UX pattern.

3. **Should duplicate name collision UX show existing name suggestions?** If the user tries to duplicate "demo" as "demo", should the form suggest "demo_copy" or "demo_2" as available alternatives before attempting save?

4. **Should the form helper check semantic model impacts BEFORE generating proposed text?** For delete/rename, it's better to fail early with a dependency report than to generate proposed text that will fail validation. Should there be a separate pre-flight check step?

5. **Should delete require explicit confirmation (GET confirmation page vs. POST directly)?** The editing safety service guards saves, but a delete confirmation page lets users see what will break before attempting the save.

6. **Should view ordering be preserved on add/delete/duplicate?** The YAML list ordering of views affects SQL generation order (`generate_all_views_sql()` iterates in order). Should the lifecycle helper preserve original ordering and insert new views at a specific position (end, or after the source view for duplicates)?

7. **Should the plan cover Iceberg catalog view references?** Views can reference Iceberg catalogs (`view.catalog`). Deleting an `IcebergCatalogConfig` would break views referencing it. Is this in scope for this plan or a separate concern?

8. **What is the safe pattern for generating proposed text?** The predecessor plan deliberately avoided defining the serialization approach in detail. Should proposed text use `yaml.safe_dump()` (lossy but simple) or a comment-preserving round-trip library (complex but preserving)? The predecessor decision was "simplest serialization that produces valid YAML."
