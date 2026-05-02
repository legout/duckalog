# Add Catalog Studio view create, duplicate, rename, and delete flows

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document must be maintained in accordance with `.execflow/PLANS.md` from the repository root. It builds on the completed umbrella brainstorm at `.execflow/plans/rebuild-duckalog-ui-starhtml/brainstorm.md` and on these prerequisite ExecPlans: `.execflow/plans/starhtml-catalog-studio-foundation/execplan.md`, `.execflow/plans/catalog-studio-explorer/execplan.md`, `.execflow/plans/catalog-studio-query-workbench/execplan.md`, `.execflow/plans/catalog-studio-editing-safety/execplan.md`, `.execflow/plans/catalog-studio-expert-editor/execplan.md`, and `.execflow/plans/catalog-studio-form-editor/execplan.md`. If any prerequisite is not implemented yet, implement it first. This plan extends the structured form editor with safe view lifecycle flows: create, duplicate, rename, and delete.

## Purpose / Big Picture

After this change, a Catalog Studio user can manage the lifecycle of catalog views through structured UI flows. They can create a new view, duplicate an existing view under a new name, rename a view, and delete a view after confirmation. Every operation generates proposed raw config text, validates the full config, previews the diff, and saves only through the editing safety service. Operations that would break semantic models or create duplicate view names are blocked before writing.

This matters because views are the core unit of Duckalog catalogs. The previous form editor lets users edit existing view fields; this plan completes the basic view management workflow while preserving the safety guarantees and raw-text handling established by earlier plans.

## Progress

- [x] (2026-04-30) Created prerequisite ExecPlans through Structured Catalog Form Editor.
- [x] (2026-04-30) User selected View create/delete flows over attachments/secrets form editor as the next plan.
- [x] (2026-04-30) Read the structured form editor and editing safety plans plus `Config`, `ViewConfig`, and semantic model validation code.
- [x] (2026-04-30) Ran a scout pass and saved view-lifecycle context at `.execflow/plans/catalog-studio-view-lifecycle/context.md`.
- [ ] Confirm the structured form editor helpers and editing safety service exist and pass tests.
- [ ] Add pure helper functions that build proposed raw text for add, duplicate, rename, and delete view operations.
- [ ] Add dependency-impact analysis for delete and rename operations, especially semantic model `base_view` and `joins[].to_view` references.
- [ ] Add StarHTML pages/routes for add view, duplicate view, rename view, and delete confirmation.
- [ ] Route all validate, preview, and save actions through the editing safety service.
- [ ] Add tests for duplicate-name rejection, SQL-source mutual exclusivity, delete blocking, delete success, duplicate success, rename reference updates, `sql_file` preservation, backup creation, and old dashboard preservation.
- [ ] Run `starhtml-check`, Studio tests, editing tests, form-editor tests, and existing dashboard tests, then update this plan with results.

## Surprises & Discoveries

- Observation: View uniqueness is schema-qualified.
  Evidence: `src/duckalog/config/models.py:Config._validate_uniqueness()` tracks duplicate views by `(view.db_schema, view.name)`, so `main.foo` and `analytics.foo` are distinct while two `analytics.foo` entries are duplicates.

- Observation: Semantic models can make view deletion and rename unsafe.
  Evidence: `SemanticModelConfig.base_view` and `SemanticJoinConfig.to_view` must reference existing views. `Config._validate_uniqueness()` validates missing base views and join targets after view lookup construction.

- Observation: Normal config loading can destroy `sql_file` and `sql_template` references.
  Evidence: `src/duckalog/config/loading/sql.py:process_sql_file_references()` replaces `sql_file` or `sql_template` with inline `sql`. Lifecycle helpers must parse raw text directly rather than serializing a loaded `Config` object.

- Observation: The predecessor form editor intentionally deferred add/delete flows.
  Evidence: `.execflow/plans/catalog-studio-form-editor/execplan.md` explicitly says add/delete view flows are out of scope and should be handled by a later plan.

## Decision Log

