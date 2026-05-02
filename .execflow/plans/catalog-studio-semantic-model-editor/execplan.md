# Add Catalog Studio semantic model form editing

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document must be maintained in accordance with `.execflow/PLANS.md` from the repository root. It builds on the completed umbrella brainstorm at `.execflow/plans/rebuild-duckalog-ui-starhtml/brainstorm.md` and on the Catalog Studio editing chain through `.execflow/plans/catalog-studio-attachments-secrets-editor/execplan.md`. If the Studio foundation, explorer, query workbench, editing safety service, expert editor, structured form editor, view lifecycle flows, and attachments/secrets editor have not been implemented yet, implement them first. This plan adds structured form editing for semantic models.

## Purpose / Big Picture

After this change, a Catalog Studio user can create and edit semantic models through structured forms. They can choose a base view, define dimensions, measures, joins, defaults, labels, descriptions, and tags, validate the model, preview the diff, and save through the editing safety service. The UI surfaces validation errors for duplicate dimension names, invalid time grains, invalid join types, missing base views, ambiguous view references, and defaults that point to missing dimensions or measures.

This feature makes Duckalog’s semantic layer manageable from Catalog Studio. It builds on the existing view, form, and safety infrastructure without introducing a new save path or a new config serializer.

## Progress

- [x] (2026-04-30) Created prerequisite ExecPlans through attachments/secrets editor.
- [x] (2026-04-30) Read semantic model config classes, whole-config validation rules, semantic model tests, and predecessor editing plans.
- [x] (2026-04-30) Ran a scout pass and saved context at `.execflow/plans/catalog-studio-semantic-model-editor/context.md`.
- [ ] Confirm the full predecessor chain is implemented and tests pass.
- [ ] Add pure helper functions that build proposed raw text for semantic model add/edit/duplicate/delete operations.
- [ ] Add normalization helpers for dimensions, measures, joins, defaults, tags, and default filters.
- [ ] Add StarHTML components and routes for semantic model list, add, edit, duplicate, and delete flows.
- [ ] Route validate, preview, and save through the editing safety service.
- [ ] Add tests for model-name uniqueness, base-view resolution, dimension/measure validation, joins, defaults, time grains, save backups, and unrelated `sql_file` preservation.
- [ ] Run `starhtml-check`, Studio tests, semantic-model tests, and old dashboard tests, then update this plan with results.

## Surprises & Discoveries

- Observation: Semantic model validation has two layers.
  Evidence: `SemanticModelConfig._validate_uniqueness()` validates dimensions, measures, conflicts, and defaults inside one semantic model. `Config._validate_uniqueness()` validates semantic model names and view references across the whole config.

- Observation: Base view and join references can be ambiguous.
  Evidence: `Config._validate_uniqueness()` resolves schema-qualified references such as `analytics.orders` and rejects ambiguous unqualified references when multiple schemas contain the same view name.

- Observation: Time grains are only valid for time dimensions.
  Evidence: `SemanticDimensionConfig._validate_time_grains()` rejects non-empty `time_grains` unless `type == "time"` and validates each grain against `year`, `quarter`, `month`, `week`, `day`, `hour`, `minute`, and `second`.

- Observation: The existing semantic model tests are comprehensive and should shape this editor’s acceptance criteria.
  Evidence: `tests/test_config.py` covers basic/minimal semantic models, duplicate model names, missing base views, duplicate dimensions/measures, dimension-measure conflicts, joins, time grains, defaults, env interpolation, schema-qualified base views, and ambiguous references.

## Decision Log

- Decision: Implement semantic models after view lifecycle and attachments/secrets editing.
  Rationale: Semantic models depend on existing views and are easier to validate after the core config editor and view lifecycle flows exist.
  Date/Author: 2026-04-30 / planning session

- Decision: Use `name` as semantic model identity.
  Rationale: `Config` enforces semantic model name uniqueness globally. Edit, duplicate, and delete helpers can identify semantic models by name.
  Date/Author: 2026-04-30 / planning session

- Decision: Support add, edit, duplicate, and delete semantic models in this plan, but not live query-building from semantic models.
  Rationale: This plan is about config authoring. Query generation or BI-style exploration on top of semantic models is a separate product feature.
  Date/Author: 2026-04-30 / planning session

