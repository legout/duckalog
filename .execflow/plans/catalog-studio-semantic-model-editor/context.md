# Code Context — catalog-studio-semantic-model-editor

## Files Retrieved

### Semantic model config models (primary source of truth)

1. `src/duckalog/config/models.py` (lines 490-820) — All `Semantic*Config` Pydantic models and `Config`-level cross-reference validation. The canonical field definitions for the semantic model editor.

2. `src/duckalog/config/__init__.py` (lines 50-125) — Re-exports of all semantic model types. The public API surface.

3. `src/duckalog/__init__.py` (lines 14-18, 92-96) — Top-level re-exports.

### Config-level whole-model validation

3. `src/duckalog/config/models.py` (lines 1029-1112) — `Config._validate_uniqueness()` model validator. Validates:
   - Semantic model name uniqueness (lines 969–980)
   - Semantic model `base_view` resolves to an existing view (lines 1033–1070)
   - Semantic model `joins[].to_view` resolves to an existing view (lines 1076–1111)

### Semantic model field validators (individual config classes)

4. `src/duckalog/config/models.py` (lines 490–575) — `SemanticDimensionConfig` field validators:
   - `_validate_name`: strips, rejects empty
   - `_validate_expression`: strips, rejects empty
   - `_validate_type`: must be `time`, `number`, `string`, `boolean`, `date` (case-normalized)
   - `_validate_time_grains`: only allowed for `type == "time"`; valid grains: `year`, `quarter`, `month`, `week`, `day`, `hour`, `minute`, `second`

5. `src/duckalog/config/models.py` (lines 577–612) — `SemanticMeasureConfig` field validators:
   - `_validate_name`: strips, rejects empty
   - `_validate_expression`: strips, rejects empty

6. `src/duckalog/config/models.py` (lines 614–658) — `SemanticJoinConfig` field validators:
   - `_validate_to_view`: strips, rejects empty
   - `_validate_type`: must be `inner`, `left`, `right`, `full` (case-normalized)
   - `_validate_on_condition`: strips, rejects empty

7. `src/duckalog/config/models.py` (lines 660–695) — `SemanticDefaultsConfig` field validators:
   - `_validate_time_dimension`: strips, allows empty/None (not validated here; `SemanticModelConfig` checks it references a real dimension)
   - `_validate_primary_measure`: same pattern

### Semantic model intra-model validation

8. `src/duckalog/config/models.py` (lines 743–820) — `SemanticModelConfig._validate_uniqueness()` model validator:
   - Dimension name uniqueness
   - Measure name uniqueness
   - No name conflicts between dimensions and measures
   - `defaults.time_dimension` must reference a defined dimension of type `time`
   - `defaults.primary_measure` must reference a defined measure
   - `defaults.default_filters[].dimension` must reference a defined dimension

### Semantic model tests (ground truth for expected behavior)

9. `tests/test_config.py` (lines 741–1637) — Comprehensive test suite for semantic model loading and validation. Key tests:
   - `test_semantic_models_basic_config` (line 741): full semantic model with dimensions and measures
   - `test_semantic_models_minimal_config` (line 817): minimal model, all optionals absent
   - `test_semantic_models_empty_list` (line 846): empty `semantic_models: []`
   - `test_semantic_models_duplicate_names_rejected` (line 881): duplicate model names caught
   - `test_semantic_models_missing_base_view_rejected` (line 908): `base_view` must exist
   - `test_semantic_models_duplicate_dimension_names_rejected` (line 931)
   - `test_semantic_models_duplicate_measure_names_rejected` (line 959)
   - `test_semantic_models_dimension_measure_name_conflict_rejected` (line 987)
   - `test_semantic_models_empty_*_rejected` (lines 1016, 1038, 1060, 1072, 1085, 1097, 1110, 1122): all empty-name and empty-expression rejections
   - `test_semantic_models_python_api_access` (line 1188): programmatic access to semantic models
   - `test_semantic_models_v2_with_joins_and_time_dimensions` (line 1199): v2 with joins, time_grains, defaults
   - `test_semantic_models_v2_invalid_join_type_rejected` (line 1307)
   - `test_semantic_models_v2_time_grains_only_for_time_dimensions` (line 1339)
   - `test_semantic_models_v2_invalid_time_grain_rejected` (line 1363)
   - `test_semantic_models_v2_invalid_dimension_type_rejected` (line 1387)
   - `test_semantic_models_with_env_interpolation` (line 1461): `${env:VAR}` in `base_view`
   - `test_semantic_models_missing_base_view_with_schema_rejected` (line 1478): ambiguous `base_view` with same-name views in different schemas
   - `test_semantic_models_with_schema_qualified_base_view` (line 2062)
   - `test_semantic_models_ambiguous_base_view_across_schemas_rejected` (line 2076)