- Decision: Support create, duplicate, rename, and delete existing views in one lifecycle plan.
  Rationale: These operations share the same raw-text transformation, validation, diff, and save pipeline. Planning them together ensures route and helper naming stays coherent.
  Date/Author: 2026-04-30 / planning session

- Decision: Keep lifecycle helpers pure Python and separate from StarHTML route handlers.
  Rationale: They need direct tests and must not depend on browser behavior. Route handlers should stay thin and call helpers plus the editing safety service.
  Date/Author: 2026-04-30 / planning session

- Decision: Insert newly created views at the end of the `views` list, and insert duplicated views immediately after the source view.
  Rationale: Appending new views is predictable. Placing duplicates next to their source preserves local context and avoids surprising reordering of unrelated views.
  Date/Author: 2026-04-30 / planning session

- Decision: Delete does not auto-update semantic model references; rename does.
  Rationale: Deleting a referenced view is destructive and ambiguous, so it should be blocked with a dependency report. Renaming has a clear one-to-one mapping from old reference to new reference, so it can update semantic model references atomically.
  Date/Author: 2026-04-30 / planning session

- Decision: Preserve `sql_file` and `sql_template` references by working from raw parsed dictionaries.
  Rationale: Serializing a loaded `Config` would risk converting file references into inline SQL. The lifecycle helpers must modify raw dictionaries and then validate proposed text.
  Date/Author: 2026-04-30 / planning session

## Outcomes & Retrospective

No implementation outcomes have been produced yet. At completion, update this section with the exact routes and helpers added, which dependency cases are blocked or auto-updated, test results, and any remaining lifecycle gaps.

## Context and Orientation

Duckalog views are configured under the top-level `views` list in YAML or JSON config files. A view can be defined with inline SQL, a SQL file reference, a SQL template reference, or an external source definition. `ViewConfig` validates those shapes. `Config` validates whole-config relationships, including duplicate view names and semantic model references to views.

The editing safety service from the earlier plan owns raw-text loading, validation, diff preview, backup, atomic save, and reload verification. The structured form editor from the previous plan owns editing fields on existing views. This lifecycle plan should extend that form editor. It should not create a second save path and should not use `Path.write_text()` directly.

A semantic model is business metadata over a base view. In config, `SemanticModelConfig.base_view` names the base view. Joins inside semantic models use `SemanticJoinConfig.to_view` to reference additional views. If a referenced view is deleted, the config becomes invalid. If a referenced view is renamed, references should be updated atomically when the rename has a clear target.

View references can be schema-qualified. A reference such as `analytics.orders` maps to schema `analytics` and view name `orders`. An unqualified reference such as `orders` can become ambiguous when multiple schemas contain a view named `orders`. Lifecycle operations must validate the whole proposed config before saving, and rename should detect ambiguity before trying to rewrite references.

## Plan of Work

Begin by verifying prerequisites. The Studio package, editing safety service, expert editor, structured form editor, and their tests must exist and pass. If not, stop and implement the prerequisite plans first.

Add a pure helper module such as `src/duckalog/studio/view_lifecycle.py`, or extend `src/duckalog/studio/form_editing.py` if that module already contains all form text-generation helpers. The lifecycle helper module should parse the current draft text into a plain dictionary, modify only the `views` list and required semantic model references, serialize proposed text back to the same format, then call or return data suitable for `validate_config_text()`.

Implement `build_proposed_add_view_text(draft, values)`. It should normalize values using the same view form normalization logic from the structured form editor, append the new view dict to the `views` list, serialize proposed text, and validate it. Duplicate view names and invalid view definitions should be surfaced as validation errors. The UI may prefill a minimal valid inline SQL view such as `select 1 as example` or require the user to provide a definition before validation succeeds.

Implement `build_proposed_duplicate_view_text(draft, source_view_ref, new_name, new_schema=None)`. It should locate the source view by schema and name, copy its raw dictionary, update `name` and optionally `db_schema`, insert the copy immediately after the source view, serialize, and validate. It must reject duplicate `(schema, name)` targets before save. It must preserve the source view’s `sql_file`, `sql_template`, `options`, tags, and source fields as raw dictionary values.