- Decision: Use JSON textareas for advanced nested fields that are not yet ergonomic as dynamic controls.
  Rationale: `defaults.default_filters` is an arbitrary list of dictionaries. A JSON textarea keeps the first editor complete without building a dynamic filter-builder UI.
  Date/Author: 2026-04-30 / planning session

- Decision: Continue using raw dictionary mutation and safety-service saves.
  Rationale: The editor must preserve unrelated config details, including comments where possible and `sql_file` references in view sections. It must not serialize a loaded `Config` object.
  Date/Author: 2026-04-30 / planning session

## Outcomes & Retrospective

No implementation outcomes have been produced yet. At completion, update this section with exact helper names, routes, supported fields, validation coverage, tests run, and any nested-list UX limitations discovered.

## Context and Orientation

Duckalog semantic models live in the top-level `semantic_models` list of the config. A semantic model gives business-friendly metadata for one base view. It contains dimensions, measures, joins, defaults, label, description, and tags.

A dimension has `name`, `expression`, optional `label`, optional `description`, optional `type`, and optional `time_grains`. A measure has `name`, `expression`, optional `label`, optional `description`, and optional `type`. A join has `to_view`, `type`, and `on_condition`. Defaults can set `time_dimension`, `primary_measure`, and `default_filters`.

The editing safety service from earlier plans is the only write path. The form editor pattern parses raw YAML or JSON into a plain dictionary, changes one section, serializes proposed text, validates the whole config, previews the diff, and saves through `save_config_text_safely()`. Semantic model helpers must follow that same pattern. Do not call `load_config()` and then serialize `Config.model_dump()`, because normal loading may inline SQL file references in unrelated views.

The view lifecycle plan handles renaming and deleting views. That plan updates semantic model references on view rename and blocks deleting referenced views. This semantic model editor should provide the complementary capability: users can explicitly edit semantic model references, joins, and defaults.

## Plan of Work

Begin by verifying prerequisites. The Studio editing service, form editor, view lifecycle, and attachments/secrets editor should exist and pass tests. If not, stop and implement the prerequisite chain first.

Add a pure helper module such as `src/duckalog/studio/semantic_model_editing.py`. It should parse the current editable draft text into a plain dictionary, modify the top-level `semantic_models` list, serialize proposed text to the same format, and validate using the editing safety service. It should expose operations equivalent to add, edit, duplicate, and delete.

Implement normalization helpers. Convert form values into a semantic model dictionary matching `SemanticModelConfig`. Tags can be comma-separated text converted to a list. Dimensions, measures, and joins may be submitted as structured repeated form groups if the existing StarHTML form pattern supports them, or as JSON textareas in the first implementation. For a practical first version, use a hybrid: simple top-level fields as individual controls, and dimensions/measures/joins as JSON or YAML-like textareas that parse into lists of dictionaries. Defaults can use simple selectors for `time_dimension` and `primary_measure`, plus a JSON textarea for `default_filters`.

Implement `build_proposed_add_semantic_model_text(draft, values)`. It should append a new semantic model to `semantic_models`, serialize proposed text, and validate. Duplicate names, missing base views, invalid dimensions, invalid defaults, and ambiguous references should return validation errors before save.

Implement `build_proposed_edit_semantic_model_text(draft, original_name, values)`. It should locate the semantic model by name, replace its raw dictionary with the normalized dictionary, serialize, and validate. If the name changes, the proposed config must still satisfy global uniqueness. No other sections should change.

Implement `build_proposed_duplicate_semantic_model_text(draft, source_name, new_name)`. It should copy the source model raw dictionary, update `name`, insert the copy immediately after the source semantic model, serialize, and validate. Duplicating without a unique name must be rejected.

Implement `build_proposed_delete_semantic_model_text(draft, name)`. It should remove the model from `semantic_models`, serialize, and validate. Unlike view deletion, semantic model deletion does not affect engine view creation directly, so no cross-reference update is needed unless future features reference semantic models; none are in scope here.

Add helper functions that list valid base view choices and join target choices from raw config views. Include schema-qualified display for duplicate view names across schemas. The UI should encourage schema-qualified references when ambiguity exists.

Add StarHTML components. Add a semantic models list page showing model name, base view, dimension count, measure count, join count, and tags. Add add/edit/duplicate/delete forms. Add validation, preview, and save panels consistent with previous editors. The edit page should link to the Expert Editor for raw control.