10. `tests/test_config_imports.py` (lines 135, 175, 278, 297, 680, 686, 709, 713, 951, 997) — Semantic model behavior under config imports.

### Spec (semantic layer design document)

11. `openspec/specs/semantic-layer/spec.md` (full file) — `SemanticModelConfig`, `SemanticDimensionConfig`, `SemanticMeasureConfig`, `SemanticJoinConfig`, `SemanticDefaultsConfig` definitions, validation rules, v2 extensions, example YAML configs.

### Config loading pipeline (how raw text becomes Config)

12. `src/duckalog/config/loading/sql.py` (lines 1–120) — `process_sql_file_references()` inlines `sql_file` into `sql`. **Critical**: helpers must NOT go through `load_config()` because that would convert `sql_file` → `sql` in other sections during semantic model edits.

13. `src/duckalog/config/resolution/imports.py` (lines 475–650) — `_load_config_with_imports()` parses YAML via `yaml.safe_load()` and JSON via `json.loads()`. This is the function the editing safety service should call (with `load_sql_files=False`) for reload verification.

14. `src/duckalog/config/api.py` (lines 1–80) — `load_config()` function signature and documentation.

### Predecessor ExecPlans (editing safety service, attachments/secrets editor, form editor)

15. `.execflow/plans/catalog-studio-editing-safety/execplan.md` (lines 1–300) — The safety service contract:
    - `load_editable_config(path)` → draft dict with `path`, `format`, `text`, `validated_config`
    - `validate_config_text(text, format, base_path)` → `{ok, errors, parsed_config}`
    - `preview_config_diff(original_text, proposed_text, path)` → `{text, stats}`
    - `save_config_text_safely(path, proposed_text)` → `{ok, backup_path, reload_status, errors}`
    - **Critical**: writes only via `save_config_text_safely()`; no direct `Path.write_text()` in routes/helpers

16. `.execflow/plans/catalog-studio-form-editor/execplan.md` (lines 1–430) — Form-to-proposed-text pattern:
    - Work from `yaml.safe_load()` / `json.loads()` on raw draft text, NOT from `Config.model_dump()`
    - Generate proposed text by modifying parsed dict, serialize with `yaml.safe_dump(sort_keys=False)` or `json.dumps(indent=2)`
    - Call `validate_config_text()` on proposed text, pass to `save_config_text_safely()` on save
    - `definition_kind` control for mutually exclusive SQL sources on views (same principle applies to semantic model structure)
    - Existing module names: `form_editing.py`, `editing.py` in `src/duckalog/studio/`
    - Route conventions: `GET /catalog/forms/view/{name}`, `POST /catalog/forms/view/validate|preview|save`

17. `.execflow/plans/catalog-studio-attachments-secrets-editor/execplan.md` (lines 1–200) — Same pattern applied to attachments and secrets. Key additions:
    - Redacted diff preview for secret fields
    - Placeholder preservation for sensitive values (show `********`, keep original unless replaced)
    - Provider-specific validation for secrets
    - Attachment identity is `(type, alias)`; must validate cross-type alias uniqueness

18. `.execflow/plans/catalog-studio-attachments-secrets-editor/context.md` (lines 1–400) — Scout context for attachments/secrets; patterns that apply to semantic models include redaction approach, dict-mutation helpers, and safety-service integration.

### Editing safety service context (already scouted)

19. `.execflow/plans/catalog-studio-form-editor/context.md` (lines 1–400) — Scout context for form editor, includes editing safety service details, route conventions, signal patterns, and `Config` field reference. Relevant for understanding helper signatures and StarHTML signal conventions.

## Key Code

### SemanticDimensionConfig (lines 490–575)

```python
class SemanticDimensionConfig(BaseModel):
    name: str
    expression: str
    label: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None  # time, number, string, boolean, date
    time_grains: list[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")

    @field_validator("name")          # strips, rejects empty
    @field_validator("expression")    # strips, rejects empty
    @field_validator("type")          # case-normalized, valid set check
    @field_validator("time_grains")  # only if type=="time", valid grain set
```

### SemanticMeasureConfig (lines 577–612)

```python
class SemanticMeasureConfig(BaseModel):
    name: str
    expression: str
    label: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None

    @field_validator("name")
    @field_validator("expression")
```

### SemanticJoinConfig (lines 614–658)