Implement `build_proposed_delete_view_text(draft, view_ref)`. It should locate the target view and perform dependency analysis before producing proposed text. If any semantic model `base_view` or join `to_view` references the target view, return a blocked result with a list of dependent semantic models and fields. Do not auto-delete semantic models or joins in this plan. If there are no dependencies, remove the view from the `views` list, serialize, and validate. Deleting the last view may be allowed only if `Config` validation permits an empty `views` list; if validation rejects it, surface that error and do not write.

Implement `build_proposed_rename_view_text(draft, view_ref, new_name, new_schema=None)`. It should locate the view, update its `name` and optionally `db_schema`, update semantic model `base_view` and `joins[].to_view` references that resolve exactly to the old view, serialize, and validate. If an unqualified semantic model reference is ambiguous, block the operation and ask the user to make references schema-qualified in Expert Editor or a later semantic-model form. If the new `(schema, name)` target already exists, block via validation. When updating references, preserve the reference style where possible: if an old reference was schema-qualified, write the new schema-qualified reference; if it was unqualified and remains unambiguous, write the new unqualified name.

Add impact-analysis helpers. For delete, return a dependency report such as “semantic model revenue_model base_view” or “semantic model revenue_model joins[0].to_view”. For rename, return a list of references that will be updated. The UI should show this before preview/save.

Add StarHTML components for view lifecycle pages. Add a “New View” button on the catalog views list. Add “Duplicate”, “Rename”, and “Delete” actions on the view detail page or form editor page. Delete must use a confirmation page or modal-style page that shows the view name, schema, and dependency report. Duplicate and add may reuse the structured view form in create mode. Rename can be a small focused form with name and schema fields plus dependency impact preview.

Add routes. Recommended routes are `GET /catalog/views/add`, `POST /catalog/views/add/validate`, `POST /catalog/views/add/preview`, `POST /catalog/views/add/save`, `GET /catalog/views/{view_name}/duplicate`, `POST /catalog/views/duplicate/validate`, `POST /catalog/views/duplicate/preview`, `POST /catalog/views/duplicate/save`, `GET /catalog/views/{view_name}/rename`, `POST /catalog/views/rename/validate`, `POST /catalog/views/rename/preview`, `POST /catalog/views/rename/save`, `GET /catalog/views/{view_name}/delete`, `POST /catalog/views/delete/preview`, and `POST /catalog/views/delete/save`. If schemas are needed in URLs, use query parameters or include a stable encoded view reference to avoid ambiguity. Follow actual route conventions established by prior Studio work.

Each POST route should call the lifecycle helper to generate proposed text, call the editing safety service to validate or preview, and call `save_config_text_safely()` only for save actions. Validate and preview must not write. Save must require valid proposed text and should use stale-check protection if the expert/form editors already implemented it.

Add tests. Direct helper tests are mandatory. Cover add duplicate rejection, add valid view success, invalid SQL-source combination rejection, duplicate valid view preserving `sql_file`, duplicate name rejection, delete blocked by semantic model `base_view`, delete blocked by semantic model join, delete success for unreferenced view, rename updating semantic model `base_view`, rename updating joins, rename duplicate target rejection, and ambiguous reference blocking. Route tests should cover rendering action pages and at least one success and one blocked path per operation. Save tests should verify backup creation, reload verification, and `sql_file` preservation.

Run `starhtml-check` on changed Studio UI files, run all lifecycle/form/editing/expert tests, then run old dashboard tests.

## Concrete Steps

Work from the repository root `/Users/volker/coding/libs/duckalog`.

Verify prerequisites:

    uv run python - <<'PY'
    from duckalog.studio import create_app, StudioContext
    from duckalog.studio import editing
    from duckalog.studio import form_editing
    print(create_app, StudioContext, editing, form_editing)
    PY

Run prerequisite tests:

    uv run pytest tests/test_studio_editing.py tests/test_studio_expert_editor.py tests/test_studio_form_editor.py -q

If prior Studio tests are split, include them:

    uv run pytest tests/test_studio.py tests/test_studio_explorer.py tests/test_studio_query.py tests/test_studio_editing.py tests/test_studio_expert_editor.py tests/test_studio_form_editor.py -q