Add routes. Recommended routes are `GET /catalog/forms/semantic-models`, `GET /catalog/forms/semantic-models/add`, `GET /catalog/forms/semantic-models/{name}/edit`, `GET /catalog/forms/semantic-models/{name}/duplicate`, `GET /catalog/forms/semantic-models/{name}/delete`, plus POST endpoints for validate, preview, and save for add/edit/duplicate/delete. Follow actual route conventions from prior Studio editors if they differ.

Every POST route should call semantic model helper functions to generate proposed text, then call the editing safety service for validation, preview, or save. Validate and preview must not write. Save must create backups via the safety service.

Add tests. Direct helper tests should cover add minimal model, add full model with dimensions/measures/joins/defaults, duplicate name rejection, missing base view rejection, duplicate dimension names, duplicate measure names, dimension/measure conflict, invalid join type, invalid time grain, time grains on non-time dimension, invalid defaults, schema-qualified base view success, ambiguous base view rejection, duplicate semantic model success with new name, delete success, and `sql_file` preservation in unrelated views. Route tests should cover list/render pages and representative validate/preview/save flows.

Run `starhtml-check` on changed UI files, all Studio editing tests, and old dashboard tests.

## Concrete Steps

Work from the repository root `/Users/volker/coding/libs/duckalog`.

Verify prerequisites:

    uv run python - <<'PY'
    from duckalog.studio import create_app, StudioContext
    from duckalog.studio import editing, form_editing, view_lifecycle
    print(create_app, StudioContext, editing, form_editing, view_lifecycle)
    PY

Run prerequisite tests:

    uv run pytest tests/test_studio_editing.py tests/test_studio_expert_editor.py tests/test_studio_form_editor.py tests/test_studio_view_lifecycle.py tests/test_studio_attachments_secrets_editor.py -q

Inspect semantic model validation and existing semantic tests:

    rg -n "class Semantic|semantic_models|base_view|to_view|time_grains|default_filters|ambiguous" src/duckalog/config/models.py tests/test_config.py

After adding helper functions, run a direct smoke test. Adjust names to match implementation:

    uv run python - <<'PY'
    from pathlib import Path
    from duckalog.studio.editing import load_editable_config, validate_config_text
    from duckalog.studio.semantic_model_editing import (
        build_proposed_add_semantic_model_text,
        build_proposed_duplicate_semantic_model_text,
        build_proposed_delete_semantic_model_text,
    )

    path = Path('/tmp/duckalog-semantic-editor.yaml')
    path.write_text('''version: 1
    duckdb:
      database: ":memory:"
    views:
      - name: orders
        sql_file:
          path: orders.sql
      - name: customers
        sql: "select 1 as customer_id"
    semantic_models: []
    ''')
    draft = load_editable_config(path)
    proposed = build_proposed_add_semantic_model_text(draft, {
        'name': 'orders_model',
        'base_view': 'orders',
        'dimensions': [{'name': 'order_date', 'expression': 'order_date', 'type': 'time', 'time_grains': ['day', 'month']}],
        'measures': [{'name': 'order_count', 'expression': 'count(*)', 'type': 'number'}],
        'joins': [{'to_view': 'customers', 'type': 'left', 'on_condition': 'orders.customer_id = customers.customer_id'}],
        'defaults': {'time_dimension': 'order_date', 'primary_measure': 'order_count'},
    })
    assert validate_config_text(proposed, draft.format, base_path=path).ok
    assert 'sql_file:' in proposed
    dup = build_proposed_duplicate_semantic_model_text(load_editable_config(path), 'orders_model', 'orders_model_copy') if 'orders_model' in path.read_text() else proposed
    delete = build_proposed_delete_semantic_model_text(load_editable_config(path), 'orders_model') if 'orders_model' in path.read_text() else proposed
    print('semantic model helpers ok')
    PY

Run StarHTML checks after adding UI:

    starhtml-check src/duckalog/studio/app.py
    starhtml-check src/duckalog/studio/components.py

If semantic components live in a new file, check it too:

    starhtml-check src/duckalog/studio/semantic_model_components.py

Run focused tests:

    uv run pytest tests/test_studio_semantic_model_editor.py -q

Run all Studio editing tests:

    uv run pytest tests/test_studio_editing.py tests/test_studio_expert_editor.py tests/test_studio_form_editor.py tests/test_studio_view_lifecycle.py tests/test_studio_attachments_secrets_editor.py tests/test_studio_semantic_model_editor.py -q

