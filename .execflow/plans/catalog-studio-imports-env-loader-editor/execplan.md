# Add Catalog Studio imports, env files, and loader settings editor

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document must be maintained in accordance with `.execflow/PLANS.md` from the repository root. It builds on the completed umbrella brainstorm at `.execflow/plans/rebuild-duckalog-ui-starhtml/brainstorm.md` and on the Catalog Studio editing chain through `.execflow/plans/catalog-studio-iceberg-catalog-editor/execplan.md`. If the Studio foundation, explorer, query workbench, editing safety service, expert editor, structured form editor, view lifecycle, attachments/secrets, semantic model editor, and Iceberg catalog editor have not been implemented yet, implement them first.

## Purpose / Big Picture

After this change, a Catalog Studio user can inspect and edit configuration composition settings: `imports`, `env_files`, and `loader_settings`. They can switch between simple imports and selective imports, set import override behavior, manage environment file patterns, and tune loader concurrency settings. Every change validates the full config, previews a diff, creates a backup on save, and reload-verifies the saved file.

This plan gives users safe control over the config-loading layer that determines how a Duckalog catalog is assembled from multiple files and environment sources.

## Progress

- [x] (2026-04-30) Created prerequisite ExecPlans through Iceberg catalog editor.
- [x] (2026-04-30) Inspected config models for `ImportEntry`, `SelectiveImports`, `env_files`, and `LoaderSettings`.
- [ ] Confirm the full predecessor chain is implemented and tests pass.
- [ ] Add pure helper functions for imports/env/loader settings updates.
- [ ] Add path and section normalization helpers for simple and selective imports.
- [ ] Add StarHTML pages and routes for imports, env files, and loader settings.
- [ ] Route validate, preview, and save through the editing safety service.
- [ ] Add tests for simple imports, selective imports, override flags, env files, loader settings, validation-only behavior, safe save behavior, and old dashboard preservation.
- [ ] Run `starhtml-check`, Studio editing tests, config import tests, and old dashboard tests.

## Surprises & Discoveries

- Observation: Duckalog supports two import shapes.
  Evidence: `Config.imports` is `Union[list[Union[str, ImportEntry]], SelectiveImports]`.

- Observation: Selective imports are section-specific.
  Evidence: `SelectiveImports` has optional lists for `duckdb`, `views`, `attachments`, `iceberg_catalogs`, and `semantic_models`.

- Observation: Loader settings are small but affect config loading performance.
  Evidence: `LoaderSettings` has `concurrency_enabled: bool = True` and `max_threads: Optional[int] = Field(default=None, ge=1)`.

- Observation: `env_files` defaults to `[".env"]`.
  Evidence: `Config.env_files` uses a default factory returning `[".env"]`.

## Decision Log

- Decision: Combine imports, env files, and loader settings in one plan.
  Rationale: They are all top-level config-loading controls and benefit from a single “Loading” settings area.
  Date/Author: 2026-04-30 / planning session

- Decision: Support both simple imports and selective imports, but require an explicit mode switch.
  Rationale: The two shapes are different. An explicit mode makes serialization predictable and prevents accidental conversion.
  Date/Author: 2026-04-30 / planning session

- Decision: Do not resolve or fetch imports in the form helper itself.
  Rationale: The editor modifies raw config text. Validation and reload verification already exercise the loader path; diagnostics and import graph exploration belong to a separate read-only feature.
  Date/Author: 2026-04-30 / planning session

- Decision: Do not edit imported files in this plan.
  Rationale: Editing transitive files requires a multi-file safety model and separate backups. This plan edits only the active config file.
  Date/Author: 2026-04-30 / planning session

## Outcomes & Retrospective

No implementation outcomes have been produced yet. At completion, update this section with exact helper names, routes, supported import shapes, validation coverage, and test results.

## Context and Orientation

Duckalog configs can be composed from multiple files. A config may use a simple import list, where each entry is either a path string or an object with `path` and `override`. It may also use selective imports, where separate lists are provided for sections such as `views`, `attachments`, `iceberg_catalogs`, and `semantic_models`. Configs also specify `env_files`, which are patterns for environment files loaded during config resolution, and `loader_settings`, which control import-loading concurrency.

Earlier Catalog Studio editors established the write-safety pattern. This editor must parse raw YAML/JSON, mutate only the targeted top-level keys, serialize proposed text, validate the full config, preview a diff, and save only through `save_config_text_safely()`. Do not serialize a loaded `Config` object.

## Plan of Work

Begin by verifying prerequisites. The editing safety service and prior structured editors must exist and pass tests.

Add `src/duckalog/studio/loading_settings_editing.py`. It should expose helpers equivalent to:

    build_proposed_imports_text(draft, values) -> str
    build_proposed_env_files_text(draft, values) -> str
    build_proposed_loader_settings_text(draft, values) -> str
    build_proposed_loading_settings_text(draft, values) -> str
    normalize_import_entry(values) -> str | dict
    normalize_selective_imports(values) -> dict

The combined helper should update `imports`, `env_files`, and `loader_settings` together for a single settings page save. Smaller helpers should be available for focused tests and route actions.

