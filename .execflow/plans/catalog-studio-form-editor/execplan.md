# Add the Catalog Studio Structured Form Editor

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document must be maintained in accordance with `.execflow/PLANS.md` from the repository root. It builds on the completed umbrella brainstorm at `.execflow/plans/rebuild-duckalog-ui-starhtml/brainstorm.md` and on these prerequisite ExecPlans: `.execflow/plans/starhtml-catalog-studio-foundation/execplan.md`, `.execflow/plans/catalog-studio-explorer/execplan.md`, `.execflow/plans/catalog-studio-query-workbench/execplan.md`, `.execflow/plans/catalog-studio-editing-safety/execplan.md`, and `.execflow/plans/catalog-studio-expert-editor/execplan.md`. If any prerequisite is not implemented yet, implement it first. This plan adds the first normal-user form/menu editing experience on top of the same editing safety service used by expert mode.

## Purpose / Big Picture

After this change, a user can edit common Duckalog catalog settings through structured forms instead of hand-editing YAML or JSON. The first structured editor focuses on existing views and DuckDB settings. A user can open a view form, change fields such as name, schema, description, tags, SQL/source definition, validate the proposed change, preview the diff, and save through the editing safety service. A user can also edit basic DuckDB settings through a form. Every save still goes through validation, diff preview, backup, atomic write, and reload verification.

This feature delivers the form/menu editing requested in the brainstorm while preserving the safety model established by Expert Editor. It is intentionally not a complete schema editor for every Duckalog feature. It creates a reusable pattern for later form editors for attachments, secrets, semantic models, imports, and Iceberg catalogs.

## Progress

- [x] (2026-04-30) Completed the umbrella brainstorm and selected structured form/menu editing plus expert YAML/JSON editing as part of the Catalog Studio vision.
- [x] (2026-04-30) Created prerequisite ExecPlans through Expert Editor.
- [x] (2026-04-30) Read the editing safety and expert editor plans, relevant `Config`, `DuckDBConfig`, `ViewConfig`, and `SQLFileReference` model fields, and StarHTML form/signal guidance.
- [x] (2026-04-30) Ran a scout pass and saved structured-form context at `.execflow/plans/catalog-studio-form-editor/context.md`.
- [ ] Confirm the editing safety service and Expert Editor are implemented and tested.
- [ ] Add helper functions that transform a structured view or DuckDB form submission into proposed raw YAML/JSON text without writing files.
- [ ] Add StarHTML components for view edit forms and DuckDB settings forms.
- [ ] Add routes for view form render, view validate, view preview, view save, DuckDB form render, DuckDB validate, DuckDB preview, and DuckDB save.
- [ ] Ensure all save paths call the editing safety service and never write files directly.
- [ ] Add tests for rendering existing values, validating edits, previewing diffs, saving through backups, preserving SQL-file references, stale-save protection, and old dashboard preservation.
- [ ] Run `starhtml-check`, Studio tests, editing safety tests, expert editor tests, and existing dashboard tests, then update this plan with results.

## Surprises & Discoveries

- Observation: The first form editor should not try to cover the entire config schema.
  Evidence: `src/duckalog/config/models.py` includes views, DuckDB settings, secrets, attachments, semantic models, Iceberg catalogs, imports, env files, and loader settings. Covering all of them at once would make this plan too broad and hard to validate.

- Observation: `ViewConfig` has a critical mutually exclusive SQL-source rule.
  Evidence: `ViewConfig._validate_definition()` requires at most one of `sql`, `sql_file`, and `sql_template`, while requiring either one SQL source or a data source. The form UI and form-to-config conversion must enforce or surface this rule clearly.

- Observation: A structured form will likely generate normalized YAML or JSON for the changed root config.
  Evidence: The editing safety plan preserves raw text when saving, but it deliberately does not provide comment-aware structured rewrites. A first form editor can generate proposed text from model data, preview the diff, and let users decide whether the normalization is acceptable.