```python
class SemanticJoinConfig(BaseModel):
    to_view: str       # must resolve to existing view name (qualified or unqualified)
    type: str          # inner, left, right, full (case-normalized)
    on_condition: str  # SQL join condition

    @field_validator("to_view")
    @field_validator("type")
    @field_validator("on_condition")
```

### SemanticDefaultsConfig (lines 660–695)

```python
class SemanticDefaultsConfig(BaseModel):
    time_dimension: Optional[str] = None      # refs dimension name, must have type="time"
    primary_measure: Optional[str] = None     # refs measure name
    default_filters: list[dict[str, Any]] = Field(default_factory=list)
                                               # each dict has "dimension" key

    @field_validator("time_dimension")
    @field_validator("primary_measure")
```

### SemanticModelConfig (lines 696–820)

```python
class SemanticModelConfig(BaseModel):
    name: str
    base_view: str                                    # must resolve to existing view
    dimensions: list[SemanticDimensionConfig] = Field(default_factory=list)
    measures: list[SemanticMeasureConfig] = Field(default_factory=list)
    joins: list[SemanticJoinConfig] = Field(default_factory=list)
    defaults: Optional[SemanticDefaultsConfig] = None
    label: Optional[str] = None
    description: Optional[str] = None
    tags: list[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")

    @field_validator("name")
    @field_validator("base_view")     # strips, rejects empty
    @model_validator(mode="after")
    def _validate_uniqueness(self) -> "SemanticModelConfig":
        # - dimension name uniqueness
        # - measure name uniqueness
        # - no dim/measure name conflict
        # - defaults.time_dimension refs existing time-type dimension
        # - defaults.primary_measure refs existing measure
        # - defaults.default_filters[*].dimension refs existing dimension
```

### Config._validate_uniqueness() cross-reference validation (lines 1029–1112)

```python
# Resolve view references
def resolve_view_reference(reference: str) -> tuple[Optional[str], str]:
    if "." in reference:
        parts = reference.split(".", 1)
        return (parts[0], parts[1])
    return (None, reference)

view_by_name: dict[str, ViewConfig] = {view.name: view for view in self.views}
view_by_schema_name: dict[tuple[Optional[str], str], ViewConfig] = {...}

# base_view must exist (uniquely if schema-qualified)
# joins[].to_view must exist (uniquely if schema-qualified)
# Ambiguous unqualified references → clear error telling user to qualify
```

### Editing safety service signatures (from predecessor)

```python
# From .execflow/plans/catalog-studio-editing-safety/execplan.md
# src/duckalog/studio/editing.py  (assumed implemented by predecessor)

@dataclass
class EditableConfig:
    path: Path
    format: str  # "yaml" or "json"
    text: str    # raw file content
    validated_config: Config

def load_editable_config(path: Path) -> EditableConfig:
    """Read raw text, validate full config, return draft."""

@dataclass
class ValidationResult:
    ok: bool
    errors: list[str]
    parsed_config: Optional[Config] = None

def validate_config_text(text: str, format: str, base_path: Path) -> ValidationResult:
    """Parse text, run Config.model_validate(), return structured result."""

@dataclass
class DiffResult:
    text: str   # unified diff
    stats: dict[str, int]  # added, removed, changed line counts

def preview_config_diff(original_text: str, proposed_text: str, path: Path) -> DiffResult:
    """Generate unified diff between original and proposed raw text."""

@dataclass
class SaveResult:
    ok: bool
    backup_path: Optional[Path] = None
    reload_status: str = ""
    errors: list[str] = field(default_factory=list)

def save_config_text_safely(path: Path, proposed_text: str) -> SaveResult:
    """Backup, atomic replace, reload verification. Only write path."""
```

### Form editor helper pattern (from predecessor)

```python
# From .execflow/plans/catalog-studio-form-editor/execplan.md
# src/duckalog/studio/form_editing.py  (assumed implemented by predecessor)

def build_proposed_view_config_text(
    draft: EditableConfig,
    original_name: str,
    values: dict[str, Any],
) -> str:
    """Parse raw YAML/JSON, modify view section, serialize back."""
    # 1. yaml.safe_load(draft.text) or json.loads(draft.text)
    # 2. Find view by original_name in config["views"]
    # 3. Update only changed fields in the view dict
    # 4. yaml.safe_dump(..., sort_keys=False) or json.dumps(..., indent=2)
    # Returns proposed raw text string
```

## Architecture

