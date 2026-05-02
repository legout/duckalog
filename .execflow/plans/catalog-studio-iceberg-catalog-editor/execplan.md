# Add Catalog Studio Iceberg catalog form editing

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document must be maintained in accordance with `.execflow/PLANS.md` from the repository root. It builds on the completed umbrella brainstorm at `.execflow/plans/rebuild-duckalog-ui-starhtml/brainstorm.md` and on the Catalog Studio editing chain through `.execflow/plans/catalog-studio-semantic-model-editor/execplan.md`. If the Studio foundation, explorer, query workbench, editing safety service, expert editor, structured form editor, view lifecycle, attachments/secrets, and semantic model editor plans have not been implemented yet, implement them first.

## Purpose / Big Picture

After this change, a Catalog Studio user can manage `iceberg_catalogs` through structured forms. They can add, edit, duplicate, and delete Iceberg catalog definitions, validate references from Iceberg-backed views, preview diffs, and save through the editing safety service. The old dashboard remains unchanged.

This completes another major catalog configuration surface. Iceberg catalogs are top-level named resources that views may reference via `source: iceberg` and `catalog: <name>`, so this editor must protect users from breaking existing views by accident.

## Progress

- [x] (2026-04-30) Created prerequisite ExecPlans through semantic model editor.
- [x] (2026-04-30) Inspected `IcebergCatalogConfig` and whole-config validation for catalog/view references.
- [ ] Confirm the full predecessor chain is implemented and tests pass.
- [ ] Add pure helper functions for Iceberg catalog add/edit/duplicate/delete operations.
- [ ] Add reference analysis for views that use an Iceberg catalog.
- [ ] Add StarHTML list, add, edit, duplicate, and delete pages for Iceberg catalogs.
- [ ] Route validate, preview, and save actions through the editing safety service.
- [ ] Add tests for required fields, duplicate names, view-reference validation, delete blocking, rename/update behavior, safe saves, and unrelated config preservation.
- [ ] Run `starhtml-check`, Studio editing tests, Iceberg SQL-generation/config tests, and old dashboard tests.

## Surprises & Discoveries

- Observation: Iceberg catalog configuration is intentionally small.
  Evidence: `IcebergCatalogConfig` has `name`, `catalog_type`, optional `uri`, optional `warehouse`, and `options`.

- Observation: Views can depend on Iceberg catalogs.
  Evidence: `Config._validate_uniqueness()` rejects views where `view.source == "iceberg"` and `view.catalog` does not appear in `iceberg_catalogs`.

- Observation: Iceberg catalog names must be unique.
  Evidence: `Config._validate_uniqueness()` raises `Duplicate Iceberg catalog name(s)` for repeated catalog names.

## Decision Log

- Decision: Use catalog `name` as the editor identity.
  Rationale: Names are globally unique among Iceberg catalogs and are what views reference.
  Date/Author: 2026-04-30 / planning session

- Decision: Delete should be blocked when views reference the catalog.
  Rationale: Removing a referenced catalog would make the config invalid and break view creation. Blocking is safer than silently deleting or rewriting views.
  Date/Author: 2026-04-30 / planning session

- Decision: Rename should offer reference updates for Iceberg views.
  Rationale: A catalog rename is a clear one-to-one transform from old name to new name for `views[].catalog` when `source == "iceberg"`.
  Date/Author: 2026-04-30 / planning session

- Decision: Represent `options` as a JSON textarea in the first structured editor.
  Rationale: Iceberg catalog options are backend-specific. A JSON object field provides completeness without hardcoding provider-specific schemas.
  Date/Author: 2026-04-30 / planning session

## Outcomes & Retrospective

No implementation outcomes have been produced yet. At completion, update this section with exact helper names, routes, reference-update behavior, validation coverage, and test results.

## Context and Orientation

Duckalog supports Iceberg views in two related ways: a view can directly reference Iceberg data, and a view can reference a named Iceberg catalog through its `catalog` field. Named catalogs live in the top-level `iceberg_catalogs` list and are validated by `IcebergCatalogConfig` in `src/duckalog/config/models.py`.

The structured editing pattern is already established by earlier Catalog Studio plans. Helpers must work from raw YAML/JSON text, mutate plain dictionaries, serialize proposed text, validate the full config, and save only through `save_config_text_safely()`. Do not call `load_config()` and serialize `Config.model_dump()`, because that can normalize unrelated authoring details such as `sql_file` references.

## Plan of Work

Begin by verifying the predecessor chain. The Studio package, editing safety service, and earlier structured editors should exist and pass tests.

Add `src/duckalog/studio/iceberg_catalog_editing.py`. It should expose helpers equivalent to:

    build_proposed_add_iceberg_catalog_text(draft, values) -> str
    build_proposed_edit_iceberg_catalog_text(draft, original_name, values, *, update_references: bool = False) -> str
    build_proposed_duplicate_iceberg_catalog_text(draft, source_name, new_name) -> str
    build_proposed_delete_iceberg_catalog_text(draft, name, *, force: bool = False) -> str
    find_iceberg_catalog_references(draft, name) -> list[dict]