- Observation: The same safety service is mandatory for both expert and form editing.
  Evidence: The expert editor plan saves raw user text through the editing safety service. This form editor must generate proposed raw text and then call that same validation, diff, and save path.

## Decision Log

- Decision: Implement structured editing for existing views and DuckDB settings first.
  Rationale: These are high-value, common, and bounded. They exercise text fields, lists, conditional view-source fields, and config-level validation without taking on secrets, attachments, imports, or semantic models.
  Date/Author: 2026-04-30 / planning session

- Decision: Defer adding new views and deleting views in this first form editor.
  Rationale: Editing existing entries is enough to prove the form-to-proposed-text pipeline. Add/delete flows require list ordering, naming collision UX, and stronger accidental-loss protections.
  Date/Author: 2026-04-30 / planning session

- Decision: Generate proposed raw text from the whole root config and pass it to the safety service.
  Rationale: The safety service owns validation, diff, backup, atomic save, and reload verification. The form editor should not write partial files or bypass root-config validation.
  Date/Author: 2026-04-30 / planning session

- Decision: Do not add a round-trip YAML dependency in this plan.
  Rationale: The editing safety and expert editor plans deliberately avoid new YAML round-trip dependencies. This plan should keep that constraint and make normalization visible through diff preview.
  Date/Author: 2026-04-30 / planning session

- Decision: Preserve `sql_file` and `sql_template` references when editing forms.
  Rationale: Normal `load_config()` can inline SQL files. The form editor must work from the raw-editing draft and proposed raw text so SQL file references are not accidentally converted to inline SQL.
  Date/Author: 2026-04-30 / planning session

## Outcomes & Retrospective

No implementation outcomes have been produced yet. At completion, update this section with the exact form routes, form fields supported, serialization behavior, tests run, and any user-facing normalization caveats found during implementation.

## Context and Orientation

Catalog Studio is the new StarHTML-based UI for Duckalog. Earlier plans add the app foundation, catalog explorer, SQL workbench, editing safety service, and expert YAML/JSON editor. The editing safety service is the write boundary. It loads raw text, validates proposed text, previews diffs, creates backups, writes atomically, and reloads the saved file. The Expert Editor passes user-written raw YAML/JSON text into that service. The Structured Form Editor should pass generated proposed YAML/JSON text into the same service.

Duckalog’s config schema lives in `src/duckalog/config/models.py`. This plan’s first form editor should cover `ViewConfig` and `DuckDBConfig`. `ViewConfig` represents a catalog view. Important fields are `name`, `db_schema`, `description`, `tags`, `source`, `uri`, `database`, `table`, `catalog`, `options`, `sql`, `sql_file`, and `sql_template`. `DuckDBConfig` represents database/session settings. Important fields are `database`, `install_extensions`, `load_extensions`, `pragmas`, and `settings`. Secrets exist under `duckdb.secrets`, but this plan should not build secret forms because secret fields have provider-specific safety concerns and should be handled later.

The form editor has a harder preservation problem than the expert editor. Expert mode saves the raw text the user edited. Form mode takes field values and must turn them into proposed raw config text. Without a round-trip YAML parser, comments and formatting around the edited area may be normalized. This is acceptable for the first form editor only because users will see a diff before saving and can use Expert Editor if they need exact manual control. The implementation must be honest in UI copy: “Structured edits may normalize formatting; review the diff before saving.”

StarHTML form fields should use snake_case signal names, content arguments before keyword arguments, and no f-strings in reactive attributes. Use signals for UI state such as `form_is_validating`, `form_is_previewing`, `form_is_saving`, `form_validation_ok`, and `form_has_preview`. Signals are not Python containers; server-side data should stay in normal Python values and be sent through validation/preview/save routes.

## Plan of Work

Begin by verifying prerequisites. The Studio package, editing safety service, Expert Editor, and their tests must exist and pass. If they do not, stop and implement the prerequisite plans first.

Add a form editing helper module under `src/duckalog/studio/`, such as `form_editing.py`. Keep this module mostly pure Python. It should not import StarHTML. It should expose functions that take the current editable draft plus form values and produce proposed raw text. Good helper names are `build_proposed_view_config_text()` and `build_proposed_duckdb_config_text()`, but exact names may follow local conventions.