Inspect validation logic and form helper conventions:

    rg -n "def _validate_uniqueness|base_view|to_view|build_proposed_view_config_text|validate_config_text|save_config_text_safely" src/duckalog/config/models.py src/duckalog/studio tests

After adding helper functions, run a direct smoke test for add/delete/duplicate/rename. Adjust function names to match implementation:

    uv run python - <<'PY'
    from pathlib import Path
    from duckalog.studio.editing import load_editable_config, validate_config_text
    from duckalog.studio.view_lifecycle import (
        build_proposed_add_view_text,
        build_proposed_duplicate_view_text,
        build_proposed_delete_view_text,
        build_proposed_rename_view_text,
    )

    path = Path('/tmp/duckalog-view-lifecycle.yaml')
    path.write_text('''version: 1
    duckdb:
      database: ":memory:"
    views:
      - name: demo
        sql_file:
          path: query.sql
        description: "Demo"
      - name: solo
        sql: "select 2 as id"
    semantic_models:
      - name: model
        base_view: demo
    ''')
    draft = load_editable_config(path)
    add_text = build_proposed_add_view_text(draft, {'name': 'new_view', 'definition_kind': 'inline_sql', 'sql': 'select 3 as id'})
    assert validate_config_text(add_text, draft.format, base_path=path).ok
    dup_text = build_proposed_duplicate_view_text(draft, source_view_ref='demo', new_name='demo_copy')
    assert 'demo_copy' in dup_text and 'sql_file:' in dup_text
    delete_text = build_proposed_delete_view_text(draft, view_ref='solo')
    assert 'solo' not in delete_text
    rename_text = build_proposed_rename_view_text(draft, view_ref='demo', new_name='demo_renamed')
    assert 'demo_renamed' in rename_text and 'base_view: demo_renamed' in rename_text
    print('view lifecycle helpers ok')
    PY

Run StarHTML checks after adding UI routes/components:

    starhtml-check src/duckalog/studio/app.py
    starhtml-check src/duckalog/studio/components.py

If lifecycle UI lives in new files, check them too:

    starhtml-check src/duckalog/studio/view_lifecycle_components.py

Run focused tests:

    uv run pytest tests/test_studio_view_lifecycle.py -q

Run all Studio editing tests:

    uv run pytest tests/test_studio_editing.py tests/test_studio_expert_editor.py tests/test_studio_form_editor.py tests/test_studio_view_lifecycle.py -q

Run all Studio tests and old dashboard tests:

    uv run pytest tests/test_studio.py tests/test_studio_explorer.py tests/test_studio_query.py tests/test_studio_editing.py tests/test_studio_expert_editor.py tests/test_studio_form_editor.py tests/test_studio_view_lifecycle.py -q
    uv run pytest tests/test_dashboard.py -q

Manual smoke test:

    cat >/tmp/duckalog-view-lifecycle.yaml <<'YAML'
    version: 1
    duckdb:
      database: ":memory:"
    views:
      - name: demo
        sql: "select 1 as id"
        description: "Demo view"
      - name: solo
        sql: "select 2 as id"
    YAML

Start Studio:

    uv run duckalog studio /tmp/duckalog-view-lifecycle.yaml --port 8788

Verify pages exist:

    curl -s http://127.0.0.1:8788/catalog/views/add | rg "New View|Validate|Preview diff|Save"
    curl -s http://127.0.0.1:8788/catalog/views/demo/duplicate | rg "Duplicate|demo|Save"
    curl -s http://127.0.0.1:8788/catalog/views/demo/rename | rg "Rename|demo|Save"
    curl -s http://127.0.0.1:8788/catalog/views/solo/delete | rg "Delete|solo|Confirm"

Endpoint curl commands depend on the implemented StarHTML request format. During implementation, add working validate, preview, and save curl examples to this plan.

## Validation and Acceptance