```
src/duckalog/studio/editing.py        (predecessor: safety service)
  load_editable_config() → EditableConfig
  validate_config_text() → ValidationResult
  preview_config_diff() → DiffResult
  save_config_text_safely() → SaveResult

src/duckalog/studio/form_editing.py   (predecessor: form helpers)
  build_proposed_view_config_text() → str
  build_proposed_duckdb_config_text() → str

src/duckalog/studio/attachment_editing.py  (predecessor: attachment helpers)
  build_proposed_add_attachment_text() → str
  ...

src/duckalog/studio/semantic_model_editing.py  (NEW — this plan)
  build_proposed_add_semantic_model_text() → str
  build_proposed_edit_semantic_model_text() → str
  build_proposed_duplicate_semantic_model_text() → str
  build_proposed_delete_semantic_model_text() → str
  # Same raw-dict mutation + yaml.safe_dump() / json.dumps() pattern

src/duckalog/studio/app.py  (StarHTML ASGI app)
  GET /catalog/forms/semantic-models  → semantic model list page
  GET /catalog/forms/semantic-models/add → add form
  GET /catalog/forms/semantic-models/{name} → edit form (pre-populated)
  GET /catalog/forms/semantic-models/{name}/duplicate
  GET /catalog/forms/semantic-models/{name}/delete
  POST /catalog/forms/semantic-models/validate
  POST /catalog/forms/semantic-models/preview
  POST /catalog/forms/semantic-models/save
  POST /catalog/forms/semantic-models/add/validate|preview|save
  POST /catalog/forms/semantic-models/{name}/validate|preview|save
```

**Critical constraint**: All helpers MUST work from `yaml.safe_load()` / `json.loads()` on raw draft text, NOT from `Config.model_dump()` or a loaded `Config` object. Serialization MUST use `yaml.safe_dump(sort_keys=False)` or `json.dumps(indent=2)`. Route handlers MUST call `validate_config_text()` and `save_config_text_safely()` and MUST NOT write files directly.

## Start Here

1. **Open `src/duckalog/config/models.py` lines 490–820** — All `Semantic*Config` model definitions and intra-model validators. This is the canonical field reference for every form field.

2. **Open `src/duckalog/config/models.py` lines 1029–1112** — `Config._validate_uniqueness()` for cross-reference validation rules (base_view resolution, join to_view resolution, ambiguous reference errors). These are the validation errors the form editor must surface.

3. **Open `.execflow/plans/catalog-studio-editing-safety/execplan.md`** — Understand the safety service contract: `load_editable_config()`, `validate_config_text()`, `preview_config_diff()`, `save_config_text_safely()`. The semantic model editor must route all writes through these functions.

4. **Open `.execflow/plans/catalog-studio-form-editor/execplan.md`** lines 75–120 — The `build_proposed_view_config_text()` helper pattern. Apply the same pattern to semantic models: parse raw text → mutate dict → serialize → validate.

5. **Open `tests/test_config.py` lines 1199–1402** — `test_semantic_models_v2_with_joins_and_time_dimensions` shows a complete v2 config. This is the ground truth for what a full semantic model YAML looks like and what validates successfully.

## Pi-intercom handoff

Scout complete for `catalog-studio-semantic-model-editor`. Output saved to `.execflow/plans/catalog-studio-semantic-model-editor/context.md`.

Key findings:
- Semantic model configs live in `src/duckalog/config/models.py` lines 490–820
- Config-level cross-reference validation (`base_view` → view, `joins[].to_view` → view, ambiguous references) is in `Config._validate_uniqueness()` at lines 1033–1112
- Comprehensive tests in `tests/test_config.py` lines 741–1637, including v2 joins/time_grains/defaults
- Predecessor editing safety service (`editing.py`) and form pattern (`form_editing.py`) define the helper contract to follow
- The critical constraint: helpers MUST parse/serialize raw YAML/JSON (not `Config.model_dump()`) to preserve comments and `sql_file` references in unrelated sections
- Semantic model identity: `(name)` — must be unique across all models
- Form fields include: `name`, `base_view` (with view-name dropdown from existing views), `label`, `description`, `tags`, `dimensions[]` (with `name`, `expression`, `type`, `time_grains`, `label`, `description`), `measures[]` (with `name`, `expression`, `type`, `label`, `description`), `joins[]` (with `to_view`, `type`, `on_condition`), `defaults` (with `time_dimension`, `primary_measure`, `default_filters[]`)

Should I scout any specific area more deeply before the ExecPlan is written? In particular, do you want deeper coverage of the StarHTML signal/UI patterns for the nested dimension/measure/join lists, or deeper coverage of the `test_config.py` semantic model tests to extract all the edge-case validation scenarios?