The helper must start from the current raw editable config, parse it into a plain dictionary, modify only the targeted section, and serialize the proposed root config back to the same format as the original file. For YAML, use the existing `pyyaml` dependency with `yaml.safe_dump(..., sort_keys=False)` or the project’s established dump style if one exists. For JSON, use `json.dumps(..., indent=2)`. Do not call `load_config()` and serialize the resulting `Config` object because that can inline SQL files, resolve env vars, and normalize path references. After generating proposed text, call `validate_config_text()` from the editing safety service to ensure the output is a valid Duckalog config.

For view editing, implement a form-value normalization function. It should accept fields for `original_name`, `name`, `db_schema`, `description`, `tags`, `definition_kind`, `sql`, `sql_file_path`, `sql_template_path`, `sql_file_variables`, `source`, `uri`, `database`, `table`, `catalog`, and `options`. It should produce a dictionary matching `ViewConfig` fields. Empty optional strings should become absent or `None` according to the serialization convention chosen. Tags may be entered as comma-separated text in the first UI iteration and converted to a list of stripped non-empty strings. `options` and `sql_file_variables` may be edited as small JSON textareas so the form does not need a dynamic key/value editor yet.

The view form must enforce or surface the mutually exclusive definition rule. Use a `definition_kind` control with values such as `inline_sql`, `sql_file`, `sql_template`, and `source`. When `inline_sql` is selected, set only `sql`. When `sql_file` is selected, set only `sql_file`. When `sql_template` is selected, set only `sql_template`. When `source` is selected, set only the relevant source fields and no SQL source unless the implementation intentionally supports source plus transformation SQL; defer that mixed mode unless it is already clearly represented in the existing config.

For source-specific fields, keep the first form simple. For `parquet` and `delta`, require `uri`. For `iceberg`, support either `uri` or `catalog` plus `table`, but present clear helper text. For `duckdb`, `sqlite`, and `postgres`, require `database` and `table`. Let `Config.model_validate()` produce authoritative errors; the UI should display them clearly.

For DuckDB settings, implement form values for `database`, `install_extensions`, `load_extensions`, `pragmas`, and `settings`. Use newline-separated textareas for list fields in the first iteration. Convert non-empty lines to lists. Preserve `settings` as a string if the user entered one line, or as a list if multiple lines are entered, as long as validation accepts it.

Add StarHTML components for forms. Use a top-level `view_edit_form_page()` and `duckdb_settings_form_page()`. They should render current values, validation panel, diff panel, save panel, and clear “Validate”, “Preview diff”, and “Save changes” buttons. Save should be guarded by server-side validation and, if available from Expert Editor, stale checksum protection. The page should link to Expert Editor for users who want full raw control.

Add routes. Recommended routes are `GET /catalog/forms/view/{view_name}`, `POST /catalog/forms/view/validate`, `POST /catalog/forms/view/preview`, `POST /catalog/forms/view/save`, `GET /catalog/forms/duckdb`, `POST /catalog/forms/duckdb/validate`, `POST /catalog/forms/duckdb/preview`, and `POST /catalog/forms/duckdb/save`. If the existing Studio route style uses singular names or no trailing slash, follow that style and update tests accordingly.

Route handlers must be thin. They should parse StarHTML/Datastar request data, call the form-editing helper to generate proposed text, then call editing safety service functions for validation, diff preview, or save. They must not call `Path.write_text()`, `os.replace()`, or `shutil.copy2()` directly. They must not mutate the in-memory `Config` without producing proposed raw text and sending it through the safety service.

Update navigation and explorer pages. The view detail page from the Explorer plan should show an “Edit in form” link to `/catalog/forms/view/{view_name}`. The Studio config area should show “DuckDB settings” linking to `/catalog/forms/duckdb`. Keep Expert Editor accessible as the advanced fallback.