Run old dashboard and existing semantic config tests:

    uv run pytest tests/test_dashboard.py tests/test_config.py -q

Manual smoke test:

    cat >/tmp/duckalog-semantic-editor.yaml <<'YAML'
    version: 1
    duckdb:
      database: ":memory:"
    views:
      - name: orders
        sql: "select 1 as order_id, current_date as order_date"
    semantic_models: []
    YAML

Start Studio:

    uv run duckalog studio /tmp/duckalog-semantic-editor.yaml --port 8788

Verify pages exist:

    curl -s http://127.0.0.1:8788/catalog/forms/semantic-models | rg "Semantic Models|New Semantic Model"
    curl -s http://127.0.0.1:8788/catalog/forms/semantic-models/add | rg "Base View|Dimensions|Measures|Validate|Preview diff|Save"

During implementation, add working validate, preview, and save curl examples once the StarHTML request format is known.

## Validation and Acceptance

Acceptance is user-visible. A user can list semantic models, add a minimal or full semantic model, edit an existing semantic model, duplicate it under a new name, and delete it. The UI validates base view and join references against configured views, validates dimension/measure/default rules, previews diffs, and saves through the editing safety service. Invalid semantic models show clear errors and do not write files.

Automated tests must prove helper behavior, route behavior, and preservation of unrelated config sections such as `views` with `sql_file` references. Tests must cover the validation edge cases already covered by `tests/test_config.py` where practical. Existing config tests and old dashboard tests must still pass.

StarHTML validation requires `starhtml-check` on every changed Studio UI file with no ERROR findings.

## Idempotence and Recovery

GET routes and validate/preview POST routes must never write. Save routes go through the editing safety service, so each successful save creates a backup and writes atomically. If stale-save protection exists from earlier editors, use it here too.

If a semantic model references an ambiguous view, leave the file unchanged and show a message that the user should choose a schema-qualified reference. If form serialization rewrites more of the file than expected, show the diff and allow the user to cancel or use Expert Editor.

If implementation must be backed out, remove semantic model helpers, components, routes, navigation links, and tests. Keep all previous Studio editors intact.

## Artifacts and Notes

Prerequisite ExecPlans include:

    .execflow/plans/catalog-studio-editing-safety/execplan.md
    .execflow/plans/catalog-studio-expert-editor/execplan.md
    .execflow/plans/catalog-studio-form-editor/execplan.md
    .execflow/plans/catalog-studio-view-lifecycle/execplan.md
    .execflow/plans/catalog-studio-attachments-secrets-editor/execplan.md

Scout context for this plan is:

    .execflow/plans/catalog-studio-semantic-model-editor/context.md

Relevant code references are:

    src/duckalog/config/models.py:SemanticDimensionConfig
    src/duckalog/config/models.py:SemanticMeasureConfig
    src/duckalog/config/models.py:SemanticJoinConfig
    src/duckalog/config/models.py:SemanticDefaultsConfig
    src/duckalog/config/models.py:SemanticModelConfig
    src/duckalog/config/models.py:Config._validate_uniqueness
    tests/test_config.py

Future plans can add a more ergonomic dynamic dimension/measure builder, semantic model query builders, and visual lineage exploration. Those are out of scope here.

## Interfaces and Dependencies

At the end of this plan, helper operations equivalent to these should exist:

    build_proposed_add_semantic_model_text(draft, values) -> str
    build_proposed_edit_semantic_model_text(draft, original_name, values) -> str
    build_proposed_duplicate_semantic_model_text(draft, source_name, new_name) -> str
    build_proposed_delete_semantic_model_text(draft, name) -> str
    list_view_reference_choices(draft) -> list of qualified/unqualified view references

The Studio app should expose list, add, edit, duplicate, delete, validate, preview, and save routes for semantic models. Exact route names may follow conventions established by previous editors, but tests must document them.

Use existing dependencies only: StarHTML, PyYAML, Pydantic, and the standard library. Do not add a dynamic form library, semantic query engine, or round-trip YAML parser in this plan. Do not write files directly outside the editing safety service.

The next ExecPlan should likely cover Iceberg catalog editing or a semantic model exploration/query-builder UI, depending on whether the priority is more config coverage or user-facing analytics workflows.

## Revision Note

2026-04-30: Initial Catalog Studio Semantic Model Editor ExecPlan created. It extends structured editing to semantic models and relies on whole-config validation plus the editing safety service for every save.