Acceptance is user-visible. A user can open Catalog Studio, add a new view through a structured form, duplicate an existing view, rename a view, and delete an unreferenced view after confirmation. The UI previews diffs before saves. Duplicate names, invalid view definitions, referenced-view deletion, and ambiguous renames are blocked with clear errors. Successful saves create backups, write atomically, reload valid config, preserve `sql_file`/`sql_template` references, and update semantic model references when renaming.

Automated tests must prove helper behavior and route behavior. Helper tests must work directly on temporary raw YAML/JSON drafts. Route tests must prove validate/preview are read-only and save uses the safety service. Regression tests must prove the structured form editor, expert editor, editing safety service, and old dashboard still pass.

StarHTML validation requires `starhtml-check` on every changed Studio UI file with no ERROR findings.

## Idempotence and Recovery

GET routes and validate/preview POST routes must never write files. Save routes are safe to repeat only when the current draft has not changed externally; use stale-save protection if available. Each successful save must create a backup through the editing safety service.

If delete is blocked by dependencies, leave the file unchanged and show the dependency list. If rename dependency updates cannot be computed unambiguously, leave the file unchanged and tell the user to resolve references manually in Expert Editor or a later semantic-model editor.

If implementation must be backed out, remove lifecycle helpers, routes, components, navigation actions, and tests. Keep existing view edit forms, expert editor, and editing safety service intact.

## Artifacts and Notes

The prerequisite ExecPlans are:

    .execflow/plans/starhtml-catalog-studio-foundation/execplan.md
    .execflow/plans/catalog-studio-explorer/execplan.md
    .execflow/plans/catalog-studio-query-workbench/execplan.md
    .execflow/plans/catalog-studio-editing-safety/execplan.md
    .execflow/plans/catalog-studio-expert-editor/execplan.md
    .execflow/plans/catalog-studio-form-editor/execplan.md

The scout context for this plan is:

    .execflow/plans/catalog-studio-view-lifecycle/context.md

Relevant code references are:

    src/duckalog/config/models.py:ViewConfig
    src/duckalog/config/models.py:Config._validate_uniqueness
    src/duckalog/config/models.py:SemanticModelConfig
    src/duckalog/config/models.py:SemanticJoinConfig
    src/duckalog/config/loading/sql.py:process_sql_file_references
    src/duckalog/studio/editing.py
    src/duckalog/studio/form_editing.py

Future lifecycle plans can add bulk reorder, import-aware edits, create/delete semantic models, and attachments/secrets lifecycle flows. Those are out of scope here.

## Interfaces and Dependencies

At the end of this plan, helper operations equivalent to these should exist:

    build_proposed_add_view_text(draft, values) -> str or blocked result
    build_proposed_duplicate_view_text(draft, source_view_ref, new_name, new_schema=None) -> str or blocked result
    build_proposed_delete_view_text(draft, view_ref) -> str or blocked result
    build_proposed_rename_view_text(draft, view_ref, new_name, new_schema=None) -> str or blocked result
    analyze_view_dependencies(draft, view_ref) -> dependency report

The Studio app should expose routes equivalent to:

    GET /catalog/views/add
    POST /catalog/views/add/validate
    POST /catalog/views/add/preview
    POST /catalog/views/add/save
    GET /catalog/views/{view_name}/duplicate
    POST /catalog/views/duplicate/validate
    POST /catalog/views/duplicate/preview
    POST /catalog/views/duplicate/save
    GET /catalog/views/{view_name}/rename
    POST /catalog/views/rename/validate
    POST /catalog/views/rename/preview
    POST /catalog/views/rename/save
    GET /catalog/views/{view_name}/delete
    POST /catalog/views/delete/preview
    POST /catalog/views/delete/save

Use only existing dependencies: StarHTML, PyYAML, Pydantic, and the standard library. Do not add a round-trip YAML parser in this plan. Do not write files directly outside the editing safety service.

The next ExecPlan should likely cover attachments/secrets form editing, because view lifecycle plus view forms covers the core catalog-view workflow.

## Revision Note

2026-04-30: Initial Catalog Studio View Lifecycle ExecPlan created. It extends the structured form editor with add, duplicate, rename, and delete flows while preserving raw config references and routing all writes through the editing safety service.