Add tests. Direct helper tests should cover converting form values into proposed YAML/JSON for a view and DuckDB settings. Route tests should cover render, validate, preview, and save flows. Tests should confirm that validation and preview do not write to disk, save creates a backup through the safety service, saved files reload, and invalid form submissions do not write. Include a `sql_file` preservation test: start with a config that has `sql_file: {path: query.sql}`, edit only the description through the form, save, and assert the saved text still contains `sql_file:` and does not replace it with inline `sql:`.

Run `starhtml-check` on changed StarHTML UI files. Run form editor tests, expert editor tests, editing safety tests, all Studio tests, and old dashboard tests.

## Concrete Steps

Work from the repository root `/Users/volker/coding/libs/duckalog`.

Verify prerequisites:

    uv run python - <<'PY'
    from duckalog.studio import create_app, StudioContext
    from duckalog.studio import editing
    print(create_app, StudioContext, editing)
    PY

Run prerequisite tests:

    uv run pytest tests/test_studio.py tests/test_studio_editing.py tests/test_studio_expert_editor.py -q

If explorer or query tests are split into separate files, include them:

    uv run pytest tests/test_studio.py tests/test_studio_explorer.py tests/test_studio_query.py tests/test_studio_editing.py tests/test_studio_expert_editor.py -q

Inspect the implemented safety service and expert editor route conventions:

    rg -n "load_editable_config|validate_config_text|preview_config_diff|save_config_text_safely|config/expert|config_text|checksum" src/duckalog/studio tests

After adding form helpers, run a direct helper smoke test. Adjust function names to match the implementation:

    uv run python - <<'PY'
    from pathlib import Path
    from duckalog.studio.editing import load_editable_config, validate_config_text
    from duckalog.studio.form_editing import build_proposed_view_config_text

    path = Path('/tmp/duckalog-form-editor.yaml')
    path.write_text('''version: 1
    duckdb:
      database: ":memory:"
    views:
      - name: demo
        sql_file:
          path: query.sql
        description: "old"
    ''')
    draft = load_editable_config(path)
    proposed = build_proposed_view_config_text(
        draft,
        original_name='demo',
        values={'name': 'demo', 'description': 'new', 'definition_kind': 'sql_file', 'sql_file_path': 'query.sql'},
    )
    assert 'description: new' in proposed or 'description: "new"' in proposed
    assert 'sql_file:' in proposed
    assert 'sql:' not in proposed.replace('sql_file:', '')
    validation = validate_config_text(proposed, draft.format, base_path=path)
    assert validation.ok, validation.errors
    print('form helper ok')
    PY

Run StarHTML checks after adding UI components:

    starhtml-check src/duckalog/studio/app.py
    starhtml-check src/duckalog/studio/components.py

If form components live in a new file, check it too:

    starhtml-check src/duckalog/studio/form_components.py

Run focused tests:

    uv run pytest tests/test_studio_form_editor.py -q

Run all Studio tests:

    uv run pytest tests/test_studio.py tests/test_studio_editing.py tests/test_studio_expert_editor.py tests/test_studio_form_editor.py -q

If tests are split by feature, include all Studio test files:

    uv run pytest tests/test_studio.py tests/test_studio_explorer.py tests/test_studio_query.py tests/test_studio_editing.py tests/test_studio_expert_editor.py tests/test_studio_form_editor.py -q

Run old dashboard tests:

    uv run pytest tests/test_dashboard.py -q

Manual smoke test:

    cat >/tmp/duckalog-form-editor.yaml <<'YAML'
    version: 1
    duckdb:
      database: ":memory:"
    views:
      - name: demo
        sql: "select 1 as id"
        description: "Before edit"
        tags: [demo]
    YAML

Start Studio:

    uv run duckalog studio /tmp/duckalog-form-editor.yaml --port 8788

Verify pages exist:

    curl -s http://127.0.0.1:8788/catalog/forms/view/demo | rg "Edit View|demo|Before edit|Validate|Preview diff|Save changes"
    curl -s http://127.0.0.1:8788/catalog/forms/duckdb | rg "DuckDB Settings|database|Validate|Preview diff|Save changes"