Implement import mode normalization. In `simple` mode, serialize `imports` as a list of strings and/or `{path, override}` objects. Preserve string entries when `override` is the default and no extra metadata is needed. In `selective` mode, serialize `imports` as an object with keys for supported sections. Empty section lists may be omitted to keep the config compact. If all sections are empty, serialize `imports: []` or omit `imports` according to prior editor conventions.

Implement env files editing. The UI should show a repeatable list of file patterns. Empty entries are ignored. Preserve order. Warn that later env files override earlier ones if that is documented by the loader. Do not require files to exist, because patterns and deployment-specific files are valid.

Implement loader settings editing. Provide a checkbox for `concurrency_enabled` and a numeric field for `max_threads`. Empty `max_threads` means null/omitted. Reject values less than 1 through validation.

Add StarHTML components. Add a “Loading” or “Config Loading” page under catalog settings with three sections: imports, env files, and loader settings. Include a mode toggle for simple versus selective imports. Include a preview panel and validation summary consistent with previous editors. For selective imports, provide per-section lists for `duckdb`, `views`, `attachments`, `iceberg_catalogs`, and `semantic_models`.

Add routes. Recommended routes are `GET /catalog/forms/loading`, `POST /catalog/forms/loading/validate`, `POST /catalog/forms/loading/preview`, and `POST /catalog/forms/loading/save`. If previous editors use a different grouped settings route convention, follow it and update tests.

Every POST route should generate proposed text using the helper module, validate using `validate_config_text()`, preview using `preview_config_diff()`, and save using `save_config_text_safely()`. Validate and preview must not write.

Add tests. Required helper tests include simple imports as strings, simple imports as objects with override false, switching to selective imports, omitting empty selective sections, env file order preservation, empty env file filtering, loader `max_threads` null/positive behavior, validation rejection for `max_threads: 0`, save backup creation, and preservation of unrelated sections such as views with `sql_file`. Route tests should prove the page renders and validate/preview/save use the safety service.

Also run existing config import tests. This editor touches the same top-level shape those tests cover.

## Concrete Steps

Verify prerequisites:

    uv run pytest tests/test_studio_editing.py tests/test_studio_form_editor.py tests/test_studio_view_lifecycle.py tests/test_studio_attachments_secrets_editor.py tests/test_studio_semantic_model_editor.py tests/test_studio_iceberg_catalog_editor.py -q

Inspect import and loader models:

    rg -n "class ImportEntry|class SelectiveImports|class LoaderSettings|env_files|loader_settings|_normalize_imports" src/duckalog/config/models.py src/duckalog/config/resolution tests/test_config_imports.py

After helpers exist, smoke-test them:

    uv run python - <<'PY'
    from pathlib import Path
    from duckalog.studio.editing import load_editable_config, validate_config_text
    from duckalog.studio.loading_settings_editing import build_proposed_loading_settings_text

    path = Path('/tmp/duckalog-loading-editor.yaml')
    path.write_text('''version: 1
    duckdb:
      database: ":memory:"
    views:
      - name: demo
        sql_file:
          path: demo.sql
    ''')
    draft = load_editable_config(path)
    proposed = build_proposed_loading_settings_text(draft, {
        'imports_mode': 'selective',
        'imports': {'views': [{'path': 'views.yaml', 'override': True}], 'semantic_models': ['semantic.yaml']},
        'env_files': ['.env', '.env.local'],
        'loader_settings': {'concurrency_enabled': True, 'max_threads': 4},
    })
    assert validate_config_text(proposed, draft.format, base_path=path).ok
    assert 'sql_file:' in proposed
    assert 'loader_settings:' in proposed
    print('loading settings helper ok')
    PY

Run StarHTML checks:

    starhtml-check src/duckalog/studio/app.py
    starhtml-check src/duckalog/studio/components.py
    starhtml-check src/duckalog/studio/loading_settings_components.py

Run focused tests:

    uv run pytest tests/test_studio_loading_settings_editor.py -q

Run broader validation:

    uv run pytest tests/test_studio_*.py tests/test_config_imports.py tests/test_config.py tests/test_dashboard.py -q

## Validation and Acceptance

A user can open the loading settings page, edit simple imports or selective imports, edit env file patterns, edit loader settings, preview the diff, validate the result, and save safely. Invalid loader settings or malformed import entries show errors and do not write. Save creates a backup and reload-verifies the config.

Automated tests must cover helper behavior, route rendering, validation/preview no-write behavior, safe save behavior, config import regression tests, and old dashboard preservation. `starhtml-check` must pass on changed Studio UI files.

## Idempotence and Recovery

GET routes and validate/preview POST routes never write. Save routes use the editing safety service. The editor changes only the active config file, not imported files or env files.

If implementation must be backed out, remove loading settings helper/component/routes/tests and navigation links. Keep prior Studio editors intact.

## Artifacts and Notes

Relevant code references:

    src/duckalog/config/models.py:ImportEntry
    src/duckalog/config/models.py:SelectiveImports
    src/duckalog/config/models.py:LoaderSettings
    src/duckalog/config/models.py:Config.imports
    src/duckalog/config/models.py:Config.env_files
    src/duckalog/config/resolution/imports.py
    tests/test_config_imports.py
    docs/examples/config-imports.md

Future work can add a read-only import graph/diagnostics page similar to `duckalog show-imports`. That is out of scope here.

## Revision Note

2026-04-30: Initial Catalog Studio Imports, Env Files, and Loader Settings Editor ExecPlan created.