The helpers should parse `draft.text` with `yaml.safe_load()` or `json.loads()`, mutate `iceberg_catalogs`, serialize back to the original format, and call validation before save. The add helper appends a catalog. The edit helper replaces a catalog by `original_name`; if the name changes and `update_references=True`, update every view where `source == "iceberg"` and `catalog == original_name`. The duplicate helper copies a raw catalog and changes `name`. The delete helper should reject deletion when references exist unless `force=True`, and even with force the resulting config must validate.

Normalize form values. Required fields are `name` and `catalog_type`. Optional fields are `uri`, `warehouse`, and `options`. Empty optional strings should be omitted or set to null following conventions from earlier editors. `options` should parse as a JSON object and reject arrays/scalars with a clear validation error.

Add reference analysis. For each Iceberg catalog, list views that reference it by name. Include view name, schema, description if available, and route links to the view detail and view edit page when those routes exist. The edit page should warn when renaming a referenced catalog and offer a checkbox to update references. The delete page should show blocking references.

Add StarHTML components and routes. Recommended routes are `GET /catalog/forms/iceberg-catalogs`, `GET /catalog/forms/iceberg-catalogs/add`, `GET /catalog/forms/iceberg-catalogs/{name}/edit`, `GET /catalog/forms/iceberg-catalogs/{name}/duplicate`, `GET /catalog/forms/iceberg-catalogs/{name}/delete`, plus POST endpoints for validate, preview, and save. Follow actual Studio route conventions if earlier editors differ.

Every POST route should generate proposed text with the helper module, call `validate_config_text()` for validation, `preview_config_diff()` for preview, and `save_config_text_safely()` for save. Validate and preview must not write.

Add tests. Required coverage includes adding a minimal catalog, adding a catalog with URI/warehouse/options, rejecting duplicate names, rejecting empty names, rejecting non-object options, editing catalog_type/options, renaming with reference update, rejecting rename without reference update when views would become invalid, blocking delete of referenced catalogs, deleting unreferenced catalogs, preserving unrelated views including `sql_file`, and creating backups on save.

## Concrete Steps

Verify prerequisites:

    uv run pytest tests/test_studio_editing.py tests/test_studio_form_editor.py tests/test_studio_view_lifecycle.py tests/test_studio_attachments_secrets_editor.py tests/test_studio_semantic_model_editor.py -q

Inspect relevant validation:

    rg -n "class IcebergCatalogConfig|iceberg_catalogs|undefined catalog|source == \"iceberg\"" src/duckalog/config/models.py tests

After helpers exist, smoke-test them:

    uv run python - <<'PY'
    from pathlib import Path
    from duckalog.studio.editing import load_editable_config, validate_config_text
    from duckalog.studio.iceberg_catalog_editing import build_proposed_add_iceberg_catalog_text

    path = Path('/tmp/duckalog-iceberg-editor.yaml')
    path.write_text('''version: 1
    duckdb:
      database: ":memory:"
    views:
      - name: orders
        source: iceberg
        catalog: prod
        table: analytics.orders
    iceberg_catalogs: []
    ''')
    draft = load_editable_config(path)
    proposed = build_proposed_add_iceberg_catalog_text(draft, {
        'name': 'prod',
        'catalog_type': 'rest',
        'uri': 'https://iceberg.example/catalog',
        'warehouse': 's3://warehouse',
        'options': {'token': '${env:ICEBERG_TOKEN}'},
    })
    assert validate_config_text(proposed, draft.format, base_path=path).ok
    assert 'iceberg_catalogs:' in proposed
    print('iceberg catalog helper ok')
    PY

Run StarHTML checks:

    starhtml-check src/duckalog/studio/app.py
    starhtml-check src/duckalog/studio/components.py
    starhtml-check src/duckalog/studio/iceberg_catalog_components.py

Run focused tests:

    uv run pytest tests/test_studio_iceberg_catalog_editor.py -q

Run broader validation:

    uv run pytest tests/test_studio_*.py tests/test_config.py tests/test_sql_generation.py tests/test_dashboard.py -q

## Validation and Acceptance

A user can list Iceberg catalogs, add a catalog, edit its fields, duplicate it with a new name, rename it with optional view-reference updates, and delete only when safe. Invalid operations show validation errors and do not write. Preview shows the proposed diff. Save creates a backup and reload-verifies the config.

Automated tests must prove all helper operations, route rendering, safe save behavior, and old dashboard preservation. `starhtml-check` must pass on changed Studio UI files.

## Idempotence and Recovery

GET routes and validate/preview POST routes never write. Save routes use the editing safety service. If delete or rename would invalidate existing Iceberg views, reject before save unless the operation explicitly updates references and the resulting config validates.

If implementation must be backed out, remove Iceberg catalog helper/component/routes/tests and navigation links. Keep prior Studio editors intact.

## Artifacts and Notes

Relevant code references:

    src/duckalog/config/models.py:IcebergCatalogConfig
    src/duckalog/config/models.py:Config._validate_uniqueness
    tests/test_sql_generation.py
    docs/reference/config-schema.md

Future work can add provider-specific Iceberg catalog presets and live connectivity tests. Those are out of scope here.

## Revision Note

2026-04-30: Initial Catalog Studio Iceberg Catalog Editor ExecPlan created.