Endpoint curl commands depend on the implemented StarHTML request format. During implementation, add the working validate, preview, and save curl examples to this plan.

## Validation and Acceptance

Acceptance is user-visible. From a running Catalog Studio session, a user can open a view’s structured edit form from the view detail page. The form is pre-populated with current values. The user can change description, tags, schema, and view definition fields, validate the proposed edit, preview a diff, and save through the editing safety service. A successful save creates a backup and reloads valid config. Invalid edits display validation errors and do not write files. A user can similarly open DuckDB settings, edit basic settings, validate, preview, and save.

Automated tests must prove that form helpers produce valid proposed raw text, validation and preview are read-only, save creates backups and reloads, invalid saves are blocked, and `sql_file` references are preserved when editing unrelated fields. Tests must also prove route handlers do not bypass the editing safety service. Existing Expert Editor and editing safety tests must still pass, and old dashboard tests must still pass.

StarHTML validation requires `starhtml-check` on every changed Studio UI file with no ERROR findings.

## Idempotence and Recovery

GET routes and validate/preview POST routes must not write files. Save routes are safe to repeat because each save goes through the editing safety service and creates a backup. If stale-save protection exists from Expert Editor, use it here too and reject saves when the file changed on disk after the form loaded.

If form serialization normalizes YAML more than expected, keep the behavior only if the diff preview makes it explicit. Do not hide large rewrites from the user. If the initial form helper would rewrite too much of the file for small changes, stop and revise the plan before shipping broad form saves.

If implementation must be backed out, remove the form editor helpers, routes, components, navigation links, and tests. Keep the editing safety service and Expert Editor intact.

## Artifacts and Notes

The umbrella brainstorm is:

    .execflow/plans/rebuild-duckalog-ui-starhtml/brainstorm.md

Prerequisite ExecPlans are:

    .execflow/plans/starhtml-catalog-studio-foundation/execplan.md
    .execflow/plans/catalog-studio-explorer/execplan.md
    .execflow/plans/catalog-studio-query-workbench/execplan.md
    .execflow/plans/catalog-studio-editing-safety/execplan.md
    .execflow/plans/catalog-studio-expert-editor/execplan.md

The scout context for this plan is:

    .execflow/plans/catalog-studio-form-editor/context.md

Relevant code references are:

    src/duckalog/config/models.py:Config
    src/duckalog/config/models.py:DuckDBConfig
    src/duckalog/config/models.py:ViewConfig
    src/duckalog/config/models.py:SQLFileReference
    src/duckalog/studio/editing.py

A first form editor should support only existing view edits and DuckDB settings. Future ExecPlans can add create/delete view flows, attachments, secrets, semantic models, imports, Iceberg catalogs, and richer key/value editors for options.

## Interfaces and Dependencies

At the end of this plan, the Studio app should expose routes equivalent to:

    GET /catalog/forms/view/{view_name}
    POST /catalog/forms/view/validate
    POST /catalog/forms/view/preview
    POST /catalog/forms/view/save
    GET /catalog/forms/duckdb
    POST /catalog/forms/duckdb/validate
    POST /catalog/forms/duckdb/preview
    POST /catalog/forms/duckdb/save

The form editor helper module should expose operations equivalent to:

    build_proposed_view_config_text(draft, original_name, values) -> str
    build_proposed_duckdb_config_text(draft, values) -> str

The implementation should use existing dependencies only: StarHTML from foundation, PyYAML, Pydantic, and the standard library. Do not add a round-trip YAML library or browser form framework in this plan. Do not write files directly from routes or helpers; saving must go through the editing safety service.

The next ExecPlan should likely cover create/delete view flows or a dedicated attachments/secrets form editor, depending on which user workflows matter most after existing-view and DuckDB setting edits work.

## Revision Note

2026-04-30: Initial Catalog Studio Structured Form Editor ExecPlan created. It scopes form editing to existing views and DuckDB settings, uses the safety service for all writes, and deliberately defers add/delete flows and advanced config sections.